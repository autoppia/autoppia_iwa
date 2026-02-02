# Modo Stateful - Guía Completa

## 🎯 ¿Qué es el Modo Stateful?

El **modo stateful** evalúa agentes que deciden **paso a paso**, viendo el estado del browser en cada iteración. Es **idéntico** a cómo funciona la subnet con miners remotos.

## ✅ Requisito: Agente HTTP

En modo stateful, el agente **DEBE** ser un servidor HTTP que exponga el endpoint `/act`.

**NO puedes usar:**
- ❌ Agentes Python locales (`FixedAutobooksAgent`, etc.)
- ❌ `solve_task()` (solo para modo concurrent)

**Debes usar:**
- ✅ Servidor HTTP con endpoint `/act`
- ✅ `ApifiedWebCUA(base_url="...")`

---

## 🚀 Inicio Rápido

### 1. Crear un agente HTTP

```python
# my_agent.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ActRequest(BaseModel):
    task_id: str | None = None
    prompt: str | None = None
    url: str
    snapshot_html: str
    step_index: int

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/act")
async def act(request: ActRequest):
    # Tu lógica aquí: analiza el HTML y decide qué hacer
    
    # Ejemplo: devolver acciones
    actions = [
        {"type": "ClickAction", "selector": "#login"},
        {"type": "TypeAction", "selector": "#username", "text": "user"},
    ]
    
    return {"actions": actions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
```

### 2. Ejecutar el agente

```bash
python my_agent.py
# Agente corriendo en http://localhost:5000
```

### 3. Configurar el benchmark

```python
# run_stateful.py
from autoppia_iwa.src.web_agents.cua import ApifiedWebCUA

AGENTS = [
    ApifiedWebCUA(base_url="http://localhost:5000", id="1", name="MyAgent"),
]

CFG = BenchmarkConfig(
    evaluator_mode="stateful",
    max_steps_per_task=50,
    agents=AGENTS,
    # ...
)
```

### 4. Ejecutar el benchmark

```bash
python -m autoppia_iwa.entrypoints.benchmark.run_stateful
```

---

## 📝 Especificación del Endpoint `/act`

### Request (POST /act)

```json
{
  "task_id": "abc-123",
  "prompt": "Click the login button and enter username",
  "url": "http://localhost:8001/login",
  "snapshot_html": "<html>...</html>",
  "step_index": 0,
  "web_project_id": "autobooks"
}
```

### Response

```json
{
  "actions": [
    {"type": "ClickAction", "selector": "#login"},
    {"type": "TypeAction", "selector": "#username", "text": "myuser"},
    {"type": "TypeAction", "selector": "#password", "text": "mypass"},
    {"type": "ClickAction", "selector": "#submit"}
  ]
}
```

**Notas:**
- Puedes devolver **múltiples acciones** (se ejecutan en batch)
- Si devuelves lista vacía `[]`, se considera que el agente terminó
- Los tipos de acciones disponibles:
  - `NavigateAction`: `{"type": "NavigateAction", "url": "..."}`
  - `ClickAction`: `{"type": "ClickAction", "selector": "..."}`
  - `TypeAction`: `{"type": "TypeAction", "selector": "...", "text": "..."}`
  - `ScrollAction`: `{"type": "ScrollAction", "down": true}`
  - etc.

---

## 🔄 Flujo de Evaluación

```
┌─────────────────────────────────────────────────┐
│ 1. Benchmark inicia evaluación                  │
│    evaluator.reset() → Navega a task.url       │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 2. Captura snapshot del browser                 │
│    snapshot_html = página HTML actual           │
│    url = URL actual                             │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 3. Llama al agente HTTP                         │
│    POST http://localhost:5000/act               │
│    {                                             │
│      "prompt": "...",                            │
│      "snapshot_html": "...",                     │
│      "url": "...",                               │
│      "step_index": 0                             │
│    }                                             │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 4. Agente decide acciones                       │
│    Analiza el HTML y devuelve:                  │
│    {"actions": [action1, action2, ...]}         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 5. Benchmark ejecuta TODAS las acciones         │
│    for action in actions:                       │
│        evaluator.step(action)                   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 6. ¿Tarea completada?                           │
│    Sí → Fin (score calculado)                  │
│    No → Volver al paso 2                        │
└─────────────────────────────────────────────────┘
```

---

## 💡 Ejemplo Completo

Incluimos un agente de ejemplo en: `example_http_agent.py`

### Ejecutar el ejemplo:

```bash
# Terminal 1: Ejecutar el agente
cd autoppia_iwa/autoppia_iwa/entrypoints/benchmark
python example_http_agent.py

# Terminal 2: Ejecutar el benchmark
# (después de configurar AGENTS en run_stateful.py)
cd autoppia_iwa
python -m autoppia_iwa.entrypoints.benchmark.run_stateful
```

---

## 🆚 Comparación: Concurrent vs Stateful

| Aspecto | Concurrent | Stateful |
|---------|-----------|----------|
| **Tipo de agente** | Objeto Python | Servidor HTTP |
| **Interfaz** | `solve_task()` | `POST /act` |
| **Decisión** | Una vez (todas las acciones) | Paso a paso (iterativo) |
| **Feedback** | Solo al final | Después de cada paso |
| **Uso típico** | Planificadores | Agentes adaptativos/HTTP |
| **Subnet compatible** | ❌ No | ✅ Sí (idéntico) |

---

## ⚠️ Errores Comunes

### Error: "agent does not have 'act' method"

```
❌ Modo stateful requiere agente HTTP con endpoint /act.
El agente 'FixedAutobooksAgent' no es un ApifiedWebCUA.
```

**Solución:** Usa `ApifiedWebCUA` en lugar de agentes Python locales:

```python
# ❌ Incorrecto (agente Python local)
AGENTS = [FixedAutobooksAgent(id="1")]

# ✅ Correcto (agente HTTP)
AGENTS = [ApifiedWebCUA(base_url="http://localhost:5000", id="1")]
```

### Error: Connection refused

```
Failed to connect to http://localhost:5000/act
```

**Solución:** Asegúrate de que el agente HTTP esté corriendo:

```bash
# En otra terminal, ejecutar:
python my_agent.py
```

---

## 📚 Más Información

- Ver código de la subnet: `autoppia_web_agents_subnet/validator/evaluation/stateful_cua_eval.py`
- Ver cliente HTTP: `autoppia_iwa/src/web_agents/cua/apified_cua.py`
- Documentación completa: `EVALUATOR_REFACTOR.md`
