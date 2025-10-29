"""Training loop for the semantic encoder distilling LLM labels."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import torch
import torch.nn as nn
from loguru import logger
from torch.utils.data import DataLoader

from autoppia_rm.datasets.loaders import SemanticDataset
from autoppia_rm.models.semantic_encoder import SemanticEncoder
from autoppia_rm.utils import config_path as get_config_path


@dataclasses.dataclass(slots=True)
class SemanticConfig:
    in_dim: int = 768
    affordance_dim: int = 16
    batch: int = 64
    lr: float = 1e-4
    epochs: int = 5
    num_workers: int = 4
    val_every: int = 1
    ckpt_path: Path = Path("data/rm/ckpts/semantic_encoder.pt")


def load_config(path: str | Path | None) -> SemanticConfig:
    if path is None:
        path = get_config_path("semantic_encoder.yaml")
    import yaml

    path = Path(path)
    data = yaml.safe_load(path.read_text())
    return SemanticConfig(**data)


def train(cfg: SemanticConfig) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SemanticEncoder(cfg.in_dim, affordance_dim=cfg.affordance_dim).to(device)

    ds_train = SemanticDataset(split="train")
    ds_val = SemanticDataset(split="val")
    loader_train = DataLoader(ds_train, batch_size=cfg.batch, shuffle=True, num_workers=cfg.num_workers)
    loader_val = DataLoader(ds_val, batch_size=cfg.batch, shuffle=False, num_workers=cfg.num_workers)

    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=1e-4)
    loss_page = nn.CrossEntropyLoss()
    loss_prog = nn.MSELoss()
    loss_aff = nn.BCEWithLogitsLoss()

    best_val = float("inf")
    for epoch in range(1, cfg.epochs + 1):
        model.train()
        total_loss = 0.0
        for batch in loader_train:
            x = batch["x"].to(device)
            y_page = batch["y_page"].to(device)
            y_prog = batch["y_prog"].to(device)
            y_aff = batch["y_aff"].to(device)

            out = model(x)
            loss = (
                loss_page(out["page_logits"], y_page)
                + loss_prog(out["goal_progress"].squeeze(-1), y_prog)
                + loss_aff(out["affordances"], y_aff)
            )
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * x.size(0)

        logger.info(f"Epoch {epoch}: train_loss={total_loss / len(ds_train):.4f}")

        if epoch % cfg.val_every == 0:
            model.eval()
            with torch.no_grad():
                val_loss = 0.0
                for batch in loader_val:
                    x = batch["x"].to(device)
                    y_page = batch["y_page"].to(device)
                    y_prog = batch["y_prog"].to(device)
                    y_aff = batch["y_aff"].to(device)
                    out = model(x)
                    loss = (
                        loss_page(out["page_logits"], y_page)
                        + loss_prog(out["goal_progress"].squeeze(-1), y_prog)
                        + loss_aff(out["affordances"], y_aff)
                    )
                    val_loss += loss.item() * x.size(0)
                val_loss /= len(ds_val)
            logger.info(f"Epoch {epoch}: val_loss={val_loss:.4f}")
            if val_loss < best_val:
                best_val = val_loss
                cfg.ckpt_path.parent.mkdir(parents=True, exist_ok=True)
                torch.save(model.state_dict(), cfg.ckpt_path)
                logger.info(f"Saved best semantic encoder to {cfg.ckpt_path}")


def main(config_path: str | Path | None = None) -> None:
    cfg = load_config(config_path)
    train(cfg)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train semantic encoder")
    parser.add_argument(
        "--config",
        type=Path,
        default=get_config_path("semantic_encoder.yaml"),
        help="Path to YAML config",
    )
    args = parser.parse_args()
    main(args.config)
