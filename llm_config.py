AVAILABLE_MODELS = {
    "GPT-4.1": "gpt-4.1",
    "GPT-4.1 mini": "gpt-4.1-mini",
    "GPT-3.5 Turbo": "gpt-3.5-turbo",
}

DEFAULT_MODEL_DISPLAY_NAME = "GPT-4.1 mini"
TEMPERATURE = 0.7
MAX_TOKENS = 1000
MAX_HISTORY_MESSAGES = 20
SYSTEM_PROMPT = "Ты полезный AI-ассистент. Отвечай ясно, дружелюбно и по делу."

AVAILABLE_TEMPERATURES = {
    "0.0 — точный": 0.0,
    "0.3 — спокойный": 0.3,
    "0.7 — сбалансированный": 0.7,
    "1.0 — творческий": 1.0,
    "1.5 — смелый": 1.5,
}

AVAILABLE_MAX_TOKENS = {
    "256 токенов": 256,
    "500 токенов": 500,
    "1000 токенов": 1000,
    "2000 токенов": 2000,
    "4000 токенов": 4000,
}


def get_available_models() -> dict[str, str]:
    if isinstance(AVAILABLE_MODELS, dict) and AVAILABLE_MODELS:
        valid_models = {
            display_name: model_id
            for display_name, model_id in AVAILABLE_MODELS.items()
            if isinstance(display_name, str)
            and display_name.strip()
            and isinstance(model_id, str)
            and model_id.strip()
        }
        if valid_models:
            return valid_models

    return {"GPT-4.1 mini": "gpt-4.1-mini"}


def get_default_model_display_name() -> str:
    models = get_available_models()
    if DEFAULT_MODEL_DISPLAY_NAME in models:
        return DEFAULT_MODEL_DISPLAY_NAME
    return next(iter(models))


def get_temperature() -> float:
    try:
        temperature = float(TEMPERATURE)
    except (TypeError, ValueError):
        return 0.7
    return temperature if 0 <= temperature <= 2 else 0.7


def get_max_tokens() -> int:
    try:
        max_tokens = int(MAX_TOKENS)
    except (TypeError, ValueError):
        return 1000
    return max_tokens if max_tokens > 0 else 1000


def get_max_history_messages() -> int:
    try:
        max_messages = int(MAX_HISTORY_MESSAGES)
    except (TypeError, ValueError):
        return 20
    return max_messages if max_messages > 0 else 20


def get_available_temperatures() -> dict[str, float]:
    if isinstance(AVAILABLE_TEMPERATURES, dict) and AVAILABLE_TEMPERATURES:
        valid = {
            name: float(value)
            for name, value in AVAILABLE_TEMPERATURES.items()
            if isinstance(name, str) and name.strip() and isinstance(value, (int, float))
        }
        if valid:
            return valid
    return {"0.7 — сбалансированный": 0.7}


def get_available_max_tokens() -> dict[str, int]:
    if isinstance(AVAILABLE_MAX_TOKENS, dict) and AVAILABLE_MAX_TOKENS:
        valid = {
            name: int(value)
            for name, value in AVAILABLE_MAX_TOKENS.items()
            if isinstance(name, str) and name.strip() and isinstance(value, (int, float)) and int(value) > 0
        }
        if valid:
            return valid
    return {"1000 токенов": 1000}


def get_default_temperature() -> float:
    return get_temperature()


def get_default_max_tokens() -> int:
    return get_max_tokens()


def format_temperature(value: float) -> str:
    for name, temperature in get_available_temperatures().items():
        if abs(temperature - value) < 0.001:
            return name
    return f"{value:g}"


def format_max_tokens(value: int) -> str:
    for name, max_tokens in get_available_max_tokens().items():
        if max_tokens == value:
            return name
    return f"{value} токенов"


def get_system_prompt() -> str:
    if isinstance(SYSTEM_PROMPT, str) and SYSTEM_PROMPT.strip():
        return SYSTEM_PROMPT
    return "Ты полезный AI-ассистент. Отвечай ясно, дружелюбно и по делу."
