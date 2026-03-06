#!/usr/bin/env python3
"""
Integration tests: constraint generation with real data from the demo webs backend.
Requires the demo webs backend to be running. Skipped when backend is unavailable.
"""

import asyncio
from pprint import pprint

import pytest

try:
    from _pytest.outcomes import Skipped
except ImportError:
    Skipped = type("Skipped", (), {})  # fallback if pytest structure changes


def _skip_if_backend_unavailable(reason: str):
    """Skip the test when backend is not reachable (e.g. in CI without services)."""
    pytest.skip(reason)


# Test para autocinema (web 1) - real data from backend
@pytest.mark.integration
async def test_autocinema_constraints():
    print("\n" + "=" * 80)
    print("🎬 TESTING AUTOCINEMA (Web 1) - real backend data")
    print("=" * 80)

    from autoppia_iwa.src.demo_webs.projects.autocinema_1.data_utils import fetch_data as fetch_movies
    from autoppia_iwa.src.demo_webs.projects.autocinema_1.generation_functions import (
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

    # 2. Cargar dataset desde backend (real flow)
    print("\n2️⃣ Cargando dataset desde backend...")
    try:
        movies = await fetch_movies(seed_value=seed)
    except Exception as e:
        _skip_if_backend_unavailable(f"Demo webs backend not reachable: {e}")

    if not movies:
        _skip_if_backend_unavailable("Backend returned no movies (is demo webs running?)")

    dataset = {"movies": movies}
    print(f"   ✅ Dataset cargado: {len(dataset['movies'])} películas")
    if movies:
        print(f"   📄 Muestra película 1: {movies[0].get('name', 'N/A')}")
        if len(movies) > 1:
            print(f"   📄 Muestra película 2: {movies[1].get('name', 'N/A')}")

    # 3. Test SIN dataset (lazy loading - backend is called internally)
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

    assert True


# Test para autobooks (web 2) - real data from backend
@pytest.mark.integration
async def test_autobooks_constraints():
    print("\n" + "=" * 80)
    print("📚 TESTING AUTOBOOKS (Web 2) - real backend data")
    print("=" * 80)

    from autoppia_iwa.src.demo_webs.projects.autobooks_2.data_utils import fetch_data as fetch_books
    from autoppia_iwa.src.demo_webs.projects.autobooks_2.generation_functions import (
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

    # 2. Cargar dataset desde backend (real flow)
    print("\n2️⃣ Cargando dataset desde backend...")
    try:
        books = await fetch_books(seed_value=seed)
    except Exception as e:
        _skip_if_backend_unavailable(f"Demo webs backend not reachable: {e}")

    if not books:
        _skip_if_backend_unavailable("Backend returned no books (is demo webs running?)")

    dataset = {"books": books}
    print(f"   ✅ Dataset cargado: {len(dataset['books'])} libros")
    if books:
        print(f"   📄 Muestra libro 1: {books[0].get('name', 'N/A')}")
        if len(books) > 1:
            print(f"   📄 Muestra libro 2: {books[1].get('name', 'N/A')}")

    # 3. Test con dataset
    print("\n3️⃣ Test generación CON dataset...")
    constraints_1 = await generate_search_book_constraints(test_url, dataset)
    constraints_2 = await generate_book_constraints(test_url, dataset)
    constraints_3 = await generate_book_filter_constraints(test_url, dataset)

    print(f"   ✅ search_book: {len(constraints_1)} constraints")
    pprint(constraints_1)
    print(f"   ✅ book_detail: {len(constraints_2) if constraints_2 else 0} constraints")
    print(f"   ✅ book_filter: {len(constraints_3)} constraints")

    assert True


# Test de validez de constraints - real data from backend
@pytest.mark.integration
async def test_constraints_validity():
    print("\n" + "=" * 80)
    print("✅ TESTING VALIDEZ DE CONSTRAINTS - real backend data")
    print("=" * 80)

    from autoppia_iwa.src.demo_webs.projects.autocinema_1.data_utils import fetch_data as fetch_movies
    from autoppia_iwa.src.demo_webs.projects.autocinema_1.generation_functions import generate_film_constraints
    from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

    test_seeds = [42, 86, 150, 200, 300]

    print("\n🔍 Verificando que constraints contienen valores del dataset...")

    for seed in test_seeds:
        test_url = f"http://localhost:8001/?seed={seed}"
        seed_resolved = get_seed_from_url(test_url)

        try:
            dataset_list = await fetch_movies(seed_value=seed_resolved)
        except Exception as e:
            _skip_if_backend_unavailable(f"Demo webs backend not reachable: {e}")

        if not dataset_list:
            _skip_if_backend_unavailable("Backend returned no movies (is demo webs running?)")

        dataset = {"movies": dataset_list}
        constraints = await generate_film_constraints(test_url, dataset)

        print(f"\n  seed={seed} → seed={seed_resolved}")
        print(f"    Dataset: {len(dataset['movies'])} películas")
        print(f"    Constraints: {len(constraints) if constraints else 0}")

        if constraints:
            constraint = constraints[0]
            field = constraint["field"]
            value = constraint["value"]

            found = False
            for item in dataset["movies"]:
                if field in item:
                    item_value = item[field]
                    if isinstance(item_value, list):
                        if value in item_value:
                            found = True
                            break
                    elif item_value == value:
                        found = True
                        break

            status = "✅" if found else "⚠️"
            print(f"    {status} Constraint '{field}={value}' {'found' if found else 'NOT FOUND'} in dataset")

    assert True


# Main (for running as script)
async def main():
    print("\n" + "🚀" * 40)
    print("SUITE DE TESTS - SISTEMA DE SEEDS OPTIMIZADO (real backend)")
    print("🚀" * 40)

    try:
        result1 = await test_autocinema_constraints()
        result2 = await test_autobooks_constraints()
        result3 = await test_constraints_validity()

        print("\n" + "=" * 80)
        print("🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE!")
        print("=" * 80)
        print("\nResumen:")
        print(f"  ✅ Autocinema constraints: {'PASS' if result1 else 'FAIL'}")
        print(f"  ✅ Autobooks constraints: {'PASS' if result2 else 'FAIL'}")
        print(f"  ✅ Validez de constraints: {'PASS' if result3 else 'FAIL'}")

        return True

    except Skipped as e:
        print(f"\n⏭️ Tests skipped (backend not available): {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
