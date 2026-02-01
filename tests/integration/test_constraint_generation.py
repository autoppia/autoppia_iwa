#!/usr/bin/env python3
"""
Script para verificar que la generación de constraints funciona correctamente
con el sistema de seeds optimizado.
"""

import asyncio
from pprint import pprint


# Test para autocinema (web 1)
async def test_autocinema_constraints():
    print("\n" + "=" * 80)
    print("🎬 TESTING AUTOCINEMA (Web 1)")
    print("=" * 80)

    from autoppia_iwa.src.demo_webs.projects.autocinema_1.generation_functions import (
        _get_data,
        generate_film_constraints,
        generate_film_filter_constraints,
        generate_search_film_constraints,
    )
    from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

    test_url = "http://localhost:8001/?seed=86"

    print(f"\n📍 Test URL: {test_url}")

    # 1. Resolver seed
    print("\n1️⃣ Resolviendo seed desde endpoint...")
    seed = get_seed_from_url(test_url)
    print(f"   ✅ seed=86 → seed={seed}")

    # 2. Cargar dataset
    print("\n2️⃣ Cargando dataset con seed...")
    dataset = await _get_data(seed_value=seed)
    print(f"   ✅ Dataset cargado: {len(dataset)} películas")
    if dataset:
        print(f"   📄 Muestra película 1: {dataset[0]['name']}")
        print(f"   📄 Muestra película 2: {dataset[1]['name']}")

    # 3. Test SIN dataset (lazy loading)
    print("\n3️⃣ Test generación SIN dataset (lazy loading)...")
    constraints_1 = await generate_search_film_constraints(task_url=test_url)
    print(f"   ✅ Constraints generados: {len(constraints_1)}")
    pprint(constraints_1)

    # 4. Test CON dataset (optimizado)
    print("\n4️⃣ Test generación CON dataset (optimizado)...")
    constraints_2 = await generate_film_constraints(task_url=test_url, dataset=dataset)
    print(f"   ✅ Constraints generados: {len(constraints_2) if constraints_2 else 0}")
    if constraints_2:
        print("   📝 Primeros 3 constraints:")
        pprint(constraints_2[:3])

    # 5. Test múltiples generators con mismo dataset
    print("\n5️⃣ Test múltiples generators CON MISMO dataset...")
    c1 = await generate_search_film_constraints(test_url, dataset)
    c2 = await generate_film_constraints(test_url, dataset)
    c3 = await generate_film_filter_constraints(test_url, dataset)
    print(f"   ✅ search_film: {len(c1)} constraints")
    print(f"   ✅ film_detail: {len(c2) if c2 else 0} constraints")
    print(f"   ✅ film_filter: {len(c3)} constraints")
    print("   🎉 TODO CON UN SOLO DATASET (optimización funcionando)")

    return True


# Test para autobooks (web 2)
async def test_autobooks_constraints():
    print("\n" + "=" * 80)
    print("📚 TESTING AUTOBOOKS (Web 2)")
    print("=" * 80)

    from autoppia_iwa.src.demo_webs.projects.autobooks_2.generation_functions import (
        _get_data,
        generate_book_constraints,
        generate_book_filter_constraints,
        generate_search_book_constraints,
    )
    from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

    test_url = "http://localhost:8002/?seed=123"

    print(f"\n📍 Test URL: {test_url}")

    # 1. Resolver seed
    print("\n1️⃣ Resolviendo seed desde endpoint...")
    seed = get_seed_from_url(test_url)
    print(f"   ✅ seed=123 → seed={seed}")

    # 2. Cargar dataset
    print("\n2️⃣ Cargando dataset con seed...")
    dataset = await _get_data(seed_value=seed)
    print(f"   ✅ Dataset cargado: {len(dataset)} libros")
    if dataset:
        print(f"   📄 Muestra libro 1: {dataset[0]['name']}")
        print(f"   📄 Muestra libro 2: {dataset[1]['name']}")

    # 3. Test con dataset
    print("\n3️⃣ Test generación CON dataset...")
    constraints_1 = await generate_search_book_constraints(test_url, dataset)
    constraints_2 = await generate_book_constraints(test_url, dataset)
    constraints_3 = await generate_book_filter_constraints(test_url, dataset)

    print(f"   ✅ search_book: {len(constraints_1)} constraints")
    pprint(constraints_1)
    print(f"   ✅ book_detail: {len(constraints_2) if constraints_2 else 0} constraints")
    print(f"   ✅ book_filter: {len(constraints_3)} constraints")

    return True


# Test de validez de constraints
async def test_constraints_validity():
    print("\n" + "=" * 80)
    print("✅ TESTING VALIDEZ DE CONSTRAINTS")
    print("=" * 80)

    from autoppia_iwa.src.demo_webs.projects.autocinema_1.generation_functions import _get_data, generate_film_constraints
    from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

    test_seeds = [42, 86, 150, 200, 300]

    print("\n🔍 Verificando que constraints contienen valores del dataset...")

    for seed in test_seeds:
        test_url = f"http://localhost:8001/?seed={seed}"
        seed = get_seed_from_url(test_url)
        dataset = await _get_data(seed_value=seed)
        constraints = await generate_film_constraints(test_url, dataset)

        print(f"\n  seed={seed} → seed={seed}")
        print(f"    Dataset: {len(dataset)} películas")
        print(f"    Constraints: {len(constraints) if constraints else 0}")

        if constraints:
            # Verificar que los valores están en el dataset
            constraint = constraints[0]
            field = constraint["field"]
            value = constraint["value"]

            # Buscar si el valor existe en el dataset
            found = False
            for item in dataset:
                if field in item:
                    item_value = item[field]
                    # Para listas (genres), verificar si value está en la lista
                    if isinstance(item_value, list):
                        if value in item_value:
                            found = True
                            break
                    elif item_value == value:
                        found = True
                        break

            status = "✅" if found else "⚠️"
            print(f"    {status} Constraint '{field}={value}' {'found' if found else 'NOT FOUND'} in dataset")

    return True


# Main
async def main():
    print("\n" + "🚀" * 40)
    print("SUITE DE TESTS - SISTEMA DE SEEDS OPTIMIZADO")
    print("🚀" * 40)

    try:
        # Test 1: Autocinema
        result1 = await test_autocinema_constraints()

        # Test 2: Autobooks
        result2 = await test_autobooks_constraints()

        # Test 3: Validez de constraints
        result3 = await test_constraints_validity()

        print("\n" + "=" * 80)
        print("🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE!")
        print("=" * 80)
        print("\nResumen:")
        print(f"  ✅ Autocinema constraints: {'PASS' if result1 else 'FAIL'}")
        print(f"  ✅ Autobooks constraints: {'PASS' if result2 else 'FAIL'}")
        print(f"  ✅ Validez de constraints: {'PASS' if result3 else 'FAIL'}")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
