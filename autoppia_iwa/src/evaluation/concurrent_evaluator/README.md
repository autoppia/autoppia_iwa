# ConcurrentEvaluator

Evaluador para soluciones completas donde todas las acciones ya están generadas.

## Descripción

El `ConcurrentEvaluator` recibe una `TaskSolution` completa con todas las acciones y las ejecuta secuencialmente en el navegador. Es el evaluador principal usado en producción para evaluar respuestas de mineros.

## Características

- ✅ Evalúa soluciones con todas las acciones pre-generadas
- ✅ Agrupa soluciones idénticas para optimizar rendimiento
- ✅ Soporta evaluación paralela de múltiples soluciones
- ✅ Genera GIFs de las ejecuciones
- ✅ Detección de fallos consecutivos
- ✅ Soporte para fases dinámicas (DOM mutations)

## Uso Básico

```python
from autoppia_iwa.src.evaluation import ConcurrentEvaluator, EvaluatorConfig
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.classes import TaskSolution

# Configuración
config = EvaluatorConfig(
    should_record_gif=True,
    enable_grouping_tasks=True,
    max_consecutive_action_failures=2,
    verbose_logging=True
)

# Crear evaluador
project = demo_web_projects[0]  # Usar el primer proyecto
evaluator = ConcurrentEvaluator(web_project=project, config=config)

# Evaluar una solución
task_solution = TaskSolution(
    task_id=task.id,
    actions=actions,  # Lista de BaseAction
    web_agent_id="my_agent"
)

result = await evaluator.evaluate_single_task_solution(task, task_solution)

print(f"Score: {result.final_score}")
print(f"Tests passed: {result.stats.tests_passed}/{result.stats.total_tests}")
```

## Evaluar Múltiples Soluciones

```python
# Múltiples soluciones (de diferentes mineros)
task_solutions = [
    TaskSolution(task_id=task.id, actions=actions1, web_agent_id="miner_1"),
    TaskSolution(task_id=task.id, actions=actions2, web_agent_id="miner_2"),
    TaskSolution(task_id=task.id, actions=actions3, web_agent_id="miner_3"),
]

# Evaluar todas (automáticamente agrupa las idénticas)
results = await evaluator.evaluate_task_solutions(task, task_solutions)

for result in results:
    print(f"Agent {result.web_agent_id}: {result.final_score}")
```

## Configuración Avanzada

```python
config = EvaluatorConfig(
    # GIF recording
    should_record_gif=True,

    # Optimización
    enable_grouping_tasks=True,  # Agrupa soluciones idénticas
    chunk_size=20,               # Número de evaluaciones en paralelo

    # Timeouts
    browser_timeout=10000,       # Timeout del navegador (ms)
    task_delay_in_seconds=0.1,   # Delay entre acciones

    # Error handling
    max_consecutive_action_failures=2,

    # Logging
    verbose_logging=False,
    debug_mode=False,
)
```

## Resultado de Evaluación

El `EvaluationResult` contiene:

```python
result = EvaluationResult(
    web_agent_id="miner_1",
    final_score=1.0,              # Score final (0.0 - 1.0)
    raw_score=1.0,                # Score sin ajustes
    test_results=[...],           # Lista de TestResult
    feedback=Feedback(...),       # Feedback detallado
    execution_history=[...],      # Historial de acciones
    evaluation_time=12.5,         # Tiempo total (segundos)
    stats=EvaluationStats(...),   # Estadísticas detalladas
    gif_recording="base64..."     # GIF de la ejecución
)
```

## Estadísticas

```python
stats = result.stats
print(f"Actions executed: {stats.action_count}")
print(f"Total time: {stats.total_time}s")
print(f"Browser setup: {stats.browser_setup_time}s")
print(f"Action execution: {sum(stats.action_execution_times)}s")
print(f"Tests passed: {stats.tests_passed}/{stats.total_tests}")
print(f"Had errors: {stats.had_errors}")
```

## Casos de Uso

### 1. Evaluación de Mineros en Bittensor

```python
# Los mineros devuelven TaskSolution con todas las acciones
for miner_uid, task_solution in miner_responses.items():
    result = await evaluator.evaluate_single_task_solution(task, task_solution)
    scores[miner_uid] = result.final_score
```

### 2. Benchmark de Agentes

```python
# Evaluar múltiples agentes en el mismo task
results = []
for agent in agents:
    # El agente genera todas las acciones
    solution = await agent.solve_task(task)
    result = await evaluator.evaluate_single_task_solution(task, solution)
    results.append(result)
```

### 3. Testing de Tasks

```python
# Verificar que un task es evaluable
test_solution = TaskSolution(
    task_id=task.id,
    actions=reference_actions,
    web_agent_id="test"
)
result = await evaluator.evaluate_single_task_solution(task, test_solution)
assert result.final_score > 0.8, "Task no pasa tests de referencia"
```

## Notas

- Las soluciones idénticas (mismo hash de acciones) se evalúan una sola vez
- El GIF se genera solo si `should_record_gif=True`
- Los fallos consecutivos detienen la evaluación temprano
- Soporta navegación con seeds para webs no reales
