"""
Ejemplo de agente HTTP para modo stateful del benchmark.

Este agente expone el endpoint /act que el benchmark llama en cada iteración.

Para ejecutarlo:
    python example_http_agent.py

Luego, en run_stateful.py configura:
    AGENTS = [
        ApifiedWebCUA(base_url="http://localhost:5000", id="1", name="ExampleAgent"),
    ]
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn

app = FastAPI()


class ActRequest(BaseModel):
    task_id: str | None = None
    prompt: str | None = None
    url: str
    snapshot_html: str
    step_index: int
    web_project_id: str | None = None


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/act")
async def act(request: ActRequest) -> Dict[str, List[Dict[str, Any]]]:
    """
    Endpoint /act que recibe el estado del browser y devuelve acciones.
    
    Este es un ejemplo simple que siempre devuelve una acción de navegación.
    En un agente real, aquí iría tu lógica de decisión basada en:
    - request.prompt: La tarea a realizar
    - request.snapshot_html: El HTML actual del browser
    - request.url: La URL actual
    - request.step_index: El número de iteración
    """
    
    print(f"\n{'='*80}")
    print(f"[ACT] Step {request.step_index}")
    print(f"  Task: {request.prompt}")
    print(f"  URL: {request.url}")
    print(f"  HTML length: {len(request.snapshot_html)} chars")
    print(f"{'='*80}\n")
    
    # Ejemplo simple: devolver una acción de navegación
    # En un agente real, analizarías el HTML y decidirías qué hacer
    actions = [
        {
            "type": "NavigateAction",
            "url": request.url,
        }
    ]
    
    # Puedes devolver múltiples acciones (se ejecutan en batch)
    # actions = [
    #     {"type": "ClickAction", "selector": "#login"},
    #     {"type": "TypeAction", "selector": "#username", "text": "user"},
    #     {"type": "TypeAction", "selector": "#password", "text": "pass"},
    #     {"type": "ClickAction", "selector": "#submit"},
    # ]
    
    return {"actions": actions}


if __name__ == "__main__":
    print("="*80)
    print("🚀 Iniciando agente HTTP de ejemplo")
    print("="*80)
    print("El agente estará disponible en: http://localhost:5000")
    print("Endpoints:")
    print("  - GET  /health  → Health check")
    print("  - POST /act     → Recibe estado y devuelve acciones")
    print("="*80)
    print("\nPara usar este agente en el benchmark, configura en run_stateful.py:")
    print('  AGENTS = [')
    print('      ApifiedWebCUA(base_url="http://localhost:5000", id="1", name="ExampleAgent"),')
    print('  ]')
    print("="*80)
    
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
