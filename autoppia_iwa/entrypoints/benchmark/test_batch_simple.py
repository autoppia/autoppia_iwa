"""
Test simple para verificar que el IterativeEvaluator ejecuta múltiples acciones.
"""

import asyncio
from autoppia_iwa.src.data_generation.tasks.classes import Task, BrowserSpecification
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.iterative_evaluator import IterativeEvaluator
from autoppia_iwa.src.web_agents.test_batch_agent import BatchTestAgent, SingleActionAgent

# Buscar proyecto autobooks
project = next((p for p in demo_web_projects if p.id == "autobooks"), None)

# Crear una task simple
task = Task(
    id="test_batch",
    prompt="Navigate to the homepage",
    url="http://localhost:8001/",
    specifications=BrowserSpecification(),
    tests=[],
    is_web_real=False,
    web_project_id="autobooks"
)

async def test_batch_agent():
    print("\n" + "="*80)
    print("🧪 TEST: BatchTestAgent (devuelve 3, 2, 1 acciones)")
    print("="*80 + "\n")
    
    config = EvaluatorConfig(
        should_record_gif=False,
        verbose_logging=True,
        debug_mode=True,
    )
    
    evaluator = IterativeEvaluator(web_project=project, config=config)
    agent = BatchTestAgent(id="batch_test", name="Batch Test Agent")
    
    result = await evaluator.evaluate_with_agent(task, agent, max_iterations=10)
    
    print("\n" + "-"*80)
    print(f"✅ RESULTADO:")
    print(f"   • Acciones ejecutadas: {result.stats.action_count}")
    print(f"   • Tiempo total: {result.evaluation_time:.2f}s")
    print("-"*80 + "\n")
    
    return result

async def test_single_agent():
    print("\n" + "="*80)
    print("🧪 TEST: SingleActionAgent (devuelve 1 acción cada vez)")
    print("="*80 + "\n")
    
    config = EvaluatorConfig(
        should_record_gif=False,
        verbose_logging=True,
        debug_mode=True,
    )
    
    evaluator = IterativeEvaluator(web_project=project, config=config)
    agent = SingleActionAgent(id="single_action", name="Single Action Agent")
    
    result = await evaluator.evaluate_with_agent(task, agent, max_iterations=10)
    
    print("\n" + "-"*80)
    print(f"✅ RESULTADO:")
    print(f"   • Acciones ejecutadas: {result.stats.action_count}")
    print(f"   • Tiempo total: {result.evaluation_time:.2f}s")
    print("-"*80 + "\n")
    
    return result

async def main():
    print("\n" + "🔷"*40)
    print("PRUEBA DE ITERATIVE EVALUATOR MEJORADO")
    print("🔷"*40)
    
    # Test 1: Batch agent
    result1 = await test_batch_agent()
    
    # Test 2: Single action agent
    result2 = await test_single_agent()
    
    print("\n" + "="*80)
    print("📊 COMPARACIÓN DE RESULTADOS")
    print("="*80)
    print(f"BatchTestAgent:       {result1.stats.action_count} acciones")
    print(f"SingleActionAgent:    {result2.stats.action_count} acciones")
    print("\n💡 Ambos deberían ejecutar 6 acciones, pero BatchTestAgent lo hace")
    print("   en menos llamadas al agente (más eficiente).")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
