from __future__ import annotations

import json

from autoppia_iwa.src.evaluation.benchmark.trace_writer import TraceWriter


def test_trace_writer_flush_and_episode_close(tmp_path):
    writer = TraceWriter(tmp_path / "traces", run_metadata={"project": "autocinema"})
    episode = writer.start_episode(
        episode_task_id="episode-1",
        task_id="task-1",
        use_case="FILM_DETAIL",
        task_data={"prompt": "Open a film"},
    )

    episode.record_step(
        0,
        before_url="http://localhost",
        before_html="<html>before</html>",
        after_url="http://localhost/detail",
        after_html="<html>after</html>",
        after_score=1.0,
        after_success=True,
        actions=[{"type": "ClickAction"}],
        reasoning="Open detail",
        done=True,
    )
    episode.close(success=True, score=1.0, total_steps=1, evaluation_time=1.2345, agent_name="Agent One")
    index_path = writer.flush()

    episode_payload = json.loads((tmp_path / "traces" / "episodes" / "episode-1.json").read_text())
    index_payload = json.loads(index_path.read_text())

    assert episode_payload["episode"]["evaluation_time"] == 1.2345
    assert episode_payload["steps"][0]["actions"] == [{"type": "ClickAction"}]
    assert index_payload["project"] == "autocinema"
    assert index_payload["episodes"][0]["file"] == "episodes/episode-1.json"
