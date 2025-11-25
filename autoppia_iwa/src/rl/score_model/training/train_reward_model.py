"""Training loop for the reward model using preference pairs and success labels."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from loguru import logger
from torch.utils.data import DataLoader

from ..datasets.loaders import PrefPairDataset, RewardDataset
from ..models.reward_model import RewardModel
from .losses import alignment_loss, preference_loss
from ..utils import config_path as get_config_path


@dataclasses.dataclass(slots=True)
class RewardConfig:
    in_dim: int = 768
    batch: int = 64
    lr: float = 1e-4
    epochs: int = 5
    lambda_succ: float = 0.5
    lambda_align: float = 0.1
    lambda_score: float = 1.0
    num_workers: int = 4
    pref_pairs_per_epoch: int = 10_000
    reward_samples_per_epoch: int = 2_000
    ckpt_path: Path = Path("data/rm/ckpts/reward_model.pt")


def load_config(path: str | Path | None) -> RewardConfig:
    if path is None:
        path = get_config_path("rm_train.yaml")
    import yaml

    path = Path(path)
    data = yaml.safe_load(path.read_text())
    return RewardConfig(**data)


def train(cfg: RewardConfig) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = RewardModel(cfg.in_dim).to(device)

    dataset_pairs = PrefPairDataset(limit=cfg.pref_pairs_per_epoch)
    loader_pairs = DataLoader(dataset_pairs, batch_size=cfg.batch, shuffle=True, num_workers=cfg.num_workers) if len(dataset_pairs) > 0 else None

    dataset_reward = RewardDataset(cfg, split="train")
    loader_reward = DataLoader(dataset_reward, batch_size=cfg.batch, shuffle=True, num_workers=cfg.num_workers)

    dataset_reward_val = RewardDataset(cfg, split="val")
    loader_reward_val = DataLoader(dataset_reward_val, batch_size=cfg.batch, shuffle=False, num_workers=cfg.num_workers)

    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=1e-4)
    loss_success = nn.BCELoss()

    for epoch in range(1, cfg.epochs + 1):
        model.train()
        total_pref = 0.0
        total_succ = 0.0
        total_align = 0.0
        total_score = 0.0

        reward_iter = iter(loader_reward)
        for batch in (loader_pairs if loader_pairs else []):
            x_pos = batch["x_pos"].to(device)
            x_neg = batch["x_neg"].to(device)
            out_pos = model(x_pos)
            out_neg = model(x_neg)
            pref = preference_loss(out_pos["R"], out_neg["R"])
            total_pref += pref.item()

            try:
                reward_batch = next(reward_iter)
            except StopIteration:
                reward_iter = iter(loader_reward)
                reward_batch = next(reward_iter)

            xr = reward_batch["x"].to(device)
            yr = reward_batch["y_success"].to(device)
            out_r = model(xr)
            succ = loss_success(out_r["p_success"], yr)
            align = alignment_loss(out_r["R"], out_r["p_success"])
            if "y_score" in reward_batch:
                ys = reward_batch["y_score"].to(device)
                score = F.mse_loss(out_r["score"], ys)
            else:
                score = torch.tensor(0.0, device=device)
            total_succ += succ.item()
            total_align += align.item()
            total_score += score.item()

            loss = pref + cfg.lambda_succ * succ + cfg.lambda_align * align + cfg.lambda_score * score
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        num_pairs = len(loader_pairs) if loader_pairs else 1
        logger.info(
            "Epoch {}: pref={:.4f} succ={:.4f} align={:.4f} score={:.4f}",
            epoch,
            total_pref / max(1, num_pairs),
            total_succ / max(1, num_pairs),
            total_align / max(1, num_pairs),
            total_score / max(1, num_pairs),
        )

        # Validation: track how often R_pos > R_neg and BCE on val set
        model.eval()
        with torch.no_grad():
            win = 0
            total = 0
            for batch in (loader_pairs if loader_pairs else []):
                x_pos = batch["x_pos"].to(device)
                x_neg = batch["x_neg"].to(device)
                out_pos = model(x_pos)
                out_neg = model(x_neg)
                win += torch.sum(out_pos["R"] > out_neg["R"]).item()
                total += x_pos.size(0)
            pref_win = win / max(1, total)

            val_loss = 0.0
            val_total = 0
            val_score_mse = 0.0
            val_score_total = 0
            for batch in loader_reward_val:
                xr = batch["x"].to(device)
                yr = batch["y_success"].to(device)
                out_r = model(xr)
                val_loss += loss_success(out_r["p_success"], yr).item() * xr.size(0)
                val_total += xr.size(0)
                if "y_score" in batch:
                    ys = batch["y_score"].to(device)
                    val_score_mse += F.mse_loss(out_r["score"], ys, reduction="sum").item()
                    val_score_total += xr.size(0)
            val_loss /= max(1, val_total)
            val_score_mse = val_score_mse / max(1, val_score_total)

        logger.info(
            "Epoch {}: pref_win={:.3f} val_bce={:.4f} val_score_mse={:.4f}",
            epoch,
            pref_win,
            val_loss,
            val_score_mse,
        )

        cfg.ckpt_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), cfg.ckpt_path)
        logger.info(f"Saved reward model checkpoint to {cfg.ckpt_path}")


def main(config_path: str | Path | None = None) -> None:
    cfg = load_config(config_path)
    train(cfg)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train reward model")
    parser.add_argument(
        "--config",
        type=Path,
        default=get_config_path("rm_train.yaml"),
        help="Path to YAML config",
    )
    args = parser.parse_args()
    main(args.config)
