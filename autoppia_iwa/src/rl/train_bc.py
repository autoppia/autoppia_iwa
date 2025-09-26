"""
Train a Behavior Cloning policy from rollouts JSONL (collected from your heuristic agent).
Saves: bc_policy.pt (weights) and bc_vocab.json (action strings).
"""

import json
from pathlib import Path
from typing import Any

import torch

from autoppia_iwa.src.rl.policies.bc import ActionVocab, BCPolicy

# ====== USER AREA ======
DATA_JSONL = "heuristic_rollouts.jsonl"
OUT_WEIGHTS = "bc_policy.pt"
OUT_VOCAB = "bc_vocab.json"
EPOCHS = 10
# =======================


def load_dataset(path: str) -> dict[str, list[dict[str, Any]]]:
    obs_list: list[dict[str, Any]] = []
    act_list: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            prompt = rec.get("prompt", "")
            for tr in rec.get("transitions", []):
                obs_list.append(
                    {
                        "url": tr["obs"]["url"],
                        "task_prompt": prompt,
                        "step": tr["obs"]["step"],
                    }
                )
                act_list.append(tr["action"])
    return {"obs": obs_list, "acts": act_list}


def main():
    data = load_dataset(DATA_JSONL)
    if not data["obs"]:
        print("Empty dataset.")
        return

    vocab = ActionVocab(data["acts"])
    policy = BCPolicy(vocab=vocab, lr=3e-3, device="cpu")
    stats = policy.fit(data["obs"], data["acts"], epochs=EPOCHS, batch_size=64)
    print("BC training done:", stats)

    torch.save(policy.state_dict(), OUT_WEIGHTS)
    Path(OUT_VOCAB).write_text(json.dumps(vocab._itos, ensure_ascii=False, indent=2))
    print(f"Saved: {OUT_WEIGHTS}, {OUT_VOCAB}")


if __name__ == "__main__":
    main()
