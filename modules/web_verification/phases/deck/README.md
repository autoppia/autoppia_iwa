# Web Project Decks

Un *deck* es la especificación fuente de verdad para un web project aportado por la comunidad. Describe exactamente:

1. **Metadatos**: `project_id`, nombre, owners, versión, URLs de referencia y estado (sandbox / mainnet).
2. **Dinámica esperada**: banderas `dynamic_profile` para D1 (HTML), D2 (datos) y D3 (atributos/UI) junto con notas de seeds.
3. **Use cases canónicos**: lista exhaustiva de casos con `name`, `event`, prioridad, etiquetas y expectativas de prompts/pruebas.
4. **Páginas obligatorias**: cada página declara `url_patterns` y `required_elements` (selectores o textos) que deben existir en la UI.
5. **Política de tasks/tests**: límites básicos de dificultad, ejemplos mínimos y notas para generación automática.

## Archivo

- Formato por defecto: JSON.
- Extensión: `.deck.json`.
- Ubicación sugerida: `modules/web_verification/phases/deck/examples/<project_slug>.deck.json` para proyectos incluidos en el repo. En producción se puede apuntar a otra ruta con `--deck`.

> **Nota sobre D2:** la capa D2 (datasets dinámicos) depende del backend y no se manipula desde el verificador; lo que verificamos es que los decks declaren correctamente si la web muta el DOM (D1) o los selectores/atributos (D3) para que el evaluator active esas fases de forma consistente.

## Esquema (simplificado)

```json
{
  "version": "1.0.0",
  "metadata": {
    "project_id": "autocinema",
    "project_name": "Autoppia Cinema",
    "summary": "Portal para gestionar estrenos y reseñas.",
    "owner": "autoppia-core",
    "deck_contact": "deck@autoppia.com",
    "deployment": {
      "preview_base_url": "http://localhost:8000",
      "notes": "Cambiar al dominio final en sandbox"
    }
  },
  "dynamic_profile": {
    "html_mutates": true,
    "data_mutates": true,
    "ui_identifiers_mutate": true,
    "seed_notes": "Usar ?seed=<id> para forzar variantes."
  },
  "use_cases": [
    {
      "name": "LOGIN",
      "event": "LoginEvent",
      "description": "Autenticación básica",
      "tags": ["auth"],
      "critical": true
    }
  ],
  "pages": [
    {
      "id": "home",
      "title": "Landing",
      "url_patterns": ["/", "/home"],
      "description": "Catálogo destacado",
      "required_elements": [
        {"selector": "header nav", "description": "Barra principal"},
        {"text_contains": "Now Trending"}
      ]
    }
  ],
  "tasks_policy": {
    "min_examples_per_use_case": 3,
    "recommended_difficulty_curve": ["easy", "medium", "hard"]
  }
}
```

## Flujo de validación

1. **Fase 1 – Procedural** (`verify_project.py`): carga el deck, comprueba coincidencia con `WebProject` (ID, use cases, eventos).
2. **Fase 2 – Visual inspector** (`visual_inspector.py`): abre las páginas del deck con Playwright y verifica que los elementos requeridos existen.
3. **Fase 3 – Sandbox**: una vez aprobadas las dos fases anteriores, se despliega el proyecto y se analizan métricas reales de agentes/mineros.

Estas fases permiten rechazar contribuciones que no respeten el deck antes de invertir recursos en despliegues largos.
