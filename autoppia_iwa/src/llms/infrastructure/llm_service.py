from typing import Any, Dict, List, Optional
import requests
from openai import OpenAI

from autoppia_iwa.src.llms.domain.interfaces import ILLMService
from autoppia_iwa.src.llms.domain.openai.classes import BaseOpenAIResponseFormat, OpenAILLMModelMixin


class BaseLLMService(ILLMService):
    """
    Base class for LLM Task Generators, providing common HTTP request functionality.
    """

    def make_request(
        self,
        message_payload: List[Dict[str, str]],
        llm_kwargs: Optional[Dict[str, Any]] = None,
        chat_completion_kwargs: Optional[Dict[str, Any]] = None,
        json_format: bool = False,
        schema: str = None,
    ) -> Any:
        raise NotImplementedError("Subclasses must implement this method.")

    @staticmethod
    def _make_http_request(url: str, payload: Dict, headers: Optional[Dict] = None, method: str = "post") -> Dict:
        """
        Makes an HTTP request.

        Args:
            url (str): The target URL.
            payload (Dict): The request payload.
            headers (Optional[Dict]): HTTP headers.
            method (str): HTTP method ('post' or 'get').

        Returns:
            Dict: JSON response from the server or error details.
        """
        try:
            if method.lower() == "post":
                response = requests.post(url, headers=headers, json=payload)
            elif method.lower() == "get":
                response = requests.get(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error in _make_http_request: {e}")
            return {"error": str(e)}


class LocalLLMService(BaseLLMService):
    """
    Local LLM Service. If json_format is True, the request payload will include
    a flag ('force_json': True) to enforce JSON formatting in the response.
    """

    def __init__(self, endpoint_url: str, threshold: int = 100):
        self.endpoint_url = endpoint_url

    def make_request(
        self,
        message_payload: List[Dict[str, str]],
        llm_kwargs: Optional[Dict[str, Any]] = None,
        chat_completion_kwargs: Optional[Dict[str, Any]] = None,
        json_format: bool = False,
        schema: str = None,
    ) -> Any:
        print("LLM REQUEST SENT")
        payload = {"input": {"text": message_payload}}
        if llm_kwargs:
            payload["input"]["llm_kwargs"] = llm_kwargs
        if chat_completion_kwargs:
            payload["input"]["chat_completion_kwargs"] = chat_completion_kwargs
        # Add flag to force JSON formatting if required.
        if json_format:
            payload["input"]["force_json"] = True

        response = self._make_http_request(self.endpoint_url, payload)
        print("LLM REQUEST Response")
        return response.get("output", {"error": "No output from local model"})

    async def async_make_request(
        self,
        message_payload: List[Dict[str, str]],
        llm_kwargs: Optional[Dict[str, Any]] = None,
        chat_completion_kwargs: Optional[Dict[str, Any]] = None,
        json_format: bool = False,
        schema: str = None,
    ) -> Any:
        payload = {"input": {"text": message_payload}}
        if llm_kwargs:
            payload["input"]["llm_kwargs"] = llm_kwargs
        if chat_completion_kwargs:
            payload["input"]["chat_completion_kwargs"] = chat_completion_kwargs
        if json_format:
            payload["input"]["force_json"] = True

        response = self._make_http_request(self.endpoint_url, payload)
        return response.get("output", {"error": "No output from local model"})


class OpenAIService(BaseLLMService, OpenAILLMModelMixin):
    """
    Service for interacting with OpenAI's GPT models.
    When json_format is True, and no custom response_format is provided via chat_completion_kwargs,
    a default JSON formatting instruction is added.
    """

    def __init__(self, api_key: str, model: str, max_tokens: int = 2000, temperature: float = 0.7):
        """
        Initialize the OpenAI Service.

        Args:
            model (str): The GPT model to use, e.g., "gpt-4" or "gpt-3.5-turbo".
            max_tokens (int): Maximum number of tokens for the response.
            temperature (float): Sampling temperature for randomness.
        """
        self._model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._messages: List[dict] = []
        self.client = OpenAI(api_key=api_key)

    async def async_make_request(
        self,
        message_payload: List[Dict[str, str]],
        llm_kwargs: Optional[Dict[str, Any]] = None,
        chat_completion_kwargs: Optional[Dict[str, Any]] = None,
        json_format: bool = False,
        schema: str = None,
    ) -> str:
        parameters = {
            "model": self._model,
            "messages": message_payload,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        if chat_completion_kwargs:
            parameters["temperature"] = chat_completion_kwargs.get("temperature", self.temperature)
            response_format = chat_completion_kwargs.get("response_format", {})
            if response_format:
                response_format_model = BaseOpenAIResponseFormat(**response_format)
                parameters["response_format"] = response_format_model.model_dump()

        # If forcing JSON and no response_format is set, add a default JSON formatting instruction.
        if json_format and "response_format" not in parameters:
            parameters["response_format"] = {"force_json": True}

        try:
            response = self.client.chat.completions.create(**parameters)
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Error with OpenAI API: {e}")

    def make_request(
        self,
        message_payload: List[Dict[str, str]],
        llm_kwargs: Optional[Dict[str, Any]] = None,
        chat_completion_kwargs: Optional[Dict[str, Any]] = None,
        json_format: bool = False,
        schema: str = None,
    ) -> str:
        parameters = {
            "model": self._model,
            "messages": message_payload,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        if chat_completion_kwargs:
            parameters["temperature"] = chat_completion_kwargs.get("temperature", self.temperature)
            response_format = chat_completion_kwargs.get("response_format", {})
            if response_format:
                response_format_model = BaseOpenAIResponseFormat(**response_format)
                parameters["response_format"] = response_format_model.model_dump()

        if json_format and "response_format" not in parameters:
            parameters["response_format"] = {"force_json": True}

        try:
            response = self.client.chat.completions.create(**parameters)
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Error with OpenAI API: {e}")
