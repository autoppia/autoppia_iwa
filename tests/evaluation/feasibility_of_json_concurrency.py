from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import CheckEventTest
from autoppia_iwa.src.demo_webs.projects.omnizone_3.main import omnizone_project
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.execution.actions.actions import ClickAction, HoverAction, NavigateAction, ScrollAction, TypeAction
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType
from autoppia_iwa.src.shared.utils import generate_random_web_agent_id
from autoppia_iwa.src.web_agents.classes import TaskSolution

WEB_PROJECT = omnizone_project
URL = "http://localhost:8002/"
task = Task(prompt="Perform various actions on the Omnizone homepage", url=URL, tests=[])

# --- Define Common Actions ---

action_navigate = NavigateAction(url=URL)


def action_type_search(text):
    return TypeAction(
        # selector=Selector(type=SelectorType.XPATH_SELECTOR, value="html/body/header/nav/div[2]/div/input"),
        selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//input[@type='search' and @placeholder='Search Autozon']"),
        text=text,
    )


action_submit_search = ClickAction(
    selector=Selector(type=SelectorType.XPATH_SELECTOR, value="html/body/header/nav/div[2]/div/button")
    # selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//button[.//svg[contains(@class, 'lucide-search')]]")
    # selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//button[@type='submit']//svg[contains(@class, 'lucide-search')]")
    # selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//button//svg[@class='lucide-search']/ancestor::button[1]")
    # selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//button[@type='submit']")
)

action_click_cart = ClickAction(selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//a[@href='/cart']"))

action_click_account_lists = ClickAction(selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//div[text()='Account & Lists']"))

action_click_todays_deals = ClickAction(selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//div[contains(@class, 'bg-amazon-lightBlue')]//span[text()=\"Today's Deals\"]"))

action_click_cooker_category = ClickAction(selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//a[@href='/kitchen-2']/h3[text()='Cooker']"))

action_click_next_slide = ClickAction(selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//button[@aria-label='Next slide']"))

action_click_all_dropdown = ClickAction(selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//div[contains(@class, 'bg-gray-100') and contains(., 'All')]/span[text()='All']"))

action_hover_account_lists = HoverAction(selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//div[text()='Account & Lists']"))

action_click_returns_orders = ClickAction(selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//div[text()='Returns']/following-sibling::div[text()='& Orders']"))

action_click_logo_homepage = ClickAction(selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//a[@href='/']/div/h1[text()='Autozone']"))

action_scroll_window_down = ScrollAction(down=True, selector=None, value=500)

action_click_explore_kitchen = ClickAction(selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//a[text()='Explore all products in Kitchen']"))

action_click_espresso_machine = ClickAction(selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//a[@href='/kitchen-1']/div[contains(text(), 'Espresso Machine')]"))

# --- Define Scenarios ---

scenario1 = [action_navigate, action_type_search("smart watch"), action_submit_search]
scenario2 = [action_navigate, action_click_cart]
scenario3 = [action_navigate, action_click_account_lists]
scenario4 = [action_navigate, action_click_todays_deals]
scenario5 = [action_navigate, action_click_cooker_category]
scenario6 = [action_navigate, action_click_all_dropdown]
scenario7 = [action_navigate, action_scroll_window_down, action_click_espresso_machine]
scenario8 = [action_navigate, action_click_explore_kitchen]

all_scenarios = [scenario1, scenario2, scenario3, scenario4, scenario5, scenario6, scenario7, scenario8]

# --- Generate Search Scenarios ---
searchable_queries = [
    "Autozon kitchen appliances deals",
    "$5 flat delivery fee electronics",
    "Home decor under $50 online store",
    "Gaming laptop deals with free shipping",
    "Beauty products under $25 best sellers",
    "Memory foam mattress with free delivery",
    "Wireless earbuds smart watch bundle deals",
    "Resistance bands and foam roller fitness set",
]

search_scenarios = [[action_navigate, action_type_search(q), action_submit_search] for q in searchable_queries]


# --- Scenario Evaluation Function ---


async def evaluate_scenario(task_instance, list_of_actions_list, scenario_name="default_scenario"):
    print(f"\n--- Evaluating Scenario: {scenario_name} ---")
    task_instance.prompt = f"Test scenario: {scenario_name}"
    evaluator_config = EvaluatorConfig(save_results_in_db=False, browser_timeout=30000, chunk_size=3)
    evaluator = ConcurrentEvaluator(WEB_PROJECT, evaluator_config)

    evaluator_input = [TaskSolution(task_id=task_instance.id, actions=actions, web_agent_id=generate_random_web_agent_id()) for actions in list_of_actions_list]

    evaluation_result = await evaluator.evaluate_task_solutions(task_instance, evaluator_input)
    print(f"Evaluation Result for {scenario_name}")
    for er in evaluation_result:
        for eh in er.execution_history:
            print(f"  - [Error] {eh.error}")
            for shot in eh.browser_snapshot.backend_events:
                print(f"  - [Backend Events] {shot}")
        print("\n-------------\n")
    print(f"--- Finished Scenario: {scenario_name} ---\n")
    return evaluation_result


# --- Main Entry Point ---


async def main():
    # To run default action scenarios:
    # await evaluate_scenario(task, all_scenarios, "UI Flow Tests")

    # To run search-based scenarios:
    task.tests = [CheckEventTest(event_name="SEARCH_PRODUCT", event_criteria={"query": ""})]
    await evaluate_scenario(task, search_scenarios, "Search Queries")


# def read_write_json_file():
#     import contextlib
#     import fcntl
#     import json
#
#     from autoppia_iwa.src.demo_webs.classes import BackendEvent
#
#     json_file_path = WEB_3_AUTOZONE_JSON_FILEPATH
#
#     with open(json_file_path) as f:
#         with contextlib.suppress(ImportError, ModuleNotFoundError):
#             fcntl.flock(f, fcntl.LOCK_SH)
#         try:
#             events_data = json.load(f)
#         finally:
#             with contextlib.suppress(NameError):
#                 fcntl.flock(f, fcntl.LOCK_UN)
#
#     events = [BackendEvent(**event) for event in events_data]
#     print(events)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
    # read_write_json_file()
