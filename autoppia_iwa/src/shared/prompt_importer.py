import os


class PromptImporter:
    """
    Loads a prompt from a specified file path.
    """

    def __init__(self, prompt_file_path: str):
        self.prompt_file_path = prompt_file_path
        self._prompt_content = self._load_prompt()

    def _load_prompt(self) -> str:
        if not os.path.exists(self.prompt_file_path):
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_file_path}")
        with open(self.prompt_file_path, encoding="utf-8") as file:
            return file.read()

    def get_prompt(self) -> str:
        return self._prompt_content
