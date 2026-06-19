import logging
from typing import Any

import aiohttp

from config import Config


logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, config: Config, timeout_seconds: int = 60) -> None:
        self.config = config
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    async def create_chat_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        url = f"{self.config.api_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with self._create_session() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data: dict[str, Any] = await response.json(content_type=None)

                    if response.status >= 400:
                        error_message = self._extract_error_message(response_data)
                        logger.warning("OpenAI API error %s: %s", response.status, error_message)
                        raise RuntimeError(f"OpenAI API error {response.status}: {error_message}")

                    return response_data["choices"][0]["message"]["content"].strip()
        except aiohttp.ClientError as error:
            logger.warning("Network error while calling OpenAI API: %s", error)
            raise RuntimeError("Could not connect to OpenAI API") from error
        except (KeyError, IndexError, TypeError) as error:
            logger.warning("Unexpected OpenAI API response format: %s", error)
            raise RuntimeError("Unexpected OpenAI API response format") from error

    def _create_session(self) -> aiohttp.ClientSession:
        if self.config.proxy_url:
            from aiohttp_socks import ProxyConnector

            connector = ProxyConnector.from_url(self.config.proxy_url)
            return aiohttp.ClientSession(connector=connector, timeout=self.timeout)
        return aiohttp.ClientSession(timeout=self.timeout)

    def _extract_error_message(self, response_data: dict[str, Any]) -> str:
        error = response_data.get("error")
        if isinstance(error, dict) and isinstance(error.get("message"), str):
            return error["message"]
        return "unknown error"
