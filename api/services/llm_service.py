from typing import Dict, List, Optional
import requests


class LLMService:

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: int,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    def chat_completion(
        self,
        messages: List[Dict],
    ) -> Dict:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "presence_penalty": 1.0,
        }

        response = requests.post(
            url=url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()


def get_llm(
    api_key: str = "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",
    base_url: str = "https://openrouter.ai/api/v1",
    model: str = "deepseek/deepseek-r1-0528:free",
    temperature: float = 0.1,  # lower is faster
    max_tokens: int = 500,  # shorter is faster
    timeout: int = 30
) -> LLMService:
    return LLMService(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )
