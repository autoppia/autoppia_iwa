"""
Test script to evaluate the contact form task used in the technical test.
Validates an agent that fills the contact form with subject='Job Position' and message containing 'I am the best developer'.
"""

import asyncio
from loguru import logger

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution

# Configuration
PROJECT_ID = "autocinema"
AGENT_HOST = "127.0.0.1"
AGENT_PORT = 7000
AGENT_TIMEOUT = 120

# Specific contact form task
CONTACT_PROMPT = "Fill the contact form with a subject equal to 'Job Position' and message contains 'I am the best developer'"


async def create_contact_task(project) -> Task:
    """Create a contact form task with specific criteria."""
    # Find the CONTACT use case
    contact_use_case = next((uc for uc in project.use_cases if uc.name == "CONTACT"), None)
    if not contact_use_case:
        raise ValueError(f"CONTACT use case not found in project {project.name}")
    
    # Create test that checks for contact event with specific subject and message
    test = CheckEventTest(
        event_name="CONTACT",
        event_criteria={
            "subject": {"operator": "equals", "value": "Job Position"},
            "message": {"operator": "contains", "value": "I am the best developer"},
        },
    )
    
    task = Task(
        use_case=contact_use_case,
        prompt=CONTACT_PROMPT,
        url=project.frontend_url,
        tests=[test]
    )
    
    return task


async def test_contact_task():
    """Test the contact form task with the agent."""
    AppBootstrap()
    
    logger.info("=" * 80)
    logger.info("TECHNICAL TEST - CONTACT FORM TASK EVALUATION")
    logger.info("=" * 80)
    logger.info(f"Project: {PROJECT_ID}")
    logger.info(f"Prompt: {CONTACT_PROMPT}")
    logger.info(f"Agent: http://{AGENT_HOST}:{AGENT_PORT}")
    logger.info("=" * 80)
    logger.info("")
    
    # Get project
    project = next((p for p in demo_web_projects if p.id.lower() == PROJECT_ID.lower()), None)
    if not project:
        logger.error(f"Project '{PROJECT_ID}' not found")
        return
    
    logger.info(f"Found project: {project.name}")
    logger.info(f"Frontend URL: {project.frontend_url}")
    
    # Create task
    task = await create_contact_task(project)
    logger.info(f"Task created with ID: {task.id}")
    logger.info(f"Task URL: {task.url}")
    
    # Create agent
    agent = ApifiedWebAgent(
        id="technical_test_agent",
        name="Technical Test Agent",
        host=AGENT_HOST,
        port=AGENT_PORT,
        timeout=AGENT_TIMEOUT
    )
    
    # Reset database
    backend = BackendDemoWebService(project)
    await backend.reset_database(web_agent_id=agent.id)
    logger.info("Database reset")
    
    try:
        # Get solution from agent
        logger.info("Sending task to agent...")
        prepared_task = task.prepare_for_agent(agent.id)
        solution = await agent.solve_task(prepared_task)
        
        task_solution = TaskSolution(
            task_id=task.id,
            actions=solution.actions or [],
            web_agent_id=agent.id
        )
        task_solution.actions = task_solution.replace_web_agent_id()
        
        logger.info(f"Agent returned {len(task_solution.actions)} actions")
        
        if len(task_solution.actions) == 0:
            logger.warning("⚠️  Agent returned no actions!")
        
        # Evaluate solution
        logger.info("Evaluating solution...")
        evaluator = ConcurrentEvaluator(project, EvaluatorConfig())
        eval_result = await evaluator.evaluate_single_task_solution(task, task_solution)
        
        # Print results
        logger.info("")
        logger.info("=" * 80)
        logger.info("RESULTS")
        logger.info("=" * 80)
        logger.info(f"Final Score: {eval_result.final_score}")
        logger.info(f"Success: {'✅ YES' if eval_result.final_score == 1.0 else '❌ NO'}")
        logger.info(f"Number of actions: {len(task_solution.actions)}")
        logger.info("")
        
        if eval_result.final_score == 1.0:
            logger.info("🎉 SUCCESS! The agent successfully completed the contact form task.")
        else:
            logger.warning("⚠️  The agent did not complete the task successfully.")
            logger.info("Check the test results for more details:")
            for i, test_result in enumerate(eval_result.test_results):
                logger.info(f"  - Test {i+1}: {'✅ PASSED' if test_result.success else '❌ FAILED'}")
        
        logger.info("=" * 80)
        
        return {
            "success": eval_result.final_score == 1.0,
            "score": eval_result.final_score,
            "num_actions": len(task_solution.actions),
            "test_results": [{"success": tr.success, "extra_data": tr.extra_data} for tr in eval_result.test_results]
        }
        
    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
        raise
    finally:
        await backend.close()


if __name__ == "__main__":
    try:
        result = asyncio.run(test_contact_task())
        if result and result["success"]:
            exit(0)
        else:
            exit(1)
    except KeyboardInterrupt:
        logger.warning("Test interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"Test failed: {e}")
        exit(1)
