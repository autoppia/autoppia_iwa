import json
from pathlib import Path

from autoppia_iwa.config.config import PROJECT_BASE_DIR

VERIFICATION_DIR = PROJECT_BASE_DIR.parent / "verification_results"

PROJECT_IDS = [
    "autobooks",
]

async def validate_operator_with_llm(prompt, constraint, llm_service):
    field = constraint.get("field")
    operator = constraint.get("operator")
    value = constraint.get("value")
    
    system_prompt = (
        "You are a validation expert. Your task is to verify if a natural language prompt "
        "accurately represents a specific constraint, especially the semantic meaning of the operator.\n\n"
        "KEY PRINCIPLE: FOCUS ON SEMANTIC MEANING, NOT EXACT WORDING.\n"
        "Auxiliary verbs (is, was, should be) and formatting are IRRELEVANT.\n\n"
        "Common operators and their meanings:\n"
        "- equals: refers to an exact match (e.g., 'name is X', 'set name to X', 'using name X')\n"
        "- not_equals: excludes the value (e.g., 'name is NOT X', 'name NOT X', 'other than X', 'different from X')\n"
        "- contains: value is part of the field (e.g., 'name includes X', 'name has X', 'containing X')\n"
        "- not_contains: value is NOT part of the field (e.g., 'not containing X', 'excluding X', 'without X')\n"
        "- greater_than/less_than: numeric comparisons (e.g., 'above', 'under', 'more than')\n"
        "- greater_equal/less_equal: (e.g., 'at least', 'at most', 'minimum', 'maximum')\n\n"
        "Respond strictly in JSON format:\n"
        "{\n"
        "  \"valid\": boolean,\n"
        "  \"reason\": \"A short explanation of why the operator is correctly or incorrectly represented. Be lenient with natural language phrasing if the meaning is clear.\"\n"
        "}"
    )
    
    user_prompt = (
        f"Prompt: \"{prompt}\"\n"
        f"Constraint: {field} {operator} '{value}'\n\n"
        "Does the prompt accurately reflect this constraint's operator and value?"
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    
    try:
        response_str = await llm_service.async_predict(messages=messages, json_format=True)
        if not response_str:
            return False, "Empty response from LLM"
            
        data = json.loads(response_str) if isinstance(response_str, str) else response_str
        return data.get("valid", False), data.get("reason", "No reason provided")
    except Exception as e:
        return False, f"LLM Error: {str(e)}"

async def is_task_consistent(task, llm_service):
    prompt = task.get("prompt", "")
    constraints = task.get("constraints", [])

    for constraint in constraints:
        value = str(constraint.get("value", ""))
        if not value: continue
            
        # 1. First check: Value presence (deterministic)
        if value.lower() not in prompt.lower():
            # Special case: handle 'a T' -> 'T' if searching
            if len(value) > 2 and value.lower() not in prompt.lower():
                return False, f"Valor '{value}' de constraint '{constraint.get('field')}' no está en el prompt"
        
        # 2. Second check: Operator semantics (LLM)
        is_valid_op, reason = await validate_operator_with_llm(prompt, constraint, llm_service)
        if not is_valid_op:
            return False, f"Operador '{constraint.get('operator')}' mal representado: {reason}"
            
    return True, "Consistente"
    
async def run_validation(project_id, llm_service):
    input_file = VERIFICATION_DIR / f"misgenerated_tasks_{project_id}.json"
    output_file = VERIFICATION_DIR / f"{project_id}_tasksconsistence.json"
    
    if not input_file.exists():
        print(f"❌ No existe el archivo de errores para: {project_id}")
        return


    with open(input_file, "r") as f:
        data = json.load(f)
    use_cases = data.get("use_cases", {})
    
    all_results = {
        "project_id": project_id,
        "summary": {"total": 0, "correct": 0, "incorrect": 0},
        "details": []
    }
    
    for uc_name, uc_content in use_cases.items():
        tasks = uc_content.get("flagged_tasks", [])
        print(f"\n📂 Analizando Use Case: {uc_name}")
        
        for task in tasks:
            valid, msg = await is_task_consistent(task, llm_service)
            
            res_item = {
                "task_id": task.get("task_id"),
                "use_case": uc_name,
                "is_consistent": valid,
                "reason": msg,
                "prompt": task.get("prompt")
            }
            all_results["details"].append(res_item)
            
            all_results["summary"]["total"] += 1
            if valid:
                all_results["summary"]["correct"] += 1
                print(f"   ✅ Tarea {task.get('task_id')[:8]}... BIEN")
            else:
                all_results["summary"]["incorrect"] += 1
                print(f"   ⚠️ Tarea {task.get('task_id')[:8]}... MAL: {msg}")
    
    # Guardamos el nuevo archivo JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
        
    print(f"\n💾 Resultados guardados en: {output_file}")


    
async def main():
    AppBootstrap()
    llm_service = DIContainer.llm_service()
    
    print(f"🚀 Iniciando validación para {len(PROJECT_IDS)} proyectos: {', '.join(PROJECT_IDS)}")
    
    for pid in PROJECT_IDS:
        await run_validation(pid, llm_service)
        
    print("\n✅ Proceso de validación global finalizado.")

if __name__ == "__main__":
    from autoppia_iwa.src.bootstrap import AppBootstrap
    from autoppia_iwa.src.di_container import DIContainer
    import asyncio
    
    asyncio.run(main())