# Estructura del Sistema de Evaluación

## 📁 Organización de Carpetas

```
evaluation/
│
├── 📄 __init__.py                    # Exporta todos los evaluadores y clases
├── 📄 classes.py                     # Clases comunes (EvaluationResult, EvaluatorConfig, etc.)
├── 📄 interfaces.py                  # Interfaz IEvaluator
├── 📄 README.md                      # Documentación general
├── 📄 STRUCTURE.md                   # Este archivo
│
├── 📂 concurrent_evaluator/          # ⚡ Evaluador para soluciones completas
│   ├── 📄 __init__.py
│   ├── 📄 evaluator.py              # ConcurrentEvaluator
│   └── 📄 README.md                 # Documentación específica
│
├── 📂 iterative_evaluator/           # 🔄 Evaluador iterativo (agentes)
│   ├── 📄 __init__.py
│   ├── 📄 evaluator.py              # IterativeEvaluator
│   └── 📄 README.md                 # Documentación específica
│
├── 📂 stateful_evaluator/            # 🎮 Evaluador para RL/PPO
│   ├── 📄 __init__.py
│   ├── 📄 evaluator.py              # AsyncStatefulEvaluator, StatefulEvaluator
│   └── 📄 README.md                 # Documentación específica
│
└── 📂 shared/                        # 🔧 Utilidades compartidas
    ├── 📄 __init__.py
    ├── 📄 feedback_generator.py      # Generación de feedback
    ├── 📄 test_runner.py            # Ejecución de tests
    └── 📄 utils.py                  # Funciones utilitarias
```

## 🎯 Evaluadores

### 1. ConcurrentEvaluator ⚡

**Ubicación:** `concurrent_evaluator/evaluator.py`

**Propósito:** Evaluar soluciones completas con todas las acciones ya generadas.

**Uso típico:**
- Evaluar respuestas de mineros en Bittensor
- Benchmarks de agentes
- Testing de tasks

**Import:**
```python
from autoppia_iwa.src.evaluation import ConcurrentEvaluator
```

**Características clave:**
- ✅ Recibe TaskSolution completa
- ✅ Agrupa soluciones idénticas
- ✅ Evaluación paralela
- ✅ Genera GIFs

---

### 2. IterativeEvaluator 🔄

**Ubicación:** `iterative_evaluator/evaluator.py`

**Propósito:** Evaluar agentes de forma iterativa, acción por acción.

**Uso típico:**
- Agentes adaptativos
- Agentes que necesitan ver resultado de cada acción
- Evaluación de agentes de RL

**Import:**
```python
from autoppia_iwa.src.evaluation import IterativeEvaluator
```

**Características clave:**
- ✅ Llama al agente iterativamente
- ✅ Enriquece task con estado del browser
- ✅ Una acción a la vez
- ✅ Agente puede adaptar estrategia

---

### 3. StatefulEvaluator 🎮

**Ubicación:** `stateful_evaluator/evaluator.py`

**Propósito:** Para Reinforcement Learning y entrenamiento de agentes.

**Uso típico:**
- Entrenamiento de RL (PPO, DQN, etc.)
- Testing de acciones individuales
- Exploración interactiva

**Import:**
```python
from autoppia_iwa.src.evaluation import AsyncStatefulEvaluator, StatefulEvaluator
```

**Características clave:**
- ✅ Interfaz WebCUA
- ✅ Mantiene estado entre steps
- ✅ Score parcial después de cada acción
- ✅ Versiones async y sync

---

## 🔧 Utilidades Compartidas

**Ubicación:** `shared/`

Todas las utilidades comunes usadas por los evaluadores:

### feedback_generator.py
- `FeedbackGenerator`: Genera feedback detallado de evaluaciones

### test_runner.py
- `TestRunner`: Ejecuta tests sobre tasks

### utils.py
- `generate_feedback()`: Genera feedback de evaluación
- `run_global_tests()`: Ejecuta todos los tests de una task
- `run_partial_tests()`: Ejecuta tests parciales (para RL)
- `make_gif_from_screenshots()`: Genera GIF de screenshots
- `hash_actions()`: Hash de acciones para agrupación
- `extract_seed_from_url()`: Extrae seed de URL
- Y más...

**Import:**
```python
from autoppia_iwa.src.evaluation.shared import (
    FeedbackGenerator,
    TestRunner,
    generate_feedback,
    run_global_tests,
)
```

---

## 📦 Clases Comunes

**Ubicación:** `classes.py`

Clases usadas por todos los evaluadores:

```python
from autoppia_iwa.src.evaluation import (
    EvaluationResult,      # Resultado de evaluación
    EvaluationStats,       # Estadísticas detalladas
    EvaluatorConfig,       # Configuración de evaluadores
    Feedback,              # Feedback de evaluación
    TestResult,            # Resultado de un test
)
```

---

## 🔌 Interfaz

**Ubicación:** `interfaces.py`

```python
from autoppia_iwa.src.evaluation import IEvaluator
```

Todos los evaluadores implementan `IEvaluator`:

```python
class IEvaluator(ABC):
    @abstractmethod
    async def evaluate_single_task_solution(self, task: Task, task_solution: TaskSolution) -> EvaluationResult:
        ...
    
    @abstractmethod
    async def evaluate_task_solutions(self, task: Task, task_solutions: list[TaskSolution]) -> list[EvaluationResult]:
        ...
```

**Nota:** `IterativeEvaluator` no implementa estos métodos (usa `evaluate_with_agent`).

---

## 🚀 Imports Simplificados

Todos los evaluadores y utilidades están disponibles desde el import principal:

```python
# Evaluadores
from autoppia_iwa.src.evaluation import (
    ConcurrentEvaluator,
    IterativeEvaluator,
    AsyncStatefulEvaluator,
    StatefulEvaluator,
)

# Clases
from autoppia_iwa.src.evaluation import (
    EvaluationResult,
    EvaluationStats,
    EvaluatorConfig,
    Feedback,
    TestResult,
    IEvaluator,
)

# Utilidades
from autoppia_iwa.src.evaluation.shared import (
    FeedbackGenerator,
    TestRunner,
    generate_feedback,
    run_global_tests,
)
```

---

## 📚 Documentación

Cada evaluador tiene su propia documentación detallada:

- **General:** `evaluation/README.md`
- **ConcurrentEvaluator:** `concurrent_evaluator/README.md`
- **IterativeEvaluator:** `iterative_evaluator/README.md`
- **StatefulEvaluator:** `stateful_evaluator/README.md`

---

## 🔄 Comparación Rápida

| Característica | Concurrent | Iterative | Stateful |
|---------------|-----------|-----------|----------|
| **Input** | TaskSolution | IWebAgent | Task + actions |
| **Llamadas al agente** | 1 | N | Manual |
| **Estado persistente** | ❌ | ❌ | ✅ |
| **Score parcial** | ❌ | ❌ | ✅ |
| **Agrupación** | ✅ | ❌ | ❌ |
| **Paralelo** | ✅ | ❌ | ❌ |
| **Adaptativo** | ❌ | ✅ | ✅ |
| **RL/PPO** | ❌ | ❌ | ✅ |
| **Uso típico** | Producción | Agentes adaptativos | Entrenamiento RL |

---

## ✅ Ventajas de esta Estructura

1. **Encapsulación:** Cada evaluador está en su propia carpeta con su documentación
2. **Claridad:** Es fácil entender qué hace cada evaluador
3. **Mantenibilidad:** Cambios en un evaluador no afectan a otros
4. **Reutilización:** Utilidades compartidas en `shared/`
5. **Documentación:** Cada carpeta tiene su README específico
6. **Imports limpios:** Todo disponible desde `autoppia_iwa.src.evaluation`

---

## 🔨 Desarrollo

### Añadir un nuevo evaluador

1. Crear carpeta: `nuevo_evaluador/`
2. Crear `evaluator.py` implementando `IEvaluator` (o interfaz custom)
3. Crear `__init__.py` exportando tu evaluador
4. Crear `README.md` con documentación
5. Añadir export en `/evaluation/__init__.py`

### Añadir utilidades compartidas

1. Añadir función en `shared/utils.py`
2. O crear nuevo módulo en `shared/`
3. Exportar en `shared/__init__.py`

---

## 📝 Notas

- Todos los evaluadores comparten las mismas clases (`EvaluationResult`, `EvaluatorConfig`, etc.)
- Las utilidades en `shared/` están disponibles para todos
- Cada evaluador puede tener su propia configuración adicional
- La interfaz `IEvaluator` es opcional (IterativeEvaluator no la implementa)
