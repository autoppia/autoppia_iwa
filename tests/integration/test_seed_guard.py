#!/usr/bin/env python3
"""
Test para verificar que el guard de validación de seeds funciona correctamente.
"""

import asyncio


async def test_seed_guard():
    print("\n" + "=" * 80)
    print("🛡️ TESTING SEED GUARD (Validación de NavigateActions)")
    print("=" * 80)

    from autoppia_iwa.src.evaluation.shared.utils import extract_seed_from_url
    from autoppia_iwa.src.execution.actions.actions import ClickAction, NavigateAction
    from autoppia_iwa.src.execution.actions.base import Selector, SelectorType

    # Crear una task de prueba
    task_url = "http://localhost:8001/?seed=86"
    assigned_seed = extract_seed_from_url(task_url)

    print(f"\n📍 Task URL: {task_url}")
    print(f"🔑 Seed asignado: {assigned_seed}")

    # Test 1: Actions CORRECTAS (mismo seed)
    print("\n" + "─" * 80)
    print("1️⃣ Test: Actions con seed CORRECTO")
    print("─" * 80)

    actions_correct = [
        ClickAction(selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="movie-1")),
        NavigateAction(url="http://localhost:8001/details?seed=86"),  # ✅ Seed 86
        ClickAction(selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="add-cart")),
        NavigateAction(url="http://localhost:8001/cart?seed=86"),  # ✅ Seed 86
    ]

    violation = False
    for action in actions_correct:
        if isinstance(action, NavigateAction) and action.url:
            nav_seed = extract_seed_from_url(action.url)
            print(f"   NavigateAction: {action.url}")
            print(f"     Seed extraído: {nav_seed}")
            if nav_seed is None or nav_seed != assigned_seed:
                violation = True
                print(f"     ❌ VIOLATION: Expected {assigned_seed}, got {nav_seed}")
                break
            else:
                print("     ✅ OK: Seed correcto")

    if violation:
        print("\n   ❌ GUARD detectó violación (NO debería pasar)")
        return False
    else:
        print("\n   ✅ Sin violación - Guard pasaría correctamente")

    # Test 2: Actions INCORRECTAS (seed diferente)
    print("\n" + "─" * 80)
    print("2️⃣ Test: Actions con seed INCORRECTO (trampa detectada)")
    print("─" * 80)

    actions_wrong = [
        ClickAction(selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="movie-1")),
        NavigateAction(url="http://localhost:8001/details?seed=999"),  # ❌ Seed 999 ≠ 86
        ClickAction(selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="known-element")),
    ]

    violation = False
    for action in actions_wrong:
        if isinstance(action, NavigateAction) and action.url:
            nav_seed = extract_seed_from_url(action.url)
            print(f"   NavigateAction: {action.url}")
            print(f"     Seed extraído: {nav_seed}")
            if nav_seed is None or nav_seed != assigned_seed:
                violation = True
                print(f"     🚨 VIOLATION DETECTADA: Expected {assigned_seed}, got {nav_seed}")
                break

    if violation:
        print("\n   ✅ VIOLATION DETECTADA correctamente - Guard funcionando!")
    else:
        print("\n   ❌ NO detectó violación (ERROR EN GUARD)")
        return False

    # Test 3: Actions sin seed
    print("\n" + "─" * 80)
    print("3️⃣ Test: Actions SIN seed en URL")
    print("─" * 80)

    actions_no_seed = [
        ClickAction(selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="movie-1")),
        NavigateAction(url="http://localhost:8001/details"),  # ❌ Sin seed
        ClickAction(selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="add-cart")),
    ]

    violation = False
    for action in actions_no_seed:
        if isinstance(action, NavigateAction) and action.url:
            nav_seed = extract_seed_from_url(action.url)
            print(f"   NavigateAction: {action.url}")
            print(f"     Seed extraído: {nav_seed}")
            if nav_seed is None or nav_seed != assigned_seed:
                violation = True
                print(f"     🚨 VIOLATION DETECTADA: Expected {assigned_seed}, got None")
                break

    if violation:
        print("\n   ✅ VIOLATION DETECTADA correctamente - Guard funcionando!")
    else:
        print("\n   ❌ NO detectó violación (ERROR EN GUARD)")
        return False

    # Test 4: Multiple NavigateActions con seeds mixtos
    print("\n" + "─" * 80)
    print("4️⃣ Test: Multiple NavigateActions con seeds mixtos")
    print("─" * 80)

    actions_mixed = [
        NavigateAction(url="http://localhost:8001/home?seed=86"),  # ✅ OK
        ClickAction(selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="filter")),
        NavigateAction(url="http://localhost:8001/search?seed=86"),  # ✅ OK
        ClickAction(selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="movie-1")),
        NavigateAction(url="http://localhost:8001/details?seed=200"),  # ❌ Diferente!
    ]

    violation = False
    for i, action in enumerate(actions_mixed, 1):
        if isinstance(action, NavigateAction) and action.url:
            nav_seed = extract_seed_from_url(action.url)
            print(f"   Action {i} - NavigateAction: seed={nav_seed}")
            if nav_seed is None or nav_seed != assigned_seed:
                violation = True
                print(f"     🚨 VIOLATION: Expected {assigned_seed}, got {nav_seed}")
                break

    if violation:
        print("\n   ✅ VIOLATION DETECTADA en action múltiple - Guard funcionando!")
    else:
        print("\n   ❌ NO detectó violación (ERROR EN GUARD)")
        return False

    print("\n" + "=" * 80)
    print("🛡️ SEED GUARD TEST COMPLETADO - TODO CORRECTO!")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = asyncio.run(test_seed_guard())
    exit(0 if success else 1)
