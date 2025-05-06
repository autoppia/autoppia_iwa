import asyncio
import base64
from pathlib import Path

from dotenv import load_dotenv

from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification, Task
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution

load_dotenv()


async def main():
    # agent = BrowserUseWebAgent()
    agent = ApifiedWebAgent(name="Apified BrowserUse Agent", host="127.0.0.1", port=5000)
    return_recording = True

    task = Task(
        # prompt="Open Wikipedia and search 'Alejandro Magno'",
        prompt="Navigate to wikipedia and that's it, no further instructions",
        url="https://wikipedia.com",
        specifications=BrowserSpecification(viewport_width=1024, viewport_height=768),
        should_record=return_recording,
    )

    solution: TaskSolution = await agent.solve_task(task)
    print(f"Solution: {solution}")
    recording = solution.recording
    print(f"Base64 Encoded Recording: {recording[:50]}...")
    if return_recording and recording:
        try:
            video_data = base64.b64decode(recording)
            output_path = Path("./output.webm")
            with open(output_path, "wb") as video_file:
                video_file.write(video_data)
            print(f"Decoded video saved to: {output_path}")
        except base64.binascii.Error as e:
            print(f"Error decoding Base64 string: {e}")
            print(f"Problematic recording data: {recording[:100]}...")
        except Exception as e:
            print(f"An error occurred while saving the video: {e}")
    elif return_recording and not recording:
        print("No recording data received in the TaskSolution.")


if __name__ == "__main__":
    asyncio.run(main())
