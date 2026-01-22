#!/usr/bin/env python3
"""
Test de generación completa de tasks para verificar que tienen sentido.
"""

import asyncio
import json


async def test_full_task_generation():
    print("\n" + "=" * 80)
    print("📝 TESTING GENERACIÓN COMPLETA DE TASKS")
    print("=" * 80)

    from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
    from autoppia_iwa.src.data_generation.domain.classes import TaskGenerationConfig
    from autoppia_iwa.src.demo_webs.projects.autocinema_1.main import cinema_project
    from autoppia_iwa.src.evaluation.evaluator.utils import extract_seed_from_url

    print("\n1️⃣ Configurando pipeline...")
    config = TaskGenerationConfig(
        prompts_per_use_case=2,
        use_cases=["FILM_DETAIL", "SEARCH_FILM", "FILTER_FILM"],
        dynamic=True,  # ✅ Modo dinámico
    )

    pipeline = TaskGenerationPipeline(web_project=cinema_project, config=config)

    print("\n2️⃣ Generando tasks...")
    tasks = await pipeline.generate()

    print(f"\n✅ Tasks generadas: {len(tasks)}")

    # Analizar cada task
    tasks_analysis = []

    for i, task in enumerate(tasks, 1):
        print(f"\n{'=' * 80}")
        print(f"Task #{i} - {task.use_case.name}")
        print(f"{'=' * 80}")
        print(f"📍 URL: {task.url}")
        print(f"🎯 Prompt:\n{task.prompt}\n")

        if task.use_case.constraints:
            print(f"📊 Constraints ({len(task.use_case.constraints)}):")
            for c in task.use_case.constraints:
                print(f"  • {c['field']} {c['operator']} {c['value']}")

        if task.tests:
            print(f"\n🧪 Tests: {len(task.tests)}")
            for test in task.tests:
                test_type = test.type if hasattr(test, "type") else "Unknown"
                event_name = test.event_name if hasattr(test, "event_name") else ""
                print(f"  • {test_type}: {event_name}")

        print(f"🔄 Dynamic: {task.dynamic}")

        # Extraer seed
        seed = extract_seed_from_url(task.url)
        print(f"🔑 Seed en URL: {seed}")

        # Guardar análisis
        analysis = {
            "id": task.id,
            "use_case": task.use_case.name,
            "url": task.url,
            "seed": seed,
            "prompt": task.prompt,
            "constraints": task.use_case.constraints,
            "num_tests": len(task.tests),
            "dynamic": task.dynamic,
        }
        tasks_analysis.append(analysis)

    # Verificar que todas tienen seed
    print("\n3️⃣ Verificando seeds en URLs...")
    seeds_found = []
    for task in tasks:
        seed = extract_seed_from_url(task.url)
        seeds_found.append(seed)
        if seed is None:
            print(f"   ❌ Task {task.id[:8]} NO tiene seed!")
        else:
            print(f"   ✅ Task {task.id[:8]}: seed={seed}")

    if all(s is not None for s in seeds_found):
        print(f"\n🎉 TODAS las {len(tasks)} tasks tienen seed correcto!")
    else:
        print(f"\n⚠️ {sum(1 for s in seeds_found if s is None)} tasks NO tienen seed!")

    # Verificar que todas tienen tests
    print("\n4️⃣ Verificando tests...")
    for task in tasks:
        if not task.tests:
            print(f"   ⚠️ Task {task.id[:8]} NO tiene tests")
        else:
            print(f"   ✅ Task {task.id[:8]}: {len(task.tests)} tests")

    # Guardar análisis a JSON
    output_file = "generated_tasks_analysis.json"
    with open(output_file, "w") as f:
        json.dump(tasks_analysis, f, indent=2, default=str)

    print(f"\n✅ Análisis guardado en: {output_file}")

    return tasks


async def test_autobooks_tasks():
    print("\n" + "=" * 80)
    print("📚 TESTING GENERACIÓN DE TASKS AUTOBOOKS")
    print("=" * 80)

    from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
    from autoppia_iwa.src.data_generation.domain.classes import TaskGenerationConfig
    from autoppia_iwa.src.demo_webs.projects.autobooks_2.main import books_project
    from autoppia_iwa.src.evaluation.evaluator.utils import extract_seed_from_url

    config = TaskGenerationConfig(
        prompts_per_use_case=2,
        use_cases=["BOOK_DETAIL", "SEARCH_BOOK"],
        dynamic=True,
    )

    pipeline = TaskGenerationPipeline(web_project=books_project, config=config)
    tasks = await pipeline.generate()

    print(f"\n✅ Tasks generadas: {len(tasks)}")

    for i, task in enumerate(tasks[:3], 1):  # Primeras 3
        print(f"\nTask #{i}:")
        print(f"  URL: {task.url}")
        print(f"  Seed: {extract_seed_from_url(task.url)}")
        print(f"  Use case: {task.use_case.name}")
        print(f"  Prompt: {task.prompt[:80]}...")

    return tasks


# Main
async def main():
    print("\n" + "🧪" * 40)
    print("SUITE DE TESTS - GENERACIÓN Y VALIDACIÓN DE TASKS")
    print("🧪" * 40)

    try:
        # Test 1: Guard de validación
        from test_seed_guard import test_seed_guard

        guard_ok = await test_seed_guard()

        # Test 2: Generación autocinema
        tasks_cinema = await test_full_task_generation()

        # Test 3: Generación autobooks
        tasks_books = await test_autobooks_tasks()

        print("\n" + "=" * 80)
        print("🎉 SUITE COMPLETA EJECUTADA!")
        print("=" * 80)
        print(f"\n✅ Guard validation: {'PASS' if guard_ok else 'FAIL'}")
        print(f"✅ Autocinema tasks: {len(tasks_cinema)} generadas")
        print(f"✅ Autobooks tasks: {len(tasks_books)} generadas")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
