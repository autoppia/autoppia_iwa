# DE Trajectories Quickstart

Guía rápida para ejecutar y validar `data extraction trajectories` desde vuestra máquina.

## Punto de partida
Estando en:

```bash
AUTOPPIA/Autoppia_repos/autoppia_iwa
```

Y con el entorno virtual activado:

```bash
source .venv/bin/activate
```

## 0) Requisito de entorno (importante)
Estos scripts cargan configuración global. Si no tienes credenciales cargadas en shell, usa:

```bash
export OPENAI_API_KEY=dummy
export LLM_PROVIDER=openai
```

Si ya tienes credenciales reales, no hace falta usar `dummy`.

## 1) Probar UNA DE trajectory

### 1.1 Ver IDs disponibles de un proyecto
Ejemplo con `autocinema`:

```bash
python - <<'PY'
from autoppia_iwa.src.demo_webs.data_extraction_trajectory_registry import get_data_extraction_trajectories
for t in get_data_extraction_trajectories("autocinema") or []:
    print(t.id, "->", t.use_case)
PY
```

### 1.2 Ejecutar una trajectory concreta por ID

```bash
python scripts/debug_data_extraction_trajectories.py \
  -p autocinema \
  -t autocinema.de.seed1.film_detail.199c022b67
```

## 2) Probar TODAS las DE trajectories de un proyecto

```bash
python scripts/debug_data_extraction_trajectories.py -p autocinema
```

Opcional: filtrar por use case:

```bash
python scripts/debug_data_extraction_trajectories.py -p autocinema -u FILM_DETAIL
```

## 3) Usarlo con el Web Verification Pipeline

## 3.1 Pipeline completo (normal)
Ejecuta verificación completa (task generation + resto de pasos + DE trajectories):

```bash
python -m autoppia_iwa.entrypoints.web_verification.run \
  --project-id autocinema
```

## 3.2 Pipeline “enfocado en DE” (rápido para validar DE en Step 2.5)
Esto fuerza que no genere tasks ni llame IWAP/dynamic, para comprobar rápido la parte DE:

```bash
python -m autoppia_iwa.entrypoints.web_verification.run \
  --project-id autocinema \
  --tasks-per-use-case 0 \
  --no-llm-review \
  --no-iwap \
  --no-dynamic-verification
```

En consola verás la sección:

- `STEP 2.5: DATA EXTRACTION TRAJECTORIES VERIFICATION`

Y en JSON:

- `verification_results/verification_<project_id>.json`
- campo `data_extraction_project_verification`

## 3.3 Flags opcionales (solo si los necesitas)
- `--data-extraction-seed <N>`: filtra qué DE trajectories se ejecutan por seed.
  - Aunque cada trajectory ya tiene su seed, este flag sirve para elegir qué grupo correr en esa ejecución.
  - Si no lo pasas, usa el default del pipeline (`seed=1`).
- `--output-dir <ruta>`: cambia la carpeta de salida.
  - Si no lo pasas, el pipeline guarda en la ruta por defecto (`./verification_results`).

## 4) Flags útiles del debug script

```bash
python scripts/debug_data_extraction_trajectories.py --help
```

Los más usados:
- `-p, --project`
- `-t, --trajectory-id` (repetible)
- `-u, --use-case` (repetible)
- `--frontend-url` (remapea localhost a otra URL)
- `--no-headless` (muestra navegador si la trajectory tiene acciones)
