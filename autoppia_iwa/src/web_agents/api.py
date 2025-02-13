import asyncio

from flask import Flask, request

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.src.web_agents.random.agent import RandomClickerWebAgent

app = Flask(__name__)
EXPOSED_WEB_AGENT = RandomClickerWebAgent


@app.route('/solve_task', methods=['POST'])
def solve_task():
    task_json = request.get_json()
    task = Task.parse_obj(task_json)
    agent = EXPOSED_WEB_AGENT()
    solution: TaskSolution = asyncio.run(agent.solve_task(task))
    return solution.model_dump()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
