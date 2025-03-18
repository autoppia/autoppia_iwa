from typing import Any

from pydantic import BaseModel, Field

from autoppia_iwa.src.execution.classes import ActionExecutionResult


class TestResult(BaseModel):
    """Represents the evaluation result of a single test."""

    success: bool  # True if the test passed, False otherwise
    extra_data: dict | None = None  # Additional data related to the test


class Feedback(BaseModel):
    task_prompt: str  # The description of the task being evaluated
    final_score: float  # Overall evaluation score (0-10)
    executed_actions: int  # Number of successfully executed actions
    failed_actions: int  # Number of failed actions
    passed_tests: int  # Number of tests that passed
    failed_tests: int  # Number of tests that failed
    total_execution_time: float  # Total time taken for execution
    time_penalty: float  # Penalty points for exceeding expected time
    critical_test_penalty: int  # Penalty points for failing critical tests
    test_results: list[TestResult]  # Detailed test results
    execution_history: list[ActionExecutionResult]  # Detailed execution logs

    def to_text(self) -> str:
        """Generates a human-readable textual summary."""
        feedback = f"Task: '{self.task_prompt}'\n"
        feedback += f"Final Score: {self.final_score}/10\n"
        feedback += f"Executed Actions: {self.executed_actions}, Failed Actions: {self.failed_actions}\n"
        feedback += f"Tests Passed: {self.passed_tests}, Tests Failed: {self.failed_tests}\n"
        feedback += f"Total Execution Time: {self.total_execution_time:.2f}s\n"
        feedback += f"Time Penalty: {self.time_penalty:.1f} points\n"
        feedback += f"Critical Test Penalty: {self.critical_test_penalty} points\n"
        feedback += "\nTest Results:\n"
        for test in self.test_results:
            feedback += f"  - Test '{test.description}' ({test.test_type}): {'PASSED' if test.success else 'FAILED'}\n"
            if test.extra_data:
                feedback += f"      Extra Data: {test.extra_data}\n"

        feedback += "\nExecution History:\n"
        for record in self.execution_history:
            feedback += f"  - Action: {record.action_event}, Success: {record.successfully_executed}, Time: {record.execution_time:.2f}s\n"
            if record.error:
                feedback += f"      Error: {record.error}\n"

        return feedback


class EvaluationStats(BaseModel):
    """Statistics for a single evaluation"""

    web_agent_id: str
    task_id: str
    action_count: int
    action_types: dict[str, int] = Field(default_factory=dict)

    # Timing stats
    start_time: float
    total_time: float = 0
    browser_setup_time: float = 0
    action_execution_times: list[float] = Field(default_factory=list)
    test_execution_time: float = 0
    random_clicker_time: float = 0

    # Performance stats
    raw_score: float = 0
    random_clicker_score: float = 0
    final_score: float = 0
    tests_passed: int = 0
    total_tests: int = 0

    # Error tracking
    had_errors: bool = False
    error_message: str = ""

    def get_summary_dict(self) -> dict[str, Any]:
        """Get a dictionary of summary statistics"""
        action_time = sum(self.action_execution_times) if self.action_execution_times else 0
        return {
            "agent_id": self.web_agent_id,
            "task_id": self.task_id,
            "actions": self.action_count,
            "score": self.final_score,
            "time_total": round(self.total_time, 2),
            "time_browser_setup": round(self.browser_setup_time, 2),
            "time_actions": round(action_time, 2),
            "time_avg_per_action": round(action_time / max(1, len(self.action_execution_times)), 3),
            "time_random": round(self.random_clicker_time, 2),
            "tests_passed": f"{self.tests_passed}/{self.total_tests}",
            "success": not self.had_errors,
        }


class EvaluationResult(BaseModel):
    """Encapsulates the output of a task evaluation."""

    final_score: float = 0
    test_results_matrix: list[list[TestResult]]  # List of test evaluation results
    execution_history: list[ActionExecutionResult]  # History of all actions executed
    feedback: Feedback | None = None  # Feedback generated during the evaluation
    web_agent_id: str | None = None
    raw_score: float = 0.0
    random_clicker_score: float = 0.0
    random_clicker_passed_tests_indexes: list[int] = Field(default_factory=list)
    evaluation_time: float = 0.0  # Time taken to evaluate this solution
    stats: EvaluationStats | None = None

    def model_dump(self, *args, **kwargs):
        base_dump = super().model_dump(*args, **kwargs)
        base_dump["execution_history"] = [action.model_dump() for action in self.execution_history]
        # Remove unwanted keys from feedback
        base_dump["feedback"].pop("execution_history", None)
        base_dump["feedback"].pop("test_results", None)
        return base_dump


class EvaluatorConfig(BaseModel):
    save_results_in_db: bool = False
    task_delay_in_seconds: float = Field(default=0.1, gt=0)
    chunk_size: int = Field(default=20, gt=0)
    browser_timeout: float = Field(default=10000, gt=0)
    event_monitor_interval: float = Field(default=0.1, gt=0, le=0.5)
    enable_grouping_tasks: bool = Field(default=True)
    normalize_score_with_random_clicker: bool = Field(default=True)
    cache_random_clicker_results: bool = Field(default=True)
    normalize_scores: bool = Field(default=True)
    verbose_logging: bool = Field(default=False)  # Default to minimal logging
    debug_mode: bool = Field(default=False)  # Even more minimal logging
