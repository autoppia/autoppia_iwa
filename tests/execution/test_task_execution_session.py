from autoppia_iwa.src.evaluation.stateful_evaluator import TaskExecutionSession as StatefulTaskExecutionSession
from autoppia_iwa.src.execution.task_execution_session import TaskExecutionSession


def test_task_execution_session_reexports_stateful_session() -> None:
    assert TaskExecutionSession is StatefulTaskExecutionSession
