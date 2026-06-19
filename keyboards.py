from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


CLEAR_DIALOG_BUTTON = "🧹 Очистить диалог"
SELECT_MODEL_BUTTON = "🤖 Выбрать модель"
SETTINGS_BUTTON = "⚙️ Настройки"
TEMPERATURE_BUTTON = "🌡 Температура"
MAX_TOKENS_BUTTON = "📏 Max tokens"
HELP_BUTTON = "ℹ️ Помощь"
BACK_BUTTON = "⬅️ Назад"
SETTINGS_BACK_BUTTON = "⬅️ К настройкам"


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=CLEAR_DIALOG_BUTTON)],
            [
                KeyboardButton(text=SELECT_MODEL_BUTTON),
                KeyboardButton(text=SETTINGS_BUTTON),
            ],
            [KeyboardButton(text=HELP_BUTTON)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Напишите сообщение",
    )


def settings_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEMPERATURE_BUTTON)],
            [KeyboardButton(text=MAX_TOKENS_BUTTON)],
            [KeyboardButton(text=BACK_BUTTON)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите параметр",
    )


def option_keyboard(
    option_names: list[str],
    back_button: str = BACK_BUTTON,
) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            *[[KeyboardButton(text=option_name)] for option_name in option_names],
            [KeyboardButton(text=back_button)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите значение",
    )


def model_keyboard(model_names: list[str]) -> ReplyKeyboardMarkup:
    return option_keyboard(model_names)
