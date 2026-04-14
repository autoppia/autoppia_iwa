# DE Trajectories Para Mí (versión 12 años)

## Idea rápida
Piensa en una `DE trajectory` como una tarjeta con 4 cosas:

1. **seed**: el número que “congela” los datos del juego.
2. **question**: la pregunta que queremos responder.
3. **expected_answer**: la respuesta correcta esperada.
4. **actions** (a veces): pasos de navegador para sacar el dato.

El test básicamente pregunta:

**“¿La respuesta que sacamos contiene la respuesta esperada?”**

Si sí: `PASS`
Si no: `FAIL`

---

## Cómo funciona por dentro (fácil)

### Caso A: trajectory con `actions`
1. Abre la web.
2. Ejecuta los pasos (click, navegar, extract, etc).
3. Junta el texto extraído.
4. Comprueba si aparece `expected_answer`.

### Caso B: trajectory sin `actions` (dataset-only)
1. Carga dataset de esa `seed`.
2. Lo convierte a texto.
3. Busca `expected_answer` dentro de ese texto.

---

## Por qué existe `seed`
La `seed` hace que los datos sean siempre los mismos para esa prueba.
Así evitamos “hoy pasa, mañana falla” por datos cambiantes.

---

## Cómo probarlo en tu máquina
Estando en el repo y con venv activo:

```bash
source .venv/bin/activate
```

Si no tienes credenciales cargadas en shell:

```bash
export OPENAI_API_KEY=dummy
export LLM_PROVIDER=openai
```

### 1) Probar UNA trajectory
```bash
python scripts/debug_data_extraction_trajectories.py -p autocinema -t autocinema.de.seed1.film_detail.199c022b67
```

### 2) Probar TODAS las trajectories de un proyecto
```bash
python scripts/debug_data_extraction_trajectories.py -p autocinema
```

### 3) Probar con el verification pipeline (normal)
```bash
python -m autoppia_iwa.entrypoints.web_verification.run --project-id autocinema
```

En la salida mira el bloque:

`STEP 2.5: DATA EXTRACTION TRAJECTORIES VERIFICATION`

---

## Cómo “romper” una para comprobar que detecta errores
1. Cambia temporalmente un `expected_answer` por algo falso (ej: `WRONG_VALUE`).
2. Ejecuta el test.
3. Debe salir `FAIL`.
4. Vuelve a poner el valor correcto.
5. Debe volver a `PASS`.

Esto confirma que el sistema **sí detecta errores reales**.

---

## Regla de oro
Si falla una DE trajectory, revisa en este orden:

1. `seed` correcta.
2. `expected_answer` correcto.
3. Si usa `actions`, que los selectores/flujo sigan siendo válidos.

---

## Qué script hace cada cosa (para explicarlo al jefe)

### 1) Dónde viven las trajectories
- `autoppia_iwa/src/demo_webs/projects/pXX_*/data_extraction_trajectories.py`
  - Aquí están definidas las DE trajectories por proyecto.
  - Cada una tiene `seed`, `question`, `expected_answer` y opcionalmente `actions`.

### 2) Registro central de trajectories
- `autoppia_iwa/src/demo_webs/data_extraction_trajectory_registry.py`
  - Sabe qué proyectos tienen DE trajectories.
  - Carga las trajectories del proyecto cuando se las piden.

### 3) Script de debug (manual, rápido)
- `scripts/debug_data_extraction_trajectories.py`
  - Sirve para probar una trajectory concreta o todas las de un proyecto.
  - Útil para depurar rápido y ver `PASS/FAIL` sin ejecutar todo el pipeline.

### 4) Verificador de DE (lógica de validación)
- `autoppia_iwa/entrypoints/web_verification/data_extraction_verifier.py`
  - Es la lógica que decide si cada trajectory pasa o falla.
  - Hace comparación entre lo extraído (o dataset) y `expected_answer`.

### 5) Pipeline completo de verificación
- `autoppia_iwa/entrypoints/web_verification/web_verification_pipeline.py`
  - Orquesta todos los pasos de verificación.
  - En DE usa el **STEP 2.5** para correr trajectories del proyecto.

### 6) Comando de entrada del pipeline
- `autoppia_iwa/entrypoints/web_verification/run.py`
  - Es el script que lanzas con:
    - `python -m autoppia_iwa.entrypoints.web_verification.run --project-id ...`
  - Parsea flags y ejecuta el pipeline.
