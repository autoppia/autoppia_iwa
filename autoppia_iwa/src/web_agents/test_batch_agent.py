"""
Agente de prueba que envía múltiples acciones en batch para verificar
el comportamiento mejorado del IterativeEvaluator.
"""

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import NavigateAction, ClickAction
from autoppia_iwa.src.web_agents.classes import IWebAgent, TaskSolution


class BatchTestAgent(IWebAgent):
    """
    Agente que devuelve múltiples acciones en cada llamada para probar
    que el IterativeEvaluator las ejecuta todas.
    """

    def __init__(self, id: str = "batch_test", name: str = "Batch Test Agent"):
        self.id = id
        self.name = name
        self.call_count = 0

    async def solve_task(self, task: Task) -> TaskSolution:
        self.call_count += 1
        
        browser_state = task.relevant_data.get("browser_state", {})
        current_url = browser_state.get("current_url", "unknown")
        
        print(f"\n🔢 AGENT CALL #{self.call_count}")
        print(f"   📍 Current URL: {current_url}")
        
        # Según la llamada, devolver diferentes batches de acciones
        if self.call_count == 1:
            # Primera llamada: devolver 3 acciones (todas Navigate para evitar errores)
            actions = [
                NavigateAction(url="http://localhost:8001/books"),
                NavigateAction(url="http://localhost:8001/authors"),
                NavigateAction(url="http://localhost:8001/contact"),
            ]
            print(f"   📤 Returning {len(actions)} actions: [Navigate, Navigate, Navigate]")
            
        elif self.call_count == 2:
            # Segunda llamada: devolver 2 acciones
            actions = [
                NavigateAction(url="http://localhost:8001/register"),
                NavigateAction(url="http://localhost:8001/login"),
            ]
            print(f"   📤 Returning {len(actions)} actions: [Navigate, Navigate]")
            
        elif self.call_count == 3:
            # Tercera llamada: devolver 1 acción
            actions = [
                NavigateAction(url="http://localhost:8001/"),
            ]
            print(f"   📤 Returning {len(actions)} actions: [Navigate]")
            
        else:
            # Cuarta llamada en adelante: terminar
            actions = []
            print(f"   ✅ Returning 0 actions - FINISHED")
        
        return TaskSolution(
            task_id=task.id,
            actions=actions,
            web_agent_id=self.id
        )


class SingleActionAgent(IWebAgent):
    """
    Agente que devuelve solo UNA acción en cada llamada (comportamiento tradicional).
    """

    def __init__(self, id: str = "single_action", name: str = "Single Action Agent"):
        self.id = id
        self.name = name
        self.call_count = 0

    async def solve_task(self, task: Task) -> TaskSolution:
        self.call_count += 1
        
        print(f"\n🔢 AGENT CALL #{self.call_count}")
        
        # Devolver siempre 1 acción hasta llegar a 6
        if self.call_count <= 6:
            actions = [
                NavigateAction(url=f"http://localhost:8001/page{self.call_count}"),
            ]
            print(f"   📤 Returning 1 action: [Navigate to page{self.call_count}]")
        else:
            actions = []
            print(f"   ✅ Returning 0 actions - FINISHED")
        
        return TaskSolution(
            task_id=task.id,
            actions=actions,
            web_agent_id=self.id
        )
