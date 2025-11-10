from __future__ import annotations

import dataclasses
from typing import Any, Dict, Iterable, List, Optional, Tuple, TypeVar

import numpy as np
import torch
from loguru import logger
from torch.utils.data import DataLoader, Dataset, random_split

from .interfaces import ObservationSpec, StepRecord, Trajectory, TrajectoryProvider

Batch = Dict[str, Any]
T_co = TypeVar("T_co", covariant=True)


def _infer_spec(step: StepRecord) -> ObservationSpec:
    """Infer observation and action dimensions from a sample step."""

    return ObservationSpec(
        goal_ids=tuple(int(x) for x in step.goal_ids.shape),
        dom_ids=tuple(int(x) for x in step.dom_ids.shape),
        url_id=tuple(int(x) for x in step.url_id.shape),
        prev_actions=tuple(int(x) for x in step.prev_actions.shape),
        topk_text_ids=tuple(int(x) for x in step.topk_text_ids.shape),
        topk_meta=tuple(int(x) for x in step.topk_meta.shape),
        score=tuple(int(x) for x in (step.score.shape if step.score is not None else (1,))),
        action_dim=int(step.action_mask.shape[0]),
    )


class TrajectoryDataset(Dataset[T_co]):
    """Flattened dataset of StepRecords suitable for behavior cloning."""

    def __init__(self, trajectories: Iterable[Trajectory], *, max_steps: Optional[int] = None):
        self._steps: List[StepRecord] = []
        self._gather_steps(trajectories, max_steps=max_steps)
        if not self._steps:
            raise ValueError("TrajectoryDataset received no steps to train on.")
        self.spec = _infer_spec(self._steps[0])

    def _gather_steps(self, trajectories: Iterable[Trajectory], *, max_steps: Optional[int]) -> None:
        count = 0
        for traj in trajectories:
            for step in traj.steps:
                self._steps.append(step)
                count += 1
                if max_steps is not None and count >= max_steps:
                    logger.debug("TrajectoryDataset: truncated to %d steps", count)
                    return

    def __len__(self) -> int:
        return len(self._steps)

    def __getitem__(self, index: int) -> Batch:
        step = self._steps[index]
        score_arr = step.score
        if score_arr is None:
            score_arr = np.zeros(self.spec.score, dtype=np.float32)

        obs = {
            "goal_ids": torch.as_tensor(step.goal_ids, dtype=torch.float32),
            "dom_ids": torch.as_tensor(step.dom_ids, dtype=torch.float32),
            "url_id": torch.as_tensor(step.url_id, dtype=torch.float32),
            "prev_actions": torch.as_tensor(step.prev_actions, dtype=torch.float32),
            "topk_text_ids": torch.as_tensor(step.topk_text_ids, dtype=torch.float32),
            "topk_meta": torch.as_tensor(step.topk_meta, dtype=torch.float32),
            "score": torch.as_tensor(score_arr, dtype=torch.float32),
        }
        action_mask = torch.as_tensor(step.action_mask, dtype=torch.bool)
        action = torch.tensor(int(step.action_index), dtype=torch.long)
        return {"obs": obs, "action_mask": action_mask, "action": action}


@dataclasses.dataclass(slots=True)
class BehaviorCloningConfig:
    batch_size: int = 128
    epochs: int = 5
    learning_rate: float = 3e-4
    grad_clip: float = 0.5
    validation_split: float = 0.1
    max_trajectories: Optional[int] = None
    max_steps: Optional[int] = None
    shuffle: bool = True
    seed: int = 1337
    num_workers: int = 0
    log_interval: int = 20
    device: Optional[str] = None


class BehaviorCloningTrainer:
    """Simple supervised trainer that mirrors the MaskablePPO policy head."""

    def __init__(self, policy: Any, cfg: BehaviorCloningConfig):
        self.policy = policy
        self.cfg = cfg
        default_device = getattr(policy, "device", None)
        if isinstance(default_device, torch.device):
            device_str = str(default_device)
        else:
            device_str = default_device
        self.device = torch.device(cfg.device or device_str or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.policy.to(self.device)
        torch.manual_seed(cfg.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(cfg.seed)
        self.spec: ObservationSpec | None = None

    def _prepare_dataset(self, provider: TrajectoryProvider) -> TrajectoryDataset:
        trajectories = list(provider.fetch(self.cfg.max_trajectories))
        if not trajectories:
            raise RuntimeError("Behavior cloning provider returned no trajectories.")
        dataset = TrajectoryDataset(trajectories, max_steps=self.cfg.max_steps)
        self.spec = dataset.spec
        logger.info(
            "Loaded %d trajectories (%d steps) for BC training (action_dim=%d).",
            len(trajectories),
            len(dataset),
            dataset.spec.action_dim,
        )
        return dataset

    def _make_dataloaders(self, dataset: TrajectoryDataset) -> tuple[DataLoader, Optional[DataLoader]]:
        val_size = int(len(dataset) * max(0.0, min(1.0, self.cfg.validation_split)))
        if val_size > 0 and len(dataset) - val_size < 1:
            val_size = 0

        if val_size > 0:
            generator = torch.Generator().manual_seed(self.cfg.seed)
            train_dataset, val_dataset = random_split(dataset, [len(dataset) - val_size, val_size], generator=generator)
        else:
            train_dataset, val_dataset = dataset, None

        train_loader = DataLoader(
            train_dataset,
            batch_size=self.cfg.batch_size,
            shuffle=self.cfg.shuffle,
            num_workers=self.cfg.num_workers,
        )
        val_loader = (
            DataLoader(
                val_dataset,
                batch_size=self.cfg.batch_size,
                shuffle=False,
                num_workers=self.cfg.num_workers,
            )
            if val_dataset is not None
            else None
        )
        return train_loader, val_loader

    def _forward(self, batch: Batch) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        obs = {key: tensor.to(self.device) for key, tensor in batch["obs"].items()}
        mask = batch["action_mask"].to(self.device)
        actions = batch["action"].to(self.device)
        distribution = self.policy.get_distribution(obs, action_masks=mask)
        log_prob = distribution.log_prob(actions)
        if hasattr(distribution.distribution, "probs"):
            probs = distribution.distribution.probs
        else:
            logits = distribution.distribution.logits
            probs = torch.softmax(logits, dim=-1)
        preds = probs.argmax(dim=-1)
        return log_prob, preds, actions

    def fit(self, provider: TrajectoryProvider) -> dict[str, float]:
        dataset = self._prepare_dataset(provider)
        train_loader, val_loader = self._make_dataloaders(dataset)
        optimizer = torch.optim.Adam(self.policy.parameters(), lr=self.cfg.learning_rate)

        self.policy.set_training_mode(True)
        history: dict[str, float] = {
            "train_loss": 0.0,
            "train_acc": 0.0,
            "val_loss": float("nan"),
            "val_acc": float("nan"),
            "num_steps": float(len(dataset)),
            "epochs": float(self.cfg.epochs),
        }

        for epoch in range(1, self.cfg.epochs + 1):
            self.policy.train()
            total_loss = 0.0
            total_correct = 0
            total_samples = 0

            for step_idx, batch in enumerate(train_loader, start=1):
                log_prob, preds, actions = self._forward(batch)
                loss = -log_prob.mean()

                optimizer.zero_grad()
                loss.backward()
                if self.cfg.grad_clip is not None and self.cfg.grad_clip > 0:
                    torch.nn.utils.clip_grad_norm_(self.policy.parameters(), self.cfg.grad_clip)
                optimizer.step()

                total_loss += loss.item() * actions.size(0)
                total_correct += (preds == actions).sum().item()
                total_samples += actions.size(0)

                if self.cfg.log_interval and step_idx % self.cfg.log_interval == 0:
                    avg_loss = total_loss / max(1, total_samples)
                    avg_acc = total_correct / max(1, total_samples)
                    logger.debug(
                        "BC epoch %d step %d: loss=%.4f acc=%.4f",
                        epoch,
                        step_idx,
                        avg_loss,
                        avg_acc,
                    )

            train_loss = total_loss / max(1, total_samples)
            train_acc = total_correct / max(1, total_samples)
            history["train_loss"] = train_loss
            history["train_acc"] = train_acc
            logger.info("BC epoch %d summary: loss=%.4f acc=%.4f", epoch, train_loss, train_acc)

            if val_loader is not None:
                self.policy.eval()
                with torch.no_grad():
                    val_loss = 0.0
                    val_correct = 0
                    val_samples = 0
                    for batch in val_loader:
                        log_prob, preds, actions = self._forward(batch)
                        loss = -log_prob.mean()
                        val_loss += loss.item() * actions.size(0)
                        val_correct += (preds == actions).sum().item()
                        val_samples += actions.size(0)

                if val_samples > 0:
                    history["val_loss"] = val_loss / val_samples
                    history["val_acc"] = val_correct / val_samples
                    logger.info(
                        "BC epoch %d validation: loss=%.4f acc=%.4f",
                        epoch,
                        history["val_loss"],
                        history["val_acc"],
                    )

        self.policy.set_training_mode(False)
        return history
