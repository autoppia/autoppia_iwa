# StatefulEvaluator

Evaluadores diseñados para Reinforcement Learning y entrenamiento de agentes.

## Descripción

`AsyncStatefulEvaluator` y `StatefulEvaluator` implementan la interfaz **WebCUA** (Web Computer Use API) para permitir el entrenamiento de agentes de Reinforcement Learning. Mantienen el estado del browser entre pasos y permiten obtener scores parciales después de cada acción.

## Características

- ✅ Implementa interfaz WebCUA
- ✅ Mantiene estado del browser entre steps
- ✅ Score parcial después de cada acción
- ✅ Versiones async y sync disponibles
- ✅ Compatible con frameworks de RL (PPO, DQN, etc.)
- ✅ Context manager para manejo de recursos

## Versiones Disponibles

### AsyncStatefulEvaluator (Async)

Para código asíncrono:

```python
from autoppia_iwa.src.evaluation import AsyncStatefulEvaluator

evaluator = AsyncStatefulEvaluator(
    task=task,
    web_agent_id="rl_agent",
    should_record_gif=False,
    capture_screenshot=True
)

# Reset inicial
step_result = await evaluator.reset()
print(f"Initial score: {step_result.score.raw_score}")

# Ejecutar acciones
for action in actions:
    step_result = await evaluator.step(action)
    print(f"Score after action: {step_result.score.raw_score}")
    print(f"Tests passed: {step_result.score.tests_passed}/{step_result.score.total_tests}")

await evaluator.close()
```

### StatefulEvaluator (Sync)

Para código síncrono (RL/PPO):

```python
from autoppia_iwa.src.evaluation import StatefulEvaluator

with StatefulEvaluator(task=task) as evaluator:
    # Reset inicial
    result = evaluator.reset()

    # Loop de RL
    done = False
    while not done:
        action = policy.select_action(result.snapshot)
        result = evaluator.step(action)

        reward = result.score.raw_score
        done = result.score.success

        policy.update(reward, done)
```

## Interfaz WebCUA

### Métodos Principales

```python
# Reset: Inicializa el entorno y navega a la URL
step_result = evaluator.reset()

# Step: Ejecuta una acción
step_result = evaluator.step(action)

# Get score: Obtiene score actual sin ejecutar acción
score = evaluator.get_score_details()

# Close: Limpia recursos
evaluator.close()
```

### StepResult

```python
@dataclass
class StepResult:
    score: ScoreDetails           # Score actual
    snapshot: BrowserSnapshot     # Estado del browser
    action_result: ActionExecutionResult | None  # Resultado de la acción
```

### ScoreDetails

```python
@dataclass
class ScoreDetails:
    raw_score: float = 0.0        # Score (0.0 - 1.0)
    tests_passed: int = 0         # Tests pasados
    total_tests: int = 0          # Tests totales
    success: bool = False         # True si todos los tests pasaron
```

### BrowserSnapshot

```python
@dataclass
class BrowserSnapshot:
    html: str                     # HTML actual
    url: str                      # URL actual
    screenshot: bytes | None      # Screenshot (si capture_screenshot=True)
```

## Uso con Reinforcement Learning

### Ejemplo PPO

```python
import torch
from autoppia_iwa.src.evaluation import StatefulEvaluator

class RLEnvironment:
    def __init__(self, task):
        self.evaluator = StatefulEvaluator(task=task, capture_screenshot=True)
        self.evaluator.reset()

    def reset(self):
        result = self.evaluator.reset()
        return self._extract_state(result.snapshot)

    def step(self, action):
        result = self.evaluator.step(action)

        state = self._extract_state(result.snapshot)
        reward = result.score.raw_score
        done = result.score.success or result.score.raw_score == 0.0
        info = {
            "tests_passed": result.score.tests_passed,
            "total_tests": result.score.total_tests
        }

        return state, reward, done, info

    def _extract_state(self, snapshot):
        # Convertir HTML/screenshot a representación para RL
        return torch.tensor(...)  # Tu representación

# Usar en entrenamiento
env = RLEnvironment(task)
agent = PPOAgent()

for episode in range(1000):
    state = env.reset()
    done = False

    while not done:
        action = agent.select_action(state)
        next_state, reward, done, info = env.step(action)
        agent.update(state, action, reward, next_state, done)
        state = next_state
```

### Ejemplo DQN

```python
from autoppia_iwa.src.evaluation import AsyncStatefulEvaluator

async def train_dqn(task, agent, episodes=1000):
    evaluator = AsyncStatefulEvaluator(task=task)

    for episode in range(episodes):
        result = await evaluator.reset()
        state = extract_features(result.snapshot)

        done = False
        episode_reward = 0

        while not done:
            action = agent.select_action(state, epsilon=0.1)
            result = await evaluator.step(action)

            next_state = extract_features(result.snapshot)
            reward = result.score.raw_score
            done = result.score.success

            agent.store_transition(state, action, reward, next_state, done)
            agent.train_step()

            state = next_state
            episode_reward += reward

        print(f"Episode {episode}: reward={episode_reward}")

    await evaluator.close()
```

## Configuración

```python
from autoppia_iwa.src.evaluation.stateful_evaluator import EvaluatorConfig

config = EvaluatorConfig(
    action_timeout_s=15.0,        # Timeout por acción
    page_default_timeout_ms=10000 # Timeout del navegador
)

evaluator = AsyncStatefulEvaluator(
    task=task,
    web_agent_id="rl_agent",
    should_record_gif=False,      # Generalmente False para RL
    capture_screenshot=True,      # True si necesitas screenshots
    config=config
)
```

## Acceso al Page de Playwright

```python
# Acceder al page directamente si necesitas operaciones custom
page = evaluator.page

# Ejemplo: obtener info adicional
await page.evaluate("document.title")
cookies = await page.context.cookies()
```

## Historial de Acciones

```python
# Ver todas las acciones ejecutadas
history = evaluator.history  # List[ActionExecutionResult]

for i, result in enumerate(history):
    print(f"Action {i}: {result.action.type} - {'✓' if result.successfully_executed else '✗'}")
```

## Diferencias con Otros Evaluadores

| Aspecto | ConcurrentEvaluator | IterativeEvaluator | StatefulEvaluator |
|---------|-------------------|-------------------|------------------|
| Input | TaskSolution | IWebAgent | Task + actions paso a paso |
| Control | Automático | Automático iterativo | Manual (step by step) |
| Score | Solo al final | Solo al final | Después de cada step |
| Estado | No persistente | No persistente | Persistente |
| Uso | Producción | Agentes adaptativos | RL/Entrenamiento |

## Casos de Uso

### 1. Entrenamiento de RL

Entrenar agentes de reinforcement learning:

```python
env = StatefulEvaluator(task=task)
agent = PPOAgent()

for episode in range(1000):
    state = env.reset()
    # Entrenamiento...
```

### 2. Testing de Acciones Individuales

Probar el efecto de acciones individuales:

```python
evaluator = AsyncStatefulEvaluator(task=task)
await evaluator.reset()

# Probar acción 1
result1 = await evaluator.step(action1)
print(f"Score after action 1: {result1.score.raw_score}")

# Probar acción 2
result2 = await evaluator.step(action2)
print(f"Score after action 2: {result2.score.raw_score}")
```

### 3. Exploración Interactiva

Explorar manualmente una task:

```python
evaluator = AsyncStatefulEvaluator(task=task)
await evaluator.reset()

# Navegar paso a paso
for action in exploratory_actions:
    result = await evaluator.step(action)
    print(f"Current URL: {result.snapshot.url}")
    print(f"Score: {result.score.raw_score}")

    if result.score.success:
        print("Task completed!")
        break
```

## Notas Importantes

- **Recursos**: Siempre usa `close()` o context manager para liberar recursos
- **Thread safety**: No es thread-safe, usa una instancia por thread
- **Performance**: Más lento que otros evaluadores (mantiene estado)
- **Screenshots**: Solo captura si `capture_screenshot=True`
- **GIFs**: Generalmente deshabilitados en RL (overhead)

## Limitaciones

- No soporta evaluación paralela de múltiples soluciones
- Más lento por el overhead de mantener estado
- Requiere gestión manual del ciclo de vida

## Cuándo Usar

✅ **Usa StatefulEvaluator cuando:**
- Estás entrenando agentes de RL
- Necesitas score después de cada acción
- Necesitas control fino sobre la ejecución
- Implementas algoritmos de exploración

❌ **Usa ConcurrentEvaluator cuando:**
- Solo necesitas evaluar soluciones completas
- No necesitas scores intermedios
- Priorizas rendimiento
