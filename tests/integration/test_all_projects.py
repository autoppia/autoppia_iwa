#!/usr/bin/env python3
"""
Test rápido para verificar que TODOS los 15 proyectos tienen get_seed_from_url.
"""

import asyncio
import json


async def test_all_projects_have_optimization():
    print("\n" + "=" * 80)
    print("🔍 VERIFICANDO QUE TODOS LOS 15 PROYECTOS ESTÁN ACTUALIZADOS")
    print("=" * 80)

    projects = [
        ("autocinema_1", "movies"),
        ("autobooks_2", "books"),
        ("autozone_3", "products"),
        ("autodining_4", "restaurants"),
        ("autocrm_5", "clients"),
        ("automail_6", "emails"),
        ("autodelivery_7", "restaurants"),
        ("autolodge_8", "hotels"),
        ("autoconnect_9", "connections"),
        ("autowork_10", "experts"),
        ("autocalendar_11", "events"),
        ("autolist_12", "tasks"),
        ("autodrive_13", "trips"),
        ("autohealth_14", "health"),
        ("autostats_15", "stats"),
    ]

    results = []

    for project_name, _entity_type in projects:
        print(f"\n{'─' * 80}")
        print(f"📦 Proyecto: {project_name}")

        try:
            # Importar el módulo de generation_functions
            module_path = f"autoppia_iwa.src.demo_webs.projects.{project_name}.generation_functions"
            import importlib

            gen_module = importlib.import_module(module_path)

            # Verificar que importa get_seed_from_url
            import inspect

            source = inspect.getsource(gen_module)

            has_resolve = "get_seed_from_url" in source
            has_old_extract = "extract_seed_from_url" in source and "from autoppia_iwa.src.demo_webs.data_provider import extract_seed_from_url" in source

            # Verificar funciones con dataset parameter
            dataset_functions = []
            for name, obj in inspect.getmembers(gen_module, inspect.isfunction):
                if name.startswith("generate_") and name.endswith("_constraints"):
                    sig = inspect.signature(obj)
                    if "dataset" in sig.parameters:
                        dataset_functions.append(name)

            print(f"   ✅ Usa get_seed_from_url: {has_resolve}")
            print(f"   {'❌' if has_old_extract else '✅'} Usa extract_seed_from_url (obsoleto): {has_old_extract}")
            print(f"   ✅ Funciones con dataset param: {len(dataset_functions)}")
            for func_name in dataset_functions[:3]:  # Mostrar primeras 3
                print(f"      • {func_name}")

            status = "✅" if (has_resolve and not has_old_extract and len(dataset_functions) > 0) else "⚠️"

            results.append(
                {
                    "project": project_name,
                    "status": "OK" if status == "✅" else "NEEDS_UPDATE",
                    "has_resolve": has_resolve,
                    "has_old_extract": has_old_extract,
                    "dataset_functions": len(dataset_functions),
                }
            )

            print(f"   {status} Estado: {'OK' if status == '✅' else 'NEEDS UPDATE'}")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({"project": project_name, "status": "ERROR", "error": str(e)})

    # Resumen
    print("\n" + "=" * 80)
    print("📊 RESUMEN")
    print("=" * 80)

    ok_count = sum(1 for r in results if r["status"] == "OK")
    needs_update = sum(1 for r in results if r["status"] == "NEEDS_UPDATE")
    error_count = sum(1 for r in results if r["status"] == "ERROR")

    print(f"\n✅ Proyectos OK: {ok_count}/15")
    print(f"⚠️ Proyectos que necesitan actualización: {needs_update}/15")
    print(f"❌ Proyectos con error: {error_count}/15")

    if needs_update > 0:
        print("\n⚠️ Proyectos que necesitan actualización:")
        for r in results:
            if r["status"] == "NEEDS_UPDATE":
                print(f"   • {r['project']}")
                if not r.get("has_resolve"):
                    print("     - Falta get_seed_from_url")
                if r.get("has_old_extract"):
                    print("     - Usa extract_seed_from_url obsoleto")
                if r.get("dataset_functions", 0) == 0:
                    print("     - Ninguna función acepta dataset parameter")

    # Guardar resultados en outputs/
    from pathlib import Path

    output_file = Path(__file__).parents[2] / "outputs" / "projects_status.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Resultados guardados en: {output_file}")

    return ok_count == 15


if __name__ == "__main__":
    success = asyncio.run(test_all_projects_have_optimization())
    if success:
        print("\n🎉 TODOS LOS 15 PROYECTOS ESTÁN CORRECTAMENTE ACTUALIZADOS!")
    else:
        print("\n⚠️ Algunos proyectos necesitan actualización")
    exit(0 if success else 1)
