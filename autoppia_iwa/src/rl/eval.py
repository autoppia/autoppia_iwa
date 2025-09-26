import time
from typing import Any

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.evaluator.utils import run_global_tests


class RLEvaluator:
    """
    Evaluador incremental robusto:
      - No ejecuta acciones; solo lee eventos de backend y calcula score parcial.
      - Tolera tareas sin .tests u otros errores devolviendo score 0.0.
      - Expone metadatos de debug (últimos eventos, nº tests, nº pasados, último error).
    """

    def __init__(self, backend_service: BackendDemoWebService, web_agent_id: str):
        self.backend_service = backend_service
        self.web_agent_id = web_agent_id
        self.task: Task | None = None
        self.prev_score: float = 0.0

        # Debug metadata
        self.last_error: str | None = None
        self.last_events_meta: list[str] = []
        self.last_num_tests: int = 0
        self.last_passed: int = 0

    async def attach_task(self, task: Task) -> None:
        self.task = task
        self.prev_score = 0.0
        self.last_error = None
        self.last_events_meta = []
        self.last_num_tests = 0
        self.last_passed = 0

    async def partial_score(self) -> tuple[float, list[list] | None]:
        """
        Devuelve (score, test_results_matrix). Si no hay tests o falla el runner,
        devuelve (0.0, None) sin lanzar excepción.
        Actualiza metadatos de debug (eventos, nº tests, pasados, error).
        """
        if self.task is None:
            self.last_error = "no_task_attached"
            self.last_events_meta = []
            self.last_num_tests = 0
            self.last_passed = 0
            return 0.0, None

        _t0 = time.time()
        try:
            backend_events: list[Any] = await self.backend_service.get_backend_events(self.web_agent_id)  # type: ignore[assignment]
        except Exception as e:
            self.last_error = f"backend_events_error: {e}"
            self.last_events_meta = []
            self.last_num_tests = 0
            self.last_passed = 0
            return 0.0, None

        # Extrae nombres de eventos para depuración
        def _name(e: Any) -> str:
            if isinstance(e, dict):
                return str(e.get("event_name") or e.get("name") or e.get("event") or "?")
            return str(getattr(e, "event_name", "?"))

        self.last_events_meta = [_name(e) for e in backend_events][:12]  # corta a 12

        try:
            test_results_matrix = await run_global_tests(self.task, backend_events=backend_events)
        except Exception as e:
            self.last_error = f"run_global_tests_error: {e}"
            self.last_num_tests = 0
            self.last_passed = 0
            return 0.0, None

        score, num_tests, passed = 0.0, 0, 0
        try:
            if test_results_matrix and len(test_results_matrix[0]) > 0:
                num_tests = len(test_results_matrix[0])
                for j in range(num_tests):
                    if any(row[j].success for row in test_results_matrix):
                        passed += 1
                score = passed / num_tests if num_tests > 0 else 0.0
        except Exception as e:
            self.last_error = f"matrix_parse_error: {e}"
            self.last_num_tests = 0
            self.last_passed = 0
            return 0.0, None

        # Guarda metadatos
        self.last_error = None
        self.last_num_tests = num_tests
        self.last_passed = passed
        return score, test_results_matrix
