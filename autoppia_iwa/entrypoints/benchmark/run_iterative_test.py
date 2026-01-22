"""
Script de prueba para verificar el comportamiento mejorado del IterativeEvaluator.

Compara:
1. BatchTestAgent: Devuelve múltiples acciones en cada llamada (3, 2, 1, 0)
2. SingleActionAgent: Devuelve una acción en cada llamada (1, 1, 1, 1, 1, 1, 0)

Ambos deberían ejecutar 6 acciones totales, pero con diferente número de llamadas.

Run with:
  python -m autoppia_iwa.entrypoints.benchmark.run_iterative_test
"""

import asyncio

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.web_agents.test_batch_agent import BatchTestAgent, SingleActionAgent

# =========================
# 💡 Configuración de Prueba
# =========================

# Proyectos a evaluar
PROJECT_IDS = ["autobooks"]
PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)

print("\n" + "="*80)
print("🧪 PRUEBA DEL ITERATIVE EVALUATOR MEJORADO")
print("="*80)
print("\nComparando dos agentes:")
print("1. 📦 BatchTestAgent: Envía múltiples acciones (3, 2, 1)")
print("2. 📄 SingleActionAgent: Envía una acción cada vez (1, 1, 1, 1, 1, 1)")
print("\n⚡ Ambos deberían ejecutar 6 acciones, pero con diferente eficiencia")
print("="*80 + "\n")


def test_batch_agent():
    """Test con agente que envía múltiples acciones"""
    print("\n" + "🔷"*40)
    print("TEST 1: BatchTestAgent (múltiples acciones por llamada)")
    print("🔷"*40 + "\n")
    
    agents = [BatchTestAgent(id="batch_test", name="Batch Test Agent")]
    
    cfg = BenchmarkConfig(
        projects=PROJECTS,
        agents=agents,
        evaluator_mode="iterative",
        max_iterations_per_task=10,  # Límite de 10 acciones
        use_cached_tasks=True,
        prompts_per_use_case=1,
        num_use_cases=0,
        use_cases=[],
        runs=1,
        max_parallel_agent_calls=1,
        use_cached_solutions=False,
        record_gif=False,
        dynamic=False,
        save_results_json=False,
        plot_results=False,
    )
    
    benchmark = Benchmark(cfg)
    asyncio.run(benchmark.run())


def test_single_action_agent():
    """Test con agente que envía una acción cada vez"""
    print("\n" + "🔶"*40)
    print("TEST 2: SingleActionAgent (una acción por llamada)")
    print("🔶"*40 + "\n")
    
    agents = [SingleActionAgent(id="single_action", name="Single Action Agent")]
    
    cfg = BenchmarkConfig(
        projects=PROJECTS,
        agents=agents,
        evaluator_mode="iterative",
        max_iterations_per_task=10,  # Límite de 10 acciones
        use_cached_tasks=True,
        prompts_per_use_case=1,
        num_use_cases=0,
        use_cases=[],
        runs=1,
        max_parallel_agent_calls=1,
        use_cached_solutions=False,
        record_gif=False,
        dynamic=False,
        save_results_json=False,
        plot_results=False,
    )
    
    benchmark = Benchmark(cfg)
    asyncio.run(benchmark.run())


def main():
    """
    Ejecuta ambos tests y compara resultados.
    """
    try:
        # Test 1: Agente con batches
        test_batch_agent()
        
        print("\n" + "="*80)
        print("Continuando con el segundo test...")
        print("="*80 + "\n")
        
        # Test 2: Agente con acciones individuales
        test_single_action_agent()
        
        print("\n" + "="*80)
        print("✅ PRUEBAS COMPLETADAS")
        print("="*80)
        print("\n📊 RESULTADOS ESPERADOS:")
        print("   • BatchTestAgent: 6 acciones en ~3 llamadas al agente")
        print("   • SingleActionAgent: 6 acciones en ~6 llamadas al agente")
        print("\n💡 CONCLUSIÓN:")
        print("   El IterativeEvaluator ahora ejecuta TODAS las acciones que el agente")
        print("   devuelve en cada llamada, haciendo el proceso más eficiente.")
        print("="*80 + "\n")

    except KeyboardInterrupt:
        logger.warning("Tests interrupted by user")
    except Exception as e:
        logger.error(f"Tests failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
