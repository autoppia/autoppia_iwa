# Data Extraction en Autoppia (explicado fácil)

## 1) ¿Qué es Data Extraction?
Piensa que la web tiene una "base de datos secreta" (dataset) que cambia según la **seed**.

Una **DEtask** es una pregunta tipo:
- "¿Quién es el director de X?"

Y debe traer:
- `de_use_case_name` (tipo de pregunta, por ejemplo `FIND_DIRECTOR`)
- `prompt` (la pregunta)
- `expected_answer` (la respuesta correcta esperada)
- un test `DataExtractionTest` para validar la respuesta.

## 2) ¿Dónde se define cada cosa?

- DE usecases + cómo generar DEtasks por proyecto:
  - `autoppia_iwa/src/demo_webs/projects/<project_module>/dataExtractionUseCases.py`
- Verificación de trajectories DE:
  - `autoppia_iwa/entrypoints/web_verification/data_extraction_verifier.py`
- Verificación de generación de DEtasks:
  - `autoppia_iwa/entrypoints/web_verification/data_extraction_task_generation_verifier.py`
- Pipeline que junta todo (Step 2.5 + Step 2.6):
  - `autoppia_iwa/entrypoints/web_verification/web_verification_pipeline.py`
- Runner CLI del pipeline:
  - `autoppia_iwa/entrypoints/web_verification/run.py`
- Script debug para trajectories DE:
  - `scripts/debug_data_extraction_trajectories.py`

## 3) Cómo generar DEtasks

### Opción A (recomendada): con Benchmark en modo `data_extraction_only`
En `autoppia_iwa/entrypoints/benchmark/run.py` pon:
- `test_types="data_extraction_only"`
- `PROJECT_IDS=["autocinema"]` (o el proyecto que quieras)

Luego ejecuta:

```bash
python -m autoppia_iwa.entrypoints.benchmark.run
```

Las DEtasks generadas se guardan en:

```text
benchmark-output/cache/DataExtraction/<project_id>_DE_tasks.json
```

Ejemplo:

```text
benchmark-output/cache/DataExtraction/autocinema_DE_tasks.json
```

### Opción B: generación implícita en Web Verification Pipeline
El pipeline también genera DEtasks en su Step 2.6 para verificarlas.

## 4) Cómo verificar que las DEtasks están bien

Ejecuta el verification pipeline:

```bash
python -m autoppia_iwa.entrypoints.web_verification.run \
  --project-id autocinema
```

Esto ejecuta:
- **Step 2.5**: verifica DE trajectories
- **Step 2.6**: genera y verifica DEtasks por DE usecase

### ¿Qué comprueba Step 2.6?
`DataExtractionTaskGenerationVerifier` valida, por cada DE usecase esperado:
- hay exactamente 1 DEtask
- tiene prompt
- tiene expected_answer
- el usecase coincide
- la seed del URL es coherente
- el expected_answer existe en el dataset de esa seed
- hay test `DataExtractionTest`

## 5) ¿Dónde veo los resultados?

Resultado principal del pipeline:

```text
verification_results/verification_<project_id>.json
```

Bloque a mirar:

```json
"data_extraction_task_generation_verification": {
  "passed_count": ...,
  "total_count": ...,
  "generated_count": ...,
  "results": [...]
}
```

En `results[]` verás por DE usecase:
- `ok`
- `detail`
- `prompt`
- `expected_answer`
- `checks`

Comando útil:

```bash
jq '.data_extraction_task_generation_verification' verification_results/verification_autocinema.json
```

## 6) Cómo verificar trajectories DE sueltas (rápido)

Lista trajectories DE de un proyecto:

```bash
python scripts/debug_data_extraction_trajectories.py -p autocinema
```

Ejecutar una trajectory concreta:

```bash
python scripts/debug_data_extraction_trajectories.py -p autocinema -t <trajectory_id>
```

## 7) Resumen ultra-corto

- `dataExtractionUseCases.py` = fabrica DEtasks.
- Benchmark en `data_extraction_only` = genera y cachea DEtasks en `benchmark-output/cache/DataExtraction`.
- Web Verification Pipeline = comprueba trajectories DE (2.5) + generación DEtasks (2.6).
- Resultado final = `verification_results/verification_<project>.json`.
