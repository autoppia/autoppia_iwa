"""
Evaluador Concurrente - ConcurrentEvaluator

Este evaluador recibe una TaskSolution completa con todas las acciones ya generadas
y las ejecuta de forma secuencial en el navegador.

Uso:
    from autoppia_iwa.src.evaluation.concurrent_evaluator import ConcurrentEvaluator

    evaluator = ConcurrentEvaluator(web_project=project, config=config)
    result = await evaluator.evaluate_single_task_solution(task, task_solution)

Características:
- Recibe todas las acciones de una vez
- Agrupa soluciones idénticas para optimizar
- Soporta evaluación de múltiples soluciones en paralelo
- Genera GIFs de las ejecuciones
"""

from autoppia_iwa.src.evaluation.concurrent_evaluator.evaluator import ConcurrentEvaluator

__all__ = ["ConcurrentEvaluator"]
