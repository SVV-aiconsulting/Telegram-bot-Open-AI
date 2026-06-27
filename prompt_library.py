import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)

DEFAULT_PROMPTS_FILE = Path("prompts/prompts.json")

REQUIRED_PROMPT_FIELDS = ("title", "role", "context", "task")

_BUILTIN_FALLBACK = {
    "default_prompt_id": "default",
    "prompts": {
        "default": {
            "title": "💬 Стандартный ассистент",
            "role": "ты полезный AI-ассистент.",
            "context": "пользователь общается с тобой в свободной форме на любые темы.",
            "task": "отвечай ясно, дружелюбно и по делу.",
        },
    },
}


@dataclass(frozen=True)
class PresetPrompt:
    id: str
    title: str
    role: str
    context: str
    task: str
    response_format: str | None = None

    def to_system_prompt(self) -> str:
        parts = [
            f"Роль: {self.role}",
            f"Контекст: {self.context}",
            f"Задача: {self.task}",
        ]
        if self.response_format:
            parts.append(f"Формат ответа: {self.response_format}")
        return "\n\n".join(parts)


class PromptLibrary:
    def __init__(self, file_path: str | Path = DEFAULT_PROMPTS_FILE) -> None:
        self.file_path = Path(file_path)
        self.default_prompt_id = "default"
        self.prompts: dict[str, PresetPrompt] = {}
        self.load()

    def load(self) -> None:
        raw_data = self._read_file()
        self.default_prompt_id, self.prompts = self._parse(raw_data)

    def reload(self) -> None:
        self.load()

    def get_default_prompt_id(self) -> str:
        return self.default_prompt_id

    def get_prompt(self, prompt_id: str) -> PresetPrompt | None:
        return self.prompts.get(prompt_id)

    def get_all(self) -> dict[str, PresetPrompt]:
        return self.prompts.copy()

    def get_titles(self) -> list[str]:
        return [prompt.title for prompt in self.prompts.values()]

    def get_id_by_title(self, title: str) -> str | None:
        for prompt in self.prompts.values():
            if prompt.title == title:
                return prompt.id
        return None

    def _read_file(self) -> dict[str, Any]:
        if not self.file_path.exists():
            logger.warning("Prompts file not found at %s, using built-in fallback", self.file_path)
            return _BUILTIN_FALLBACK.copy()

        try:
            raw_content = self.file_path.read_text(encoding="utf-8")
            if not raw_content.strip():
                raise ValueError("prompts file is empty")

            loaded_data = json.loads(raw_content)
            if not isinstance(loaded_data, dict):
                raise ValueError("prompts file root is not an object")

            return loaded_data
        except (json.JSONDecodeError, OSError, ValueError) as error:
            logger.warning("Could not load prompts from %s: %s", self.file_path, error)
            return _BUILTIN_FALLBACK.copy()

    def _parse(self, raw_data: dict[str, Any]) -> tuple[str, dict[str, PresetPrompt]]:
        prompts_raw = raw_data.get("prompts")
        if not isinstance(prompts_raw, dict) or not prompts_raw:
            logger.warning("Invalid prompts section, using built-in fallback")
            return self._parse(_BUILTIN_FALLBACK)

        parsed: dict[str, PresetPrompt] = {}
        for prompt_id, prompt_data in prompts_raw.items():
            if not isinstance(prompt_id, str) or not prompt_id.strip():
                continue
            if not isinstance(prompt_data, dict):
                logger.warning("Skipping prompt %r: entry is not an object", prompt_id)
                continue

            prompt = self._parse_prompt(prompt_id.strip(), prompt_data)
            if prompt is not None:
                parsed[prompt.id] = prompt

        if not parsed:
            logger.warning("No valid prompts found, using built-in fallback")
            return self._parse(_BUILTIN_FALLBACK)

        titles = [prompt.title for prompt in parsed.values()]
        if len(titles) != len(set(titles)):
            logger.warning("Duplicate prompt titles detected in %s", self.file_path)

        default_prompt_id = raw_data.get("default_prompt_id", "default")
        if not isinstance(default_prompt_id, str) or default_prompt_id not in parsed:
            default_prompt_id = next(iter(parsed))

        return default_prompt_id, parsed

    def _parse_prompt(self, prompt_id: str, prompt_data: dict[str, Any]) -> PresetPrompt | None:
        missing_fields = [
            field for field in REQUIRED_PROMPT_FIELDS
            if not isinstance(prompt_data.get(field), str) or not prompt_data[field].strip()
        ]
        if missing_fields:
            logger.warning(
                "Skipping prompt %r: missing or empty fields: %s",
                prompt_id,
                ", ".join(missing_fields),
            )
            return None

        response_format = prompt_data.get("response_format")
        if response_format is not None and (
            not isinstance(response_format, str) or not response_format.strip()
        ):
            response_format = None

        return PresetPrompt(
            id=prompt_id,
            title=prompt_data["title"].strip(),
            role=prompt_data["role"].strip(),
            context=prompt_data["context"].strip(),
            task=prompt_data["task"].strip(),
            response_format=response_format.strip() if isinstance(response_format, str) else None,
        )


_library = PromptLibrary()


def get_library() -> PromptLibrary:
    return _library


def get_available_prompts() -> dict[str, PresetPrompt]:
    return _library.get_all()


def get_prompt_by_id(prompt_id: str) -> PresetPrompt | None:
    return _library.get_prompt(prompt_id)


def get_default_prompt_id() -> str:
    return _library.get_default_prompt_id()


def get_prompt_titles() -> list[str]:
    return _library.get_titles()


def get_prompt_id_by_title(title: str) -> str | None:
    return _library.get_id_by_title(title)
