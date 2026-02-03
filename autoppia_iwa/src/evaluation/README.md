# Sistema de Evaluación de Autoppia IWA

Este módulo proporciona diferentes tipos de evaluadores para evaluar tareas de automatización web.

## Estructura de Carpetas

```
evaluation/
├── __init__.py                    # Exporta todos los evaluadores
├── classes.py                     # Clases comunes (EvaluationResult, EvaluatorConfig, etc.)
├── interfaces.py                  # Interfaz IEvaluator
│
├── concurrent_evaluator/          # Evaluador para soluciones completas
│   ├── __init__.py
│   └── evaluator.py              # ConcurrentEvaluator
│
├── stateful_evaluator/            # Evaluador para modo iterativo/stateful
│   ├── __init__.py
│   └── evaluator.py              # AsyncStatefulEvaluator, StatefulEvaluator
│
└── shared/                        # Utilidades compartidas
    ├── __init__.py
    ├── feedback_generator.py      # Generación de feedback
    ├── test_runner.py            # Ejecución de tests
    └── utils.py                  # Funciones utilitarias
```

## Evaluadores Disponibles

### 1. ConcurrentEvaluator

**Uso:** Evaluar soluciones completas con todas las acciones ya generadas (modo tradicional).

```python
from autoppia_iwa.src.evaluation import ConcurrentEvaluator, EvaluatorConfig

config = EvaluatorConfig(
    should_record_gif=True,
    enable_grouping_tasks=True,
    max_consecutive_action_failures=2
)

evaluator = ConcurrentEvaluator(web_project=project, config=config)

# Evaluar una solución
result = await evaluator.evaluate_single_task_solution(task, task_solution)

# Evaluar múltiples soluciones (con agrupación)
results = await evaluator.evaluate_task_solutions(task, task_solutions)
```

**Características:**
- Recibe `TaskSolution` con todas las acciones
- Agrupa soluciones idénticas para optimizar
- Soporta evaluación paralela de múltiples soluciones
- Genera GIFs de las ejecuciones

**Caso de uso típico:** Evaluar respuestas de mineros en Bittensor que envían todas las acciones de una vez.

---

### 2. StatefulEvaluator

**Uso:** Para evaluación iterativa paso a paso (usado en subnet y modo stateful del benchmark).

```python
from autoppia_iwa.src.evaluation import AsyncStatefulEvaluator, StatefulEvaluator

# Versión asíncrona
async_evaluator = AsyncStatefulEvaluator(task=task, web_agent_id="agent_id")
step_result = await async_evaluator.reset()
step_result = await async_evaluator.step(action)

# Versión síncrona (para RL/PPO)
with StatefulEvaluator(task=task) as evaluator:
    result = evaluator.reset()
    for action in actions:
        result = evaluator.step(action)
        score = evaluator.get_score_details()
```

**Características:**
- Implementa interfaz WebCUA
- Mantiene estado del browser entre steps
- Permite obtener score parcial en cada step
- Versiones async y sync disponibles
- El agente puede devolver múltiples acciones por llamada (ejecutadas en batch)
- Usado en la subnet para evaluar miners remotos

**Casos de uso típicos:**
- Evaluar miners remotos en la subnet (HTTP)
- Modo stateful del benchmark (agentes iterativos)
- Entrenar agentes de RL/PPO que necesitan feedback después de cada acción

---

## Utilidades Compartidas

Las utilidades en `shared/` están disponibles para todos los evaluadores:

```python
from autoppia_iwa.src.evaluation.shared import (
    FeedbackGenerator,
    TestRunner,
    generate_feedback,
    run_global_tests,
    run_partial_tests,
)
```

- **FeedbackGenerator:** Genera feedback detallado sobre la evaluación
- **TestRunner:** Ejecuta tests sobre las tareas
- **Utilidades:** Funciones para GIF, seeds, hashing, etc.

---

## Clases Comunes

```python
from autoppia_iwa.src.evaluation import (
    EvaluationResult,
    EvaluationStats,
    EvaluatorConfig,
    Feedback,
    TestResult,
    IEvaluator,
)
```

- **EvaluationResult:** Resultado de una evaluación
- **EvaluationStats:** Estadísticas detalladas
- **EvaluatorConfig:** Configuración de evaluadores
- **IEvaluator:** Interfaz que todos los evaluadores implementan

---

## Migración desde Estructura Antigua

Si anteriormente importabas:

```python
# Antes
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.evaluation.stateful_evaluator import StatefulEvaluator
```

Ahora simplemente usa:

```python
# Ahora
from autoppia_iwa.src.evaluation import ConcurrentEvaluator, StatefulEvaluator, IterativeEvaluator
```

Todos los evaluadores están disponibles desde el import principal.

---

## Ejemplos Completos

Ver ejemplos de uso en:
- `entrypoints/benchmark/` - Uso de ConcurrentEvaluator y StatefulEvaluator
- `entrypoints/test_task.py` - Uso de ConcurrentEvaluator
- Subnet: `autoppia_web_agents_subnet/validator/evaluation/stateful_cua_eval.py` - Uso de AsyncStatefulEvaluator

---

## Desarrollo

### Añadir un nuevo evaluador

1. Crear una nueva carpeta: `nuevo_evaluador/`
2. Implementar `evaluator.py` que implemente `IEvaluator`
3. Crear `__init__.py` exportando tu evaluador
4. Añadir export en `/evaluation/__init__.py`

### Añadir utilidades compartidas

Añadir funciones en `shared/utils.py` o crear nuevos módulos en `shared/`.
