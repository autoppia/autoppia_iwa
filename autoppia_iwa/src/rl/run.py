# entrypoints/benchmark/run_rl.py (ejemplo)
from agents.rl_agent import RLWebAgent
from iwa_rl.envs.async_env import AsyncWebAgentEnv
from iwa_rl.rewards.milestone_delta import MilestoneDeltaReward, url_text_scorer
from loguru import logger

from autoppia_iwa.entrypoints.benchmark.task_generation import get_projects_by_ids
from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor

# 1) Policy dummy (regla/LLM/ppo → aquí devuelves acciones dict/JSON)


class DummyPolicy:
    async def act(self, obs):
        # navega a start, escribe, etc. (placeholder)
        return {"type": "WaitAction", "time_seconds": 0.2}


# 2) Env factory por task (instancia executor + reward)


def make_env_factory(project):
    def factory(task):
        # Inicializa PlaywrightBrowserExecutor con Page creada fuera o dentro (según tu infra).
        executor = PlaywrightBrowserExecutor(
            browser_config=BrowserSpecification(headless=True),
            page=project.get_page(),  # si tu WebProject expone esto
            backend_demo_webs_service=BackendDemoWebService(project),
        )
        reward = MilestoneDeltaReward(scorer=url_text_scorer, success_threshold=1.0)

        async def reset_fn(executor, task):
            await executor.page.goto(task.start_url)

        return AsyncWebAgentEnv(
            executor=executor,
            task_sampler=lambda: task,
            reward_fn=reward,
            reset_fn=reset_fn,
            H=320,
            W=320,
            max_steps=40,
            action_mode="json",
            safe_action_types=["NavigateAction", "ClickAction", "TypeAction", "ScrollAction", "SubmitAction", "WaitAction", "HoverAction"],
        )

    return factory


def main():
    PROJECT_IDS = ["work"]
    PROJECTS = get_projects_by_ids(demo_web_projects, PROJECT_IDS)
    if not PROJECTS:
        logger.error("No valid projects.")
        return

    [
        RLWebAgent(
            id="rl-1",
            name="RLAgent",
            env_factory=make_env_factory(PROJECTS[0]),
            policy=DummyPolicy(),
            max_steps=40,
        )
    ]
