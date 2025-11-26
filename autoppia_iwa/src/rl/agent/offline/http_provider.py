from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
import requests

from .interfaces import StepRecord, Trajectory, TrajectoryProvider


@dataclass
class HttpTrajectoryProvider(TrajectoryProvider):
    """
    Lightweight client for pulling trajectories from an external service.

    The service is expected to expose an endpoint such as:
        GET /trajectories?limit=K

    Response schema (per trajectory):
        {
            "steps": [
                {
                    "goal_ids": [...],
                    "dom_ids": [...],
                    "url_id": [...],
                    "prev_actions": [...],
                    "topk_text_ids": [...],
                    "topk_meta": [...],
                    "action_mask": [...],
                    "action_index": <int>
                },
                ...
            ]
        }

    All arrays must already be numeric (ints/floats) and match the shapes used by
    IWAWebEnv observations.
    """

    base_url: str
    timeout: float = 30.0

    def fetch(self, limit: int | None = None) -> Iterable[Trajectory]:
        params = {"limit": limit} if limit is not None else None
        response = requests.get(
            f"{self.base_url.rstrip('/')}/trajectories",
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        trajectories = payload.get("trajectories", []) if isinstance(payload, dict) else payload

        for traj_raw in trajectories:
            steps_raw = traj_raw.get("steps", [])
            steps: list[StepRecord] = []
            for step in steps_raw:
                steps.append(
                    StepRecord(
                        goal_ids=np.asarray(step["goal_ids"], dtype=np.int32),
                        dom_ids=np.asarray(step["dom_ids"], dtype=np.int32),
                        url_id=np.asarray(step["url_id"], dtype=np.int32),
                        prev_actions=np.asarray(step["prev_actions"], dtype=np.int32),
                        topk_text_ids=np.asarray(step["topk_text_ids"], dtype=np.int32),
                        topk_meta=np.asarray(step["topk_meta"], dtype=np.float32),
                        action_mask=np.asarray(step["action_mask"], dtype=bool),
                        action_index=int(step["action_index"]),
                        score=np.asarray(step.get("score"), dtype=np.float32) if "score" in step else None,
                    )
                )
            if steps:
                yield Trajectory(steps=steps)


def dump_trajectory(traj: Trajectory) -> str:
    """Utility helper used in debugging/tests to view provider output."""

    steps_dump = []
    for step in traj.steps:
        steps_dump.append(
            {
                "goal_ids": step.goal_ids.tolist(),
                "dom_ids": step.dom_ids.tolist(),
                "url_id": step.url_id.tolist(),
                "prev_actions": step.prev_actions.tolist(),
                "topk_text_ids": step.topk_text_ids.tolist(),
                "topk_meta": step.topk_meta.tolist(),
                "action_mask": step.action_mask.tolist(),
                "action_index": int(step.action_index),
                "score": step.score.tolist() if step.score is not None else None,
            }
        )
    return json.dumps({"steps": steps_dump}, ensure_ascii=False, indent=2)
