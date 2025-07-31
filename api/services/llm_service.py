import asyncio
from datetime import time
import json
import os
from typing import AsyncGenerator, Dict, List, Optional
import aiohttp
from fastapi.logger import logger
import requests


class LLMService:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

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

        for attempt in range(self.max_retries):
            try:
                response = self.session.post(
                    url=url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()

                if not data.get('choices') or not data['choices'][0].get('message'):
                    raise ValueError("Invalid LLM response structure")

                return data

            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise Exception(
                        f"LLM API failed after {self.max_retries} attempts: {str(e)}")
                time.sleep(1 * (attempt + 1))  # Exponential backoff
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to decode LLM response: {str(e)}")
            except ValueError as e:
                raise Exception(f"LLM response validation failed: {str(e)}")

    async def stream_chat_completion(
        self,
        messages: List[Dict],
    ) -> AsyncGenerator[Dict, None]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "presence_penalty": 1.0,
        }

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            for attempt in range(self.max_retries):
                try:
                    async with session.post(url, headers=headers, json=payload) as response:
                        if response.status != 200:
                            error = await response.text()
                            raise Exception(f"LLM API error: {error}")

                        async for line in response.content:
                            if line.startswith(b"data: "):
                                chunk = line[6:].strip()
                                if chunk != b"[DONE]":
                                    try:
                                        data = json.loads(chunk)
                                        if not data.get('choices'):
                                            continue
                                        yield data
                                    except json.JSONDecodeError:
                                        continue
                        return  # Success - exit retry loop

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt == self.max_retries - 1:
                        logger.error(
                            f"LLM streaming failed after {self.max_retries} attempts: {str(e)}")
                        raise
                    await asyncio.sleep(1 * (attempt + 1))


def get_llm(
    api_key: Optional[str] = None,
    base_url: str = "https://openrouter.ai/api/v1",
    model: str = "deepseek/deepseek-r1-0528:free",
    temperature: float = 0.1,
    max_tokens: int = 500,
    timeout: int = 60,
    max_retries: int = 3,
) -> LLMService:
    api_key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set in environment")
    return LLMService(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        max_retries=max_retries
    )
