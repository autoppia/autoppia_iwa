# Web Verification Pipeline

Este documento describe el pipeline completo de verificación de proyectos web en IWA, incluyendo todas las fases, dependencias, y requisitos.

## 📋 Visión General

El pipeline de verificación ejecuta **8 fases** que validan un proyecto web desde múltiples ángulos:

1. **Module Scaffold & Metadata Gate** (Procedural)
2. **Deck Consistency Gate** (Deck)
3. **Use-Case & Event Integrity Gate** (Procedural)
4. **Frontend Reachability & Code Analysis Gate** (Procedural + Frontend Analysis)
5. **Visual Evidence & LLM Review Gate** (Visual + LLM)
6. **LLM Task/Test Pipeline Gate** (LLM)
7. **Dynamic Mutation Integrity Gate** (Dynamic + LLM)
8. **Random Baseline Gate** (LLM)

## 🔄 Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────┐
│                    VERIFICATION PIPELINE                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  FASE 1: Module Scaffold & Metadata │
        │  - Verifica estructura del módulo   │
        │  - Valida archivos requeridos       │
        │  - Importa y valida WebProject      │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  FASE 2: Deck Consistency           │
        │  - Carga y valida deck JSON         │
        │  - Verifica metadata (ID, name)     │
        │  - Valida use cases coinciden       │
        │  - Verifica pages no vacío          │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  FASE 3: Use-Case & Event Integrity │
        │  - Valida ALL_USE_CASES definido     │
        │  - Verifica nombres únicos          │
        │  - Valida eventos referenciados     │
        │  - Verifica constraints_generator    │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  FASE 4: Frontend Analysis          │
        │  - Verifica frontend_url responde  │
        │  - Localiza frontend_dir           │
        │  - Analiza eventos (100% coverage) │
        │  - Analiza sistema dinámico (V1/V3)│
        │  - Valida SeedContext              │
        │  - Valida estructura de tests      │
        │  - Valida variant JSONs            │
        │  - Ejecuta tests Node.js            │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  FASE 5: Visual Evidence (LLM)      │
        │  - Abre páginas con Playwright      │
        │  - Verifica required_elements       │
        │  - Captura screenshots + HTML      │
        │  - LLM judge valida UI vs deck      │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  FASE 6: LLM Task Pipeline (LLM)    │
        │  - Genera prompts para use cases    │
        │  - Verifica placeholders resueltos │
        │  - LLM spot-check valida tareas     │
        │  - Genera tests (CheckEventTest)    │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  FASE 7: Dynamic Validation (LLM)  │
        │  - Carga páginas con seeds          │
        │  - Verifica determinismo            │
        │  - Verifica variación              │
        │  - LLM valida cambios observados   │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  FASE 8: Random Baseline (LLM)       │
        │  - RandomClicker intenta resolver   │
        │  - Verifica score = 0               │
        │  - LLM revisa traza si score > 0   │
        └─────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  GENERA REPORTE  │
                    └─────────────────┘
```

## 📊 Dependencias entre Fases

### Requisitos por Fase

| Fase | Requiere | Opcional | Bloquea si falla |
|------|----------|----------|------------------|
| **1. Module Scaffold** | Módulo Python válido | - | ✅ Sí (no puede continuar) |
| **2. Deck Consistency** | Fase 1, Deck JSON válido | - | ✅ Sí |
| **3. Use-Case Integrity** | Fase 1, Fase 2 | - | ✅ Sí |
| **4. Frontend Analysis** | Fase 1, Frontend corriendo | Frontend dir | ⚠️ Parcial (continúa con warnings) |
| **5. Visual Evidence** | Fase 2, Frontend corriendo | LLM service | ⚠️ No (solo reporta) |
| **6. LLM Task Pipeline** | Fase 3, LLM service | - | ✅ Sí |
| **7. Dynamic Validation** | Fase 2, Frontend corriendo | LLM service | ⚠️ No (solo reporta) |
| **8. Random Baseline** | Fase 6, LLM service | - | ⚠️ No (solo reporta) |

### Dependencias de Servicios

- **Frontend corriendo**: Requerido para Fases 4, 5, 7
- **LLM service**: Requerido para Fases 5, 6, 7, 8
- **Node.js**: Requerido para ejecutar tests Node.js en Fase 4
- **Playwright**: Requerido para Fases 5, 7

## 🔍 Detalles por Fase

### Fase 1: Module Scaffold & Metadata Gate

**Propósito**: Validar que el módulo Python está correctamente estructurado.

**Checks**:
- ✅ Directorio `src/demo_webs/projects/<slug>` existe
- ✅ Archivos requeridos: `main.py`, `use_cases.py`, `events.py`, `generation_functions.py`
- ✅ `main.py` se importa correctamente
- ✅ `WebProject` está expuesto con `id`, `name`, `frontend_url`, `use_cases`

**Bloquea**: Sí, si falla no puede continuar.

---

### Fase 2: Deck Consistency Gate

**Propósito**: Validar que el deck JSON coincide con el módulo Python.

**Checks**:
- ✅ Deck JSON válido (schema Pydantic)
- ✅ `project_id` y `project_name` coinciden con `WebProject`
- ✅ Use cases del deck coinciden con código
- ✅ `pages` no está vacío

**Bloquea**: Sí, si falla no puede continuar.

---

### Fase 3: Use-Case & Event Integrity Gate

**Propósito**: Validar integridad de use cases y eventos.

**Checks**:
- ✅ `ALL_USE_CASES` definido y contiene solo `UseCase` objects
- ✅ Nombres únicos
- ✅ Descripciones presentes
- ✅ Ejemplos tienen `prompt` y `prompt_for_task_generation`
- ✅ Cada use case referencia un evento en `EVENTS`
- ✅ `constraints_generator` es callable

**Bloquea**: Sí, si falla no puede continuar.

---

### Fase 4: Frontend Reachability & Code Analysis Gate

**Propósito**: Analizar el código frontend y validar implementación.

**Checks**:
- ✅ `frontend_url` responde (HTTP GET)
- ✅ `frontend_dir` localizado en `autoppia_webs_demo`
- ✅ **Event coverage 100%** (todos los eventos usados)
- ✅ **Sistema dinámico V1/V3** detectado
- ✅ **Uso real V1/V3** contado (addWrapDecoy, changeOrderElements, getVariant)
- ✅ **SeedContext** validado (existe, exporta SeedProvider/useSeed, usa useSearchParams)
- ✅ **Estructura de tests** validada (tests/, test-dynamic-system.js, test-events.js, README.md)
- ✅ **Variant JSONs** validados (id-variants.json, class-variants.json, text-variants.json)
- ✅ **Tests Node.js** ejecutados (test-dynamic-system.js, test-events.js)

**Bloquea**: Parcial, algunos checks son críticos (event coverage 100%), otros son warnings.

**Nuevas validaciones (2025-01-27)**:
- Contador de uso real de V1/V3
- Enforcement de cobertura 100%
- Integración con tests Node.js
- Validación de SeedContext
- Validación de estructura de tests
- Validación de variant JSONs

---

### Fase 5: Visual Evidence & LLM Review Gate

**Propósito**: Validar que la UI renderizada coincide con el deck.

**Requisitos**: Frontend corriendo, LLM service (opcional)

**Checks**:
- ✅ Abre cada página del deck con Playwright
- ✅ Verifica `required_elements` existen
- ✅ Captura screenshot + HTML snapshot
- ✅ LLM judge valida UI vs descripción del deck (opcional)

**Bloquea**: No, solo reporta resultados.

---

### Fase 6: LLM Task/Test Pipeline Gate

**Propósito**: Generar y validar tareas para miners.

**Requisitos**: LLM service

**Checks**:
- ✅ Genera prompts para use cases
- ✅ Verifica placeholders resueltos (no `<constraints_info>` sin resolver)
- ✅ Verifica prompts mencionan valores de constraints
- ✅ LLM spot-check valida tareas
- ✅ Genera `CheckEventTest` para cada tarea
- ✅ Tests alineados con eventos esperados

**Bloquea**: Sí, si falla no puede continuar.

---

### Fase 7: Dynamic Mutation Integrity Gate

**Propósito**: Validar que el sistema dinámico funciona correctamente.

**Requisitos**: Frontend corriendo, LLM service (opcional)

**Checks**:
- ✅ Carga páginas con `seed=None` (baseline)
- ✅ Carga páginas con seeds determinísticos (13, 23)
- ✅ Verifica determinismo (mismo seed = mismo resultado)
- ✅ Verifica variación (diferentes seeds = diferentes resultados)
- ✅ Verifica seedless estable (sin seed = estable)
- ✅ LLM valida cambios observados (opcional)

**Bloquea**: No, solo reporta resultados.

---

### Fase 8: Random Baseline Gate

**Propósito**: Validar que un agente aleatorio no puede resolver tareas.

**Requisitos**: LLM service

**Checks**:
- ✅ `RandomClickerWebAgent` intenta resolver tareas
- ✅ Verifica score = 0 (no debe resolver nada)
- ✅ Si score > 0, LLM revisa traza para confirmar

**Bloquea**: No, solo reporta resultados.

## 🚀 Ejecución del Pipeline

### Comando Completo

```bash
python -m modules.web_verification verify <project_slug> \
  --deck path/to/deck.deck.json \
  --frontend-root /path/to/autoppia_webs_demo \
  --frontend-base-url http://localhost:8000 \
  --code-checks \
  --results-checks
```

### Flags Importantes

- `--code-checks`: Ejecuta solo fases 1-4 (procedural/deck/frontend)
- `--results-checks`: Ejecuta solo fases 5-8 (LLM/dynamic/agent)
- `--frontend-root`: Ruta al directorio `autoppia_webs_demo`
- `--frontend-base-url`: Override de `frontend_url` del módulo
- `--frontend-port`: Override solo del puerto

### Variables de Entorno

- `AUTOPPIA_WEB_FRONTENDS_ROOT`: Ruta al directorio de frontends
- `AUTOPPIA_TASKS_PER_USE_CASE`: Número de tareas por use case (default: 2)
- `AUTOPPIA_DYNAMIC_MAX_PAGES`: Máximo de páginas para validación dinámica (default: 2)
- `AUTOPPIA_DYNAMIC_TIMEOUT_MS`: Timeout para carga de páginas (default: 15000)
- `AUTOPPIA_DYNAMIC_SIM_THRESHOLD`: Umbral de similitud para determinismo (default: 0.995)
- `AUTOPPIA_DYNAMIC_MIN_DELTA`: Delta mínimo para detectar mutación (default: 0.02)

## 📝 Reporte Final

El pipeline genera un reporte en Markdown que incluye:

1. **Resumen ejecutivo**: Estado general (PASS/FAIL)
2. **Sección Procedural**: Resultados de fases 1-4
3. **Sección Deck**: Resultados de fase 2
4. **Sección Use Cases**: Resultados de fase 3
5. **Sección LLM Tasks**: Resultados de fase 6
6. **Sección LLM Tests**: Resultados de fase 6 (tests)
7. **Sección Dynamic**: Resultados de fase 7
8. **Análisis Frontend**: Detalles de fase 4
   - Event coverage (100% requerido)
   - Dynamic usage (V1/V3 counts)
   - SeedContext validation
   - Tests structure validation
   - Variant JSONs validation
   - Node.js tests results

## ⚠️ Checks Críticos

Los siguientes checks **bloquean** el pipeline si fallan:

1. ✅ Module scaffold válido
2. ✅ Deck consistency
3. ✅ Use-case integrity
4. ✅ **Event coverage 100%** (nuevo)
5. ✅ LLM task generation válida

Los siguientes checks **no bloquean** pero se reportan:

- Frontend reachability (warning si falla)
- Visual evidence (solo reporta)
- Dynamic validation (solo reporta)
- Random baseline (solo reporta)

## 🔧 Troubleshooting

### Frontend no responde

- Verifica que el frontend esté corriendo
- Usa `--frontend-base-url` para override
- Verifica `AUTOPPIA_WEB_FRONTENDS_ROOT` está configurado

### LLM service no disponible

- Algunas fases requieren LLM (5, 6, 7, 8)
- Usa `--code-checks` para ejecutar solo fases sin LLM
- Configura LLM service en `DIContainer` o variables de entorno

### Tests Node.js fallan

- Verifica que Node.js esté en PATH
- Verifica que `tests/test-dynamic-system.js` y `tests/test-events.js` existan
- Ejecuta manualmente: `node tests/test-dynamic-system.js`

### SeedContext no encontrado

- Verifica que `src/context/SeedContext.tsx` exista
- Verifica que exporte `SeedProvider` y `useSeed`
- Verifica que use `useSearchParams` de Next.js

---

**Última actualización**: 2025-01-27
**Versión**: Incluye mejoras de prioridad ALTA y MEDIA
