"""
Evaluador Iterativo - IterativeEvaluator

Este evaluador funciona como un agente, llamando iterativamente al agente
para generar acciones una por una basándose en el estado actual del navegador.

Uso:
    from autoppia_iwa.src.evaluation.iterative_evaluator import IterativeEvaluator
    
    evaluator = IterativeEvaluator(web_project=project, config=config)
    result = await evaluator.evaluate_with_agent(task, agent, max_iterations=50)

Características:
- Llama al agente de forma iterativa
- Ejecuta una acción a la vez
- Enriquece el task con el estado actual del browser
- El agente puede adaptar su estrategia basándose en el estado
- Genera GIFs de las ejecuciones
"""

from autoppia_iwa.src.evaluation.iterative_evaluator.evaluator import IterativeEvaluator

__all__ = ["IterativeEvaluator"]
