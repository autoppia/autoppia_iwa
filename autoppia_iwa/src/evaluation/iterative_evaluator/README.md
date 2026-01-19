# IterativeEvaluator

Evaluador que funciona como un agente, ejecutando acciones paso a paso de forma iterativa.

## Descripción

El `IterativeEvaluator` llama al agente de forma iterativa, ejecutando una acción a la vez y enriqueciendo el task con el estado actual del browser antes de cada llamada. Esto permite que agentes adaptativos ajusten su estrategia basándose en el resultado de acciones previas.

## Características

- ✅ Llama al agente iterativamente
- ✅ Ejecuta una acción a la vez
- ✅ Enriquece el task con estado del browser (HTML, URL)
- ✅ El agente puede adaptar estrategia basándose en el estado
- ✅ Se detiene cuando el agente devuelve lista vacía
- ✅ Límite configurable de iteraciones
- ✅ Genera GIFs de las ejecuciones

## Diferencia con ConcurrentEvaluator

| Aspecto | ConcurrentEvaluator | IterativeEvaluator |
|---------|-------------------|-------------------|
| Input | TaskSolution completa | Agente (IWebAgent) |
| Llamadas al agente | 1 (todas las acciones) | N (una acción por iteración) |
| Contexto | Task inicial | Task + estado browser |
| Adaptabilidad | No | Sí |
| Uso típico | Mineros, benchmarks | Agentes adaptativos, RL |

## Uso Básico

```python
from autoppia_iwa.src.evaluation import IterativeEvaluator, EvaluatorConfig
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent

# Configuración
config = EvaluatorConfig(
    should_record_gif=True,
    max_consecutive_action_failures=2,
    verbose_logging=True
)

# Crear evaluador
project = demo_web_projects[0]
evaluator = IterativeEvaluator(web_project=project, config=config)

# Crear agente
agent = ApifiedWebAgent(
    base_url="http://localhost:8000",
    id="my_adaptive_agent",
    name="Adaptive Agent"
)

# Evaluar con el agente (máximo 50 acciones)
result = await evaluator.evaluate_with_agent(
    task=task,
    agent=agent,
    max_iterations=50
)

print(f"Score: {result.final_score}")
print(f"Actions executed: {result.stats.action_count}")
print(f"Tests passed: {result.stats.tests_passed}/{result.stats.total_tests}")
```

## Cómo Funciona

### Flujo de Ejecución

1. **Navegación inicial**: El evaluador navega a `task.url`
2. **Preparar task**: Se prepara el task con `prepare_for_agent()`
3. **Bucle iterativo** (hasta `max_iterations`):
   - Enriquecer task con estado del browser (HTML, URL)
   - Llamar `agent.solve_task(enriched_task)`
   - Tomar la **primera acción** de la lista devuelta
   - Ejecutar la acción en el browser
   - Si el agente devuelve lista vacía → terminar
   - Si hay fallos consecutivos → terminar con error
4. **Evaluación final**: Ejecutar tests y calcular score

### Enriquecimiento del Task

Antes de cada llamada, el task se enriquece con:

```python
# Información añadida al prompt
"Current browser state:
- URL: http://localhost:3000/movies
- HTML length: 45234 characters"

# Información añadida a relevant_data
task.relevant_data["browser_state"] = {
    "current_url": "http://localhost:3000/movies",
    "html_length": 45234
}
```

Esto permite que el agente tome decisiones informadas basándose en el estado actual.

## Ejemplo: Agente Adaptativo

```python
class AdaptiveAgent(IWebAgent):
    """Agente que adapta su estrategia según el estado del browser"""
    
    async def solve_task(self, task: Task) -> TaskSolution:
        # Obtener estado actual del browser
        browser_state = task.relevant_data.get("browser_state", {})
        current_url = browser_state.get("current_url", "")
        
        # Decidir siguiente acción basándose en la URL actual
        if "/login" in current_url:
            # Estamos en login, hacer login
            actions = [
                TypeAction(selector="input[name='email']", text="user@example.com"),
                TypeAction(selector="input[name='password']", text="password"),
                ClickAction(selector="button[type='submit']")
            ]
        elif "/dashboard" in current_url:
            # Ya estamos en dashboard, completar tarea
            actions = [
                ClickAction(selector=".create-button"),
                # ...
            ]
        else:
            # No sabemos dónde estamos, terminar
            actions = []
        
        return TaskSolution(
            task_id=task.id,
            actions=actions,
            web_agent_id=self.id
        )
```

## Configuración

```python
config = EvaluatorConfig(
    # GIF recording
    should_record_gif=True,
    
    # Timeouts
    browser_timeout=10000,
    task_delay_in_seconds=0.1,
    
    # Error handling (importante para modo iterativo)
    max_consecutive_action_failures=2,  # Detiene si 2 acciones fallan seguidas
    
    # Logging
    verbose_logging=True,
    debug_mode=False,
)

# Parámetro específico del evaluador
max_iterations = 50  # Máximo de acciones permitidas
```

## Control de Ejecución

### Detención por Lista Vacía

El agente puede indicar que terminó devolviendo lista vacía:

```python
async def solve_task(self, task: Task) -> TaskSolution:
    # Si ya completamos la tarea
    if self.task_completed:
        return TaskSolution(task_id=task.id, actions=[], web_agent_id=self.id)
    
    # Generar siguiente acción
    return TaskSolution(task_id=task.id, actions=[next_action], web_agent_id=self.id)
```

### Detención por Fallos Consecutivos

Si `max_consecutive_action_failures` acciones fallan consecutivamente, se detiene:

```python
# Configurar límite de fallos
config = EvaluatorConfig(max_consecutive_action_failures=3)

# Si 3 acciones fallan seguidas → early_stop_reason se establece
# y final_score = 0.0
```

### Límite de Iteraciones

Máximo de acciones permitidas:

```python
result = await evaluator.evaluate_with_agent(
    task=task,
    agent=agent,
    max_iterations=100  # Máximo 100 acciones
)
```

## Resultado

El resultado es idéntico al de `ConcurrentEvaluator`:

```python
result = EvaluationResult(
    web_agent_id="adaptive_agent",
    final_score=0.95,
    raw_score=0.95,
    test_results=[...],
    feedback=Feedback(...),
    execution_history=[...],  # Todas las acciones ejecutadas
    evaluation_time=18.3,
    stats=EvaluationStats(...),
    gif_recording="base64..."
)
```

## Casos de Uso

### 1. Agentes Adaptativos

Agentes que necesitan ver el resultado de cada acción antes de decidir:

```python
# El agente puede navegar de forma adaptativa
result = await evaluator.evaluate_with_agent(task, adaptive_agent, max_iterations=50)
```

### 2. Agentes de RL en Evaluación

Evaluar un agente de RL ya entrenado:

```python
# El agente RL genera acciones basándose en el estado
rl_agent = RLAgent(model=trained_model)
result = await evaluator.evaluate_with_agent(task, rl_agent, max_iterations=30)
```

### 3. Debugging de Agentes

Ver cómo el agente responde a diferentes estados:

```python
config = EvaluatorConfig(verbose_logging=True, debug_mode=True)
evaluator = IterativeEvaluator(project, config)
result = await evaluator.evaluate_with_agent(task, agent, max_iterations=20)
# Los logs mostrarán cada llamada al agente y las acciones generadas
```

## Compatibilidad con Agentes Existentes

Los agentes existentes que devuelven todas las acciones de una vez también funcionan:

```python
# Este agente devuelve [action1, action2, action3]
result = await evaluator.evaluate_with_agent(task, standard_agent)
# El evaluador usará solo action1 en cada iteración
```

Esto permite usar el mismo agente con ambos evaluadores.

## Limitaciones

- **Más lento**: Requiere múltiples llamadas al agente (vs. una sola en ConcurrentEvaluator)
- **No agrupa**: No puede agrupar soluciones idénticas (cada evaluación es única)
- **Requiere IWebAgent**: No puede trabajar con TaskSolution directamente

## Cuándo Usar

✅ **Usa IterativeEvaluator cuando:**
- El agente necesita ver el resultado de cada acción
- El agente es adaptativo
- Estás evaluando agentes de RL

❌ **Usa ConcurrentEvaluator cuando:**
- Ya tienes todas las acciones generadas
- Necesitas evaluar múltiples soluciones idénticas
- Necesitas máximo rendimiento
