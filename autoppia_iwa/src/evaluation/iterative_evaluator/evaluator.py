# iterative_evaluator.py
"""
Evaluador iterativo que funciona como un agente, ejecutando acciones paso a paso.

A diferencia del ConcurrentEvaluator que recibe todas las acciones de una vez,
este evaluador llama iterativamente al agente, ejecuta una acción, y vuelve a
llamar al agente con el nuevo estado del browser.
"""
import asyncio
import contextlib
import copy
import os
import time
from collections import defaultdict
from typing import Optional

from loguru import logger
from playwright.async_api import async_playwright, Page

from autoppia_iwa.config.config import EVALUATOR_HEADLESS, VALIDATOR_ID
from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.classes import EvaluationResult, EvaluationStats, EvaluatorConfig
from autoppia_iwa.src.evaluation.shared.utils import (
    display_single_evaluation_summary,
    extract_seed_from_url,
    generate_feedback,
    initialize_test_results,
    make_gif_from_screenshots,
    run_global_tests,
)
from autoppia_iwa.src.evaluation.interfaces import IEvaluator
from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.execution.dynamic import DynamicPlaywrightExecutor
from autoppia_iwa.src.web_agents.classes import IWebAgent, TaskSolution

EVALUATION_LEVEL_NAME = "EVALUATION"
EVALUATION_LEVEL_NO = 25


def _ensure_evaluation_level() -> None:
    """Register the EVALUATION level if it is missing."""
    try:
        logger.level(EVALUATION_LEVEL_NAME)
    except ValueError:
        logger.level(EVALUATION_LEVEL_NAME, EVALUATION_LEVEL_NO)


def _log_evaluation_fallback(message: str) -> None:
    """Fallback logger that emits messages at INFO level with EVALUATION tag."""
    logger.info(f"[EVALUATION] {message}")


def _log_action_execution(message: str, web_agent_id: str | None = None):
    """Helper function to log action execution with EVALUATION level"""
    agent_prefix = f"[agent={web_agent_id}] " if web_agent_id else ""
    try:
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_action_execution

        log_action_execution(f"{agent_prefix}{message}")
    except ImportError:
        _log_evaluation_fallback(f"[ACTION EXECUTION] {agent_prefix}{message}")


def _log_evaluation_event(message: str, context: str = "GENERAL"):
    """Helper function to log generic evaluation events with EVALUATION level."""
    try:
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_evaluation_event

        log_evaluation_event(message, context=context)
    except ImportError:
        _log_evaluation_fallback(message if context == "GENERAL" else f"[{context}] {message}")


class IterativeEvaluator(IEvaluator):
    """
    Evaluador iterativo que funciona como un agente.
    
    En lugar de recibir todas las acciones de una vez (como ConcurrentEvaluator),
    este evaluador:
    1. Llama al agente con el task y el estado actual del browser
    2. Obtiene la primera acción de la lista devuelta
    3. Ejecuta esa acción
    4. Actualiza el estado del browser (HTML, URL, etc.)
    5. Vuelve a llamar al agente con el nuevo estado
    6. Repite hasta que el agente devuelva una lista vacía o se alcance un límite
    """

    def __init__(self, web_project: WebProject, config: EvaluatorConfig):
        self.config = config
        self.total_evaluation_time = 0.0
        self.evaluation_count = 0
        self.web_project = web_project
        self.backend_demo_webs_service = BackendDemoWebService(web_project=web_project)

        # Statistics collection
        self.evaluation_stats: list[EvaluationStats] = []
        self.action_type_timing = defaultdict(list)
        self.errors: list[str] = []

        # Configure logs minimally if not verbose
        if not self.config.verbose_logging:
            logger.remove()
            logger.add(
                lambda msg: print(msg, end=""),
                level="WARNING" if self.config.debug_mode else "INFO",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            )

    async def evaluate_single_task_solution(self, task: Task, task_solution: TaskSolution) -> EvaluationResult:
        """
        Este método no se usa en el evaluador iterativo.
        En su lugar, usa evaluate_with_agent.
        """
        raise NotImplementedError(
            "IterativeEvaluator no soporta evaluate_single_task_solution. "
            "Usa evaluate_with_agent en su lugar."
        )

    async def evaluate_task_solutions(self, task: Task, task_solutions: list[TaskSolution]) -> list[EvaluationResult]:
        """
        Este método no se usa en el evaluador iterativo.
        En su lugar, usa evaluate_with_agent para cada agente.
        """
        raise NotImplementedError(
            "IterativeEvaluator no soporta evaluate_task_solutions. "
            "Usa evaluate_with_agent para cada agente en su lugar."
        )

    async def evaluate_with_agent(self, task: Task, agent: IWebAgent, max_iterations: int = 50) -> EvaluationResult:
        """
        Evalúa una tarea con un agente de forma iterativa.
        
        Args:
            task: La tarea a evaluar
            agent: El agente que generará las acciones iterativamente
            max_iterations: Número máximo de iteraciones (acciones) permitidas
            
        Returns:
            EvaluationResult con los resultados de la evaluación
        """
        try:
            _log_evaluation_event(f"Evaluating task {task.id} with agent {agent.id} (iterative mode)...")

            _log_evaluation_event("Resetting Project Environment & Database.", context="RESETTING DATABASE")
            await self.backend_demo_webs_service.reset_database(web_agent_id=agent.id)

            result = await self._evaluate_iteratively(task, agent, max_iterations)

            # Display final report for this evaluation
            if result.stats:
                display_single_evaluation_summary(result.stats, debug_mode=self.config.debug_mode)
                self.evaluation_stats.append(result.stats)

            return result
        finally:
            if self.backend_demo_webs_service:
                await self.backend_demo_webs_service.close()

    async def _evaluate_iteratively(self, task: Task, agent: IWebAgent, max_iterations: int) -> EvaluationResult:
        """
        Lógica interna para evaluar iterativamente con un agente.
        """
        web_agent_id = agent.id
        is_web_real = task.is_web_real

        stats = EvaluationStats(
            web_agent_id=web_agent_id,
            task_id=task.id,
            action_count=0,  # Se actualizará durante la ejecución
            start_time=time.time(),
        )

        # Validate NavigateAction seed usage against assigned seed in task.url
        try:
            assigned_seed = extract_seed_from_url(task.url)
        except Exception:
            assigned_seed = None

        evaluation_gif = ""
        execution_history: list[ActionExecutionResult] = []
        action_execution_times: list[float] = []
        consecutive_failures = 0
        max_consecutive_failures = self.config.max_consecutive_action_failures
        early_stop_reason: str | None = None

        try:
            browser_setup_start = time.time()

            # Start browser usage
            browser_execution_start = time.time()
            stats.browser_setup_time = browser_execution_start - browser_setup_start

            _log_evaluation_event("Executing actions iteratively in browser", context=f"ACTION EXECUTION | agent={web_agent_id}")

            # Ejecutar iterativamente
            execution_history, action_execution_times, early_stop_reason = await self._execute_iteratively(
                task, agent, web_agent_id, is_web_real, max_iterations, max_consecutive_failures
            )

            # Si la ejecución se detuvo temprano debido a fallos consecutivos
            task_failed_due_to_consecutive_failures = False
            if early_stop_reason:
                stats.had_errors = True
                stats.error_message = early_stop_reason
                task_failed_due_to_consecutive_failures = True
                _log_evaluation_event(
                    f"Task marked as FAILED: {early_stop_reason}",
                    context=f"ACTION EXECUTION | agent={web_agent_id}"
                )

            # Generar GIF si está habilitado
            if self.config.should_record_gif:
                _log_evaluation_event("🎬 GIF ENABLED", context="GIF")
                all_screenshots = []
                if execution_history:
                    all_screenshots.append(execution_history[0].browser_snapshot.screenshot_before)

                    for h in execution_history:
                        all_screenshots.append(h.browser_snapshot.screenshot_after)

                if all_screenshots:
                    evaluation_gif = make_gif_from_screenshots(all_screenshots)
                    if evaluation_gif:
                        _log_evaluation_event("✅ GIF CREATION SUCCESS", context="GIF")
                    else:
                        _log_evaluation_event("❌ GIF CREATION ERROR", context="GIF")
                        evaluation_gif = None
                else:
                    _log_evaluation_event("❌ GIF CREATION ERROR", context="GIF")
                    evaluation_gif = None
            else:
                _log_evaluation_event("📷 GIF Recording disabled (should_record_gif=False)", context="GIF")

            stats.action_execution_times = action_execution_times
            stats.action_count = len(execution_history)

            # Contar tipos de acciones
            for action_result in execution_history:
                action_type = action_result.action.type
                stats.action_types[action_type] = stats.action_types.get(action_type, 0) + 1

            # Ejecutar tests
            test_start_time = time.time()
            backend_events = await self.backend_demo_webs_service.get_backend_events(web_agent_id)

            if self.config.debug_mode:
                logger.debug("🔍 DEBUG - Backend Events Retrieved:")
                logger.debug(f"   - Number of events: {len(backend_events) if backend_events else 0}")

            test_results = await run_global_tests(task, backend_events=backend_events, web_agent_id=web_agent_id)

            if self.config.debug_mode:
                logger.debug("🔍 DEBUG - Test Results:")
                logger.debug(f"   - Number of tests: {len(test_results) if test_results else 0}")

            stats.test_execution_time = time.time() - test_start_time

            # Calcular score
            raw_score = 0.0
            tests_passed_count = 0
            num_tests = 0

            if test_results:
                num_tests = len(test_results)
                stats.total_tests = num_tests

                for test_result in test_results:
                    if test_result.success:
                        tests_passed_count += 1

                if num_tests > 0:
                    # Binary score: 1.0 if AT LEAST ONE test passed, 0.0 otherwise
                    raw_score = 1.0 if tests_passed_count > 0 else 0.0
                    if self.config.debug_mode:
                        logger.debug(f"   - Tests passed: {tests_passed_count}/{num_tests}")
                        logger.debug(f"   - Raw score (binary): {raw_score:.4f}")

            stats.tests_passed = tests_passed_count
            stats.raw_score = raw_score

            # Si la tarea falló debido a fallos consecutivos, establecer score a 0.0
            if task_failed_due_to_consecutive_failures:
                final_score = 0.0
                stats.raw_score = 0.0
            else:
                final_score = raw_score

            stats.final_score = final_score
            stats.total_time = time.time() - stats.start_time

            # Generar feedback
            feedback = generate_feedback(task, execution_history, test_results)

            return EvaluationResult(
                web_agent_id=web_agent_id,
                final_score=final_score,
                raw_score=raw_score,
                test_results=test_results,
                feedback=feedback,
                execution_history=execution_history,
                evaluation_time=stats.total_time,
                stats=stats,
                gif_recording=evaluation_gif,
            )

        except Exception as e:
            stats.had_errors = True
            stats.error_message = str(e)
            stats.total_time = time.time() - stats.start_time

            return EvaluationResult(
                web_agent_id=web_agent_id,
                final_score=0,
                raw_score=0,
                test_results=initialize_test_results(task),
                feedback=None,
                execution_history=[],
                evaluation_time=0,
                stats=stats,
                gif_recording=evaluation_gif,
            )

    async def _execute_iteratively(
        self,
        task: Task,
        agent: IWebAgent,
        web_agent_id: str,
        is_web_real: bool,
        max_iterations: int,
        max_consecutive_failures: int,
    ) -> tuple[list[ActionExecutionResult], list[float], str | None]:
        """
        Ejecuta acciones de forma iterativa llamando al agente en cada paso.
        
        Returns:
            Tuple de (action_results, action_execution_times, early_stop_reason)
        """
        action_execution_times: list[float] = []
        action_results: list[ActionExecutionResult] = []
        consecutive_failures = 0
        early_stop_reason: str | None = None

        async with async_playwright() as playwright:
            browser, context, page = None, None, None
            try:
                browser_specifications = task.specifications or BrowserSpecification()
                browser = await playwright.chromium.launch(
                    headless=EVALUATOR_HEADLESS,
                    args=[f"--window-size={browser_specifications.screen_width},{browser_specifications.screen_height}"],
                )
                context = await browser.new_context(
                    extra_http_headers={"X-WebAgent-Id": web_agent_id, "X-Validator-Id": VALIDATOR_ID},
                    no_viewport=True,
                )
                context.set_default_timeout(self.config.browser_timeout)
                page = await context.new_page()

                # Inicializar executor
                dynamic_config = self.config.dynamic_phase_config
                dynamic_enabled = dynamic_config.any_enabled() if dynamic_config else False
                if dynamic_enabled:
                    try:
                        seed_value = extract_seed_from_url(task.url)
                    except Exception:
                        seed_value = None
                    browser_executor = DynamicPlaywrightExecutor(
                        browser_specifications,
                        page,
                        self.backend_demo_webs_service,
                        dynamic_config=dynamic_config,
                        project_id=self.web_project.id,
                        seed=seed_value,
                    )
                else:
                    browser_executor = PlaywrightBrowserExecutor(browser_specifications, page, self.backend_demo_webs_service)

                # Navegar a la URL inicial
                nav_action = NavigateAction(url=task.url)
                _log_action_execution(f"🎬 Navigating to initial URL: {task.url}", web_agent_id=web_agent_id)
                nav_result = await browser_executor.execute_single_action(
                    nav_action, web_agent_id, iteration=0, is_web_real=is_web_real, should_record=self.config.should_record_gif
                )
                action_results.append(nav_result)
                action_execution_times.append(nav_result.execution_time or 0.0)

                # Preparar el task inicial para el agente
                current_task = task.prepare_for_agent(web_agent_id)

                # Bucle iterativo
                total_actions_executed = 0
                agent_call_count = 0
                
                while total_actions_executed < max_iterations:
                    agent_call_count += 1
                    _log_action_execution(
                        f"🔄 Agent call #{agent_call_count} - Total actions: {total_actions_executed}/{max_iterations}",
                        web_agent_id=web_agent_id
                    )

                    # Enriquecer el task con el estado actual del browser
                    enriched_task = await self._enrich_task_with_browser_state(current_task, page)

                    # Llamar al agente
                    try:
                        task_solution = await agent.solve_task(enriched_task)
                    except Exception as e:
                        _log_action_execution(
                            f"❌ Error calling agent: {e}",
                            web_agent_id=web_agent_id
                        )
                        consecutive_failures += 1
                        if consecutive_failures >= max_consecutive_failures:
                            early_stop_reason = f"Agent call failed {consecutive_failures} times consecutively"
                            break
                        continue

                    # Si el agente no devuelve acciones, terminamos
                    if not task_solution or not task_solution.actions:
                        _log_action_execution(
                            f"✅ Agent returned no actions - task completed or agent finished",
                            web_agent_id=web_agent_id
                        )
                        break

                    # Ejecutar TODAS las acciones que el agente devolvió
                    actions_in_this_batch = task_solution.actions
                    num_actions_in_batch = len(actions_in_this_batch)
                    
                    # Limitar si excedería max_iterations
                    actions_remaining = max_iterations - total_actions_executed
                    if num_actions_in_batch > actions_remaining:
                        _log_action_execution(
                            f"⚠️  Agent returned {num_actions_in_batch} actions, but only {actions_remaining} remaining to reach max_iterations. Executing only {actions_remaining}.",
                            web_agent_id=web_agent_id
                        )
                        actions_in_this_batch = actions_in_this_batch[:actions_remaining]
                        num_actions_in_batch = actions_remaining
                    
                    _log_action_execution(
                        f"📦 Executing {num_actions_in_batch} action(s) from agent response",
                        web_agent_id=web_agent_id
                    )

                    # Ejecutar cada acción del batch
                    for action_idx, action in enumerate(actions_in_this_batch, 1):
                        total_actions_executed += 1
                        
                        _log_action_execution(
                            f"   ▶️  Action {action_idx}/{num_actions_in_batch} (Total: {total_actions_executed}/{max_iterations}): {action.type}",
                            web_agent_id=web_agent_id
                        )
                        
                        start_time_action = time.time()
                        try:
                            result = await browser_executor.execute_single_action(
                                action, web_agent_id, iteration=total_actions_executed, is_web_real=is_web_real, should_record=self.config.should_record_gif
                            )
                            action_results.append(result)
                            elapsed = time.time() - start_time_action
                            action_execution_times.append(elapsed)

                            # Rastrear fallos consecutivos
                            if result and not result.successfully_executed:
                                consecutive_failures += 1
                                _log_action_execution(
                                    f"      ❌ FAILED in {elapsed:.2f}s - Error: {getattr(result, 'error', 'unknown')} "
                                    f"(Consecutive failures: {consecutive_failures}/{max_consecutive_failures})",
                                    web_agent_id=web_agent_id
                                )

                                if consecutive_failures >= max_consecutive_failures:
                                    early_stop_reason = f"Task marked as failed after {consecutive_failures} consecutive action failures (limit: {max_consecutive_failures})"
                                    _log_action_execution(
                                        f"🛑 Stopping execution: {early_stop_reason}",
                                        web_agent_id=web_agent_id
                                    )
                                    break
                            else:
                                # Resetear contador en éxito
                                consecutive_failures = 0
                                _log_action_execution(
                                    f"      ✅ SUCCESS in {elapsed:.2f}s",
                                    web_agent_id=web_agent_id
                                )

                            self.action_type_timing[action.type].append(elapsed)

                            # Pausa opcional entre acciones
                            if self.config.task_delay_in_seconds > 0:
                                await asyncio.sleep(self.config.task_delay_in_seconds)

                        except Exception as e:
                            consecutive_failures += 1
                            _log_action_execution(
                                f"      ❌ EXCEPTION: {e} "
                                f"(Consecutive failures: {consecutive_failures}/{max_consecutive_failures})",
                                web_agent_id=web_agent_id
                            )
                            elapsed = time.time() - start_time_action
                            action_execution_times.append(elapsed)

                            if consecutive_failures >= max_consecutive_failures:
                                early_stop_reason = f"Task marked as failed after {consecutive_failures} consecutive action failures (limit: {max_consecutive_failures})"
                                _log_action_execution(
                                    f"🛑 Stopping execution: {early_stop_reason}",
                                    web_agent_id=web_agent_id
                                )
                                break
                    
                    # Si hubo early stop por fallos consecutivos, salir del bucle principal
                    if early_stop_reason:
                        break

                if early_stop_reason:
                    _log_action_execution(
                        f"🏁 Finished: {total_actions_executed} actions executed in {agent_call_count} agent call(s) (stopped early due to consecutive failures)",
                        web_agent_id=web_agent_id
                    )
                else:
                    _log_action_execution(
                        f"🏁 Finished: {total_actions_executed} actions executed in {agent_call_count} agent call(s) (reached max_iterations or agent finished)",
                        web_agent_id=web_agent_id
                    )

                return action_results, action_execution_times, early_stop_reason

            except Exception as e:
                logger.error(f"Browser evaluation error: {e}")
                return [], [], f"Browser evaluation error: {e}"
            finally:
                if context:
                    await context.close()
                if browser:
                    await browser.close()

    async def _enrich_task_with_browser_state(self, task: Task, page: Page) -> Task:
        """
        Enriquece el task con el estado actual del browser (HTML, URL, etc.).
        
        Esto permite que el agente tenga información del estado actual para
        generar la siguiente acción de forma más inteligente.
        """
        try:
            # Obtener el estado actual del browser
            current_html = await page.content()
            current_url = page.url

            # Crear una copia del task
            enriched_task = copy.deepcopy(task)

            # Añadir información del browser al prompt o relevant_data
            browser_state_info = f"\n\nCurrent browser state:\n- URL: {current_url}\n- HTML length: {len(current_html)} characters"
            
            # Añadir al prompt (puedes ajustar esto según cómo quieras que el agente reciba la información)
            enriched_task.prompt = enriched_task.prompt + browser_state_info

            # Opcionalmente, también puedes añadir al relevant_data
            if "browser_state" not in enriched_task.relevant_data:
                enriched_task.relevant_data["browser_state"] = {}
            enriched_task.relevant_data["browser_state"]["current_url"] = current_url
            enriched_task.relevant_data["browser_state"]["html_length"] = len(current_html)

            return enriched_task
        except Exception as e:
            logger.warning(f"Error enriching task with browser state: {e}")
            # Si hay error, devolver el task original
            return task
