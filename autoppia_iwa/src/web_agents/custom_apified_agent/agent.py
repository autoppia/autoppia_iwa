from autoppia_iwa.src.web_agents.base import ApifiedWebAgent


class MyCustomApifiedWebAgent(ApifiedWebAgent):
    def __init__(self, name: str, host: str, port: int):
        super().__init__(name, host, port)
