# Changelog - IterativeEvaluator

## [Mejorado] 2026-01-22 - Ejecución de Múltiples Acciones por Batch

### 🎯 Problema Anterior
El `IterativeEvaluator` ejecutaba **solo la primera acción** de la lista que devolvía el agente, ignorando el resto. Esto era ineficiente porque:
- Desperdiciaba las acciones que el agente ya había decidido
- Requería múltiples llamadas al agente innecesarias
- Aumentaba la latencia total de evaluación

### ✅ Solución Implementada
Ahora el `IterativeEvaluator` ejecuta **TODAS las acciones** que el agente devuelve en cada llamada.

### 📊 Comportamiento Nuevo

#### Antes (ineficiente):
```python
# Agente devuelve: [Action1, Action2, Action3]
# IterativeEvaluator ejecuta: Action1 ❌ (ignora Action2 y Action3)
# Vuelve a llamar al agente...
```

#### Ahora (eficiente):
```python
# Agente devuelve: [Action1, Action2, Action3]
# IterativeEvaluator ejecuta: Action1, Action2, Action3 ✅
# Vuelve a llamar al agente...
```

### 🔑 Ventajas

1. **Eficiencia**: Menos llamadas al agente para el mismo número de acciones
2. **Flexibilidad**: El agente puede decidir cuántas acciones enviar en cada paso
3. **Compatibilidad**: Una solución válida para `ConcurrentEvaluator` también lo es para `IterativeEvaluator`

### 📝 Ejemplo Comparativo

```python
# Agente que envía batches de acciones
class BatchAgent:
    async def solve_task(self, task):
        if self.call_count == 1:
            return TaskSolution(actions=[Action1, Action2, Action3])  # 3 acciones
        elif self.call_count == 2:
            return TaskSolution(actions=[Action4, Action5])           # 2 acciones
        else:
            return TaskSolution(actions=[])                           # Terminar

# Resultado:
# - Total de acciones: 5
# - Llamadas al agente: 2
# - Eficiencia: 2.5 acciones por llamada
```

vs

```python
# Agente que envía una acción a la vez
class SingleActionAgent:
    async def solve_task(self, task):
        if self.call_count <= 5:
            return TaskSolution(actions=[ActionN])  # 1 acción
        else:
            return TaskSolution(actions=[])         # Terminar

# Resultado:
# - Total de acciones: 5
# - Llamadas al agente: 5
# - Eficiencia: 1 acción por llamada
```

### 🔍 Logs Mejorados

Los nuevos logs muestran claramente el proceso:

```
🔄 Agent call #1 - Total actions: 0/50
📦 Executing 3 action(s) from agent response
   ▶️  Action 1/3 (Total: 1/50): NavigateAction
      ✅ SUCCESS in 0.72s
   ▶️  Action 2/3 (Total: 2/50): ClickAction
      ✅ SUCCESS in 0.15s
   ▶️  Action 3/3 (Total: 3/50): TypeAction
      ✅ SUCCESS in 0.23s

🔄 Agent call #2 - Total actions: 3/50
📦 Executing 2 action(s) from agent response
   ...

🏁 Finished: 5 actions executed in 2 agent call(s)
```

### ⚠️ Límite de Iteraciones

El parámetro `max_iterations_per_task` ahora cuenta **acciones totales ejecutadas**, no llamadas al agente:

```python
# Configuración
max_iterations_per_task = 50  # Máximo 50 ACCIONES (no 50 llamadas)

# Si el agente devuelve [A1, A2, A3] en cada llamada:
# - Llamada 1: ejecuta 3 acciones (total: 3/50)
# - Llamada 2: ejecuta 3 acciones (total: 6/50)
# - ...
# - Llamada 17: ejecuta 2 acciones (total: 50/50) ← Se detiene aquí
```

### 🧪 Testing

Se incluyen scripts de prueba:
- `test_batch_agent.py`: Agentes de prueba (BatchTestAgent, SingleActionAgent)
- `test_batch_simple.py`: Test simple que compara ambos comportamientos

Ejecutar:
```bash
python -m autoppia_iwa.entrypoints.benchmark.test_batch_simple
```

### 💡 Recomendación

Para máxima eficiencia:
- Si tu agente **ya sabe** las próximas N acciones → envíalas todas en un batch
- Si tu agente **necesita ver el resultado** antes de decidir → envía una acción a la vez
- El `IterativeEvaluator` ahora soporta ambos casos óptimamente

### 🔄 Compatibilidad

✅ **100% compatible con código existente**: Los agentes que devuelven una sola acción siguen funcionando igual.

✅ **Mejora automática**: Los agentes que ya devolvían múltiples acciones ahora se ejecutan más eficientemente.
