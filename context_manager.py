import json
import logging
from pathlib import Path
from typing import Any

from llm_config import (
    get_available_models,
    get_available_max_tokens,
    get_available_temperatures,
    get_default_max_tokens,
    get_default_model_display_name,
    get_default_temperature,
    get_max_history_messages,
)
from prompt_library import get_available_prompts, get_default_prompt_id, get_prompt_by_id


logger = logging.getLogger(__name__)


def get_available_prompt_ids() -> set[str]:
    return set(get_available_prompts())


class ContextManager:
    def __init__(self, file_path: str | Path = "data/context.json") -> None:
        self.file_path = Path(file_path)
        self.data: dict[str, dict[str, Any]] = {}
        self.load()

    def load(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists():
            self.data = {}
            self.save()
            return

        try:
            raw_content = self.file_path.read_text(encoding="utf-8")
            if not raw_content.strip():
                raise ValueError("context file is empty")

            loaded_data = json.loads(raw_content)
            if not isinstance(loaded_data, dict):
                raise ValueError("context file root is not an object")

            self.data = loaded_data
        except (json.JSONDecodeError, OSError, ValueError) as error:
            logger.warning("Could not load context from %s: %s", self.file_path, error)
            self.data = {}
            self.save()

    def save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get_context(self, user_id: int | str) -> list[dict[str, str]]:
        user_data = self._get_user_data(user_id)
        return user_data["messages"]

    def add_user_message(self, user_id: int | str, text: str) -> None:
        self._add_message(user_id, "user", text)

    def add_assistant_message(self, user_id: int | str, text: str) -> None:
        self._add_message(user_id, "assistant", text)

    def clear_context(self, user_id: int | str) -> None:
        user_data = self._get_user_data(user_id)
        user_data["messages"] = [self._system_message_for(user_data)]
        self.save()

    def get_user_prompt_id(self, user_id: int | str) -> str:
        user_data = self._get_user_data(user_id)
        return self._resolve_prompt_id(user_data)

    def get_user_prompt_title(self, user_id: int | str) -> str:
        prompt_id = self.get_user_prompt_id(user_id)
        prompt = get_prompt_by_id(prompt_id)
        return prompt.title if prompt else prompt_id

    def set_user_prompt(self, user_id: int | str, prompt_id: str) -> None:
        if prompt_id not in get_available_prompt_ids():
            raise ValueError(f"Unknown prompt: {prompt_id}")

        user_data = self._get_user_data(user_id)
        user_data["prompt_id"] = prompt_id
        user_data["messages"] = [self._system_message_for(user_data)]
        self.save()

    def get_user_model(self, user_id: int | str) -> str:
        user_data = self._get_user_data(user_id)
        model_display_name = user_data.get("model")
        if model_display_name in get_available_models():
            return model_display_name

        default_model = get_default_model_display_name()
        user_data["model"] = default_model
        self.save()
        return default_model

    def set_user_model(self, user_id: int | str, model_display_name: str) -> None:
        if model_display_name not in get_available_models():
            raise ValueError(f"Unknown model: {model_display_name}")

        user_data = self._get_user_data(user_id)
        user_data["model"] = model_display_name
        self.save()

    def get_user_temperature(self, user_id: int | str) -> float:
        user_data = self._get_user_data(user_id)
        return user_data["temperature"]

    def set_user_temperature(self, user_id: int | str, temperature: float) -> None:
        available_values = set(get_available_temperatures().values())
        if temperature not in available_values:
            raise ValueError(f"Unknown temperature: {temperature}")

        user_data = self._get_user_data(user_id)
        user_data["temperature"] = temperature
        self.save()

    def get_user_max_tokens(self, user_id: int | str) -> int:
        user_data = self._get_user_data(user_id)
        return user_data["max_tokens"]

    def set_user_max_tokens(self, user_id: int | str, max_tokens: int) -> None:
        available_values = set(get_available_max_tokens().values())
        if max_tokens not in available_values:
            raise ValueError(f"Unknown max_tokens: {max_tokens}")

        user_data = self._get_user_data(user_id)
        user_data["max_tokens"] = max_tokens
        self.save()

    def _add_message(self, user_id: int | str, role: str, text: str) -> None:
        user_data = self._get_user_data(user_id)
        user_data["messages"].append({"role": role, "content": text})
        self._trim_history(user_id, user_data)
        self.save()

    def _get_user_data(self, user_id: int | str) -> dict[str, Any]:
        user_key = str(user_id)
        if user_key not in self.data or not isinstance(self.data[user_key], dict):
            user_data = self._new_user_data()
            user_data["messages"] = [self._system_message_for(user_data)]
            self.data[user_key] = user_data
            self.save()
            return user_data

        user_data = self.data[user_key]
        if user_data.get("model") not in get_available_models():
            user_data["model"] = get_default_model_display_name()

        user_data["temperature"] = self._normalize_temperature(user_data.get("temperature"))
        user_data["max_tokens"] = self._normalize_max_tokens(user_data.get("max_tokens"))

        if user_data.get("prompt_id") not in get_available_prompt_ids():
            user_data["prompt_id"] = get_default_prompt_id()

        messages = user_data.get("messages")
        if not isinstance(messages, list):
            user_data["messages"] = [self._system_message_for(user_data)]
        else:
            user_data["messages"] = self._normalize_messages(user_data, messages)

        self._trim_history(user_key, user_data)
        return user_data

    def _new_user_data(self) -> dict[str, Any]:
        return {
            "model": get_default_model_display_name(),
            "temperature": get_default_temperature(),
            "max_tokens": get_default_max_tokens(),
            "prompt_id": get_default_prompt_id(),
            "messages": [],
        }

    def _normalize_temperature(self, value: Any) -> float:
        try:
            temperature = float(value)
        except (TypeError, ValueError):
            return get_default_temperature()

        available_values = get_available_temperatures().values()
        if any(abs(temperature - option) < 0.001 for option in available_values):
            return temperature
        return get_default_temperature()

    def _normalize_max_tokens(self, value: Any) -> int:
        try:
            max_tokens = int(value)
        except (TypeError, ValueError):
            return get_default_max_tokens()

        if max_tokens in get_available_max_tokens().values():
            return max_tokens
        return get_default_max_tokens()

    def _resolve_prompt_id(self, user_data: dict[str, Any]) -> str:
        prompt_id = user_data.get("prompt_id")
        if prompt_id in get_available_prompt_ids():
            return prompt_id
        return get_default_prompt_id()

    def _system_message_for(self, user_data: dict[str, Any]) -> dict[str, str]:
        prompt = get_prompt_by_id(self._resolve_prompt_id(user_data))
        content = prompt.to_system_prompt() if prompt else ""
        return {"role": "system", "content": content}

    def _normalize_messages(
        self,
        user_data: dict[str, Any],
        messages: list[Any],
    ) -> list[dict[str, str]]:
        normalized_messages: list[dict[str, str]] = []
        system_added = False

        for message in messages:
            if not isinstance(message, dict):
                continue

            role = message.get("role")
            content = message.get("content")
            if role not in {"system", "user", "assistant"} or not isinstance(content, str):
                continue

            if role == "system":
                if system_added:
                    continue
                normalized_messages.insert(0, self._system_message_for(user_data))
                system_added = True
            else:
                normalized_messages.append({"role": role, "content": content})

        if not system_added:
            normalized_messages.insert(0, self._system_message_for(user_data))

        return normalized_messages

    def _trim_history(self, user_id: int | str, user_data: dict[str, Any]) -> None:
        messages = user_data["messages"]
        system_message = (
            messages[0]
            if messages and messages[0]["role"] == "system"
            else self._system_message_for(user_data)
        )
        regular_messages = [message for message in messages if message["role"] != "system"]
        user_data["messages"] = [system_message] + regular_messages[-get_max_history_messages():]
