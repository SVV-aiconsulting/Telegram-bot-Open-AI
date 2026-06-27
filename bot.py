import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart
from aiogram.types import Message

from api_client import ApiClient
from config import load_config
from context_manager import ContextManager
from keyboards import (
    BACK_BUTTON,
    CLEAR_DIALOG_BUTTON,
    HELP_BUTTON,
    MAX_TOKENS_BUTTON,
    PROMPTS_BUTTON,
    SELECT_MODEL_BUTTON,
    SETTINGS_BACK_BUTTON,
    SETTINGS_BUTTON,
    TEMPERATURE_BUTTON,
    main_keyboard,
    model_keyboard,
    option_keyboard,
    settings_keyboard,
)
from llm_config import (
    format_max_tokens,
    format_temperature,
    get_available_max_tokens,
    get_available_models,
    get_available_temperatures,
)
from prompt_library import get_prompt_id_by_title, get_prompt_titles


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

config = load_config()
context_manager = ContextManager()
api_client = ApiClient(config)
available_models = get_available_models()
available_temperatures = get_available_temperatures()
available_max_tokens = get_available_max_tokens()
available_prompt_titles = get_prompt_titles()


def create_bot() -> Bot:
    if config.proxy_url:
        logger.info("Using proxy for Telegram API")
        session = AiohttpSession(proxy=config.proxy_url)
        return Bot(token=config.bot_token, session=session)
    return Bot(token=config.bot_token)


def user_settings_text(user_id: int) -> str:
    model_name = context_manager.get_user_model(user_id)
    prompt_title = context_manager.get_user_prompt_title(user_id)
    temperature = format_temperature(context_manager.get_user_temperature(user_id))
    max_tokens = format_max_tokens(context_manager.get_user_max_tokens(user_id))
    return (
        f"Роль: {prompt_title}\n"
        f"Модель: {model_name}\n"
        f"Температура: {temperature}\n"
        f"Max tokens: {max_tokens}"
    )


bot = create_bot()
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Привет! Я AI-бот с памятью диалога.\n\n"
        f"{user_settings_text(message.from_user.id)}\n\n"
        "Напишите сообщение, и я отвечу с учетом истории.",
        reply_markup=main_keyboard(),
    )


@dp.message(F.text == HELP_BUTTON)
async def help_message(message: Message) -> None:
    await message.answer(
        "Я сохраняю историю вашего диалога и отправляю ее в OpenAI API.\n\n"
        f"{user_settings_text(message.from_user.id)}\n\n"
        "Кнопка очистки удаляет только историю сообщений. "
        "Модель, роль и настройки генерации сохраняются.",
        reply_markup=main_keyboard(),
    )


@dp.message(F.text == CLEAR_DIALOG_BUTTON)
async def clear_dialog(message: Message) -> None:
    context_manager.clear_context(message.from_user.id)
    await message.answer(
        "Диалог очищен. Роль, модель и настройки генерации сохранены.",
        reply_markup=main_keyboard(),
    )


@dp.message(F.text == PROMPTS_BUTTON)
async def choose_prompt(message: Message) -> None:
    await message.answer(
        f"Текущая роль: {context_manager.get_user_prompt_title(message.from_user.id)}\n\n"
        "Выберите роль из библиотеки промптов:",
        reply_markup=option_keyboard(available_prompt_titles),
    )


@dp.message(F.text.in_(available_prompt_titles))
async def set_prompt(message: Message) -> None:
    prompt_id = get_prompt_id_by_title(message.text)
    if prompt_id is None:
        await message.answer(
            "Не удалось найти выбранный промпт.",
            reply_markup=main_keyboard(),
        )
        return

    context_manager.set_user_prompt(message.from_user.id, prompt_id)
    await message.answer(
        f"Роль выбрана: {message.text}\n"
        "История диалога сброшена. Напишите ваш запрос.",
        reply_markup=main_keyboard(),
    )


@dp.message(F.text == SELECT_MODEL_BUTTON)
async def choose_model(message: Message) -> None:
    await message.answer(
        "Выберите модель:",
        reply_markup=model_keyboard(list(available_models.keys())),
    )


@dp.message(F.text == SETTINGS_BUTTON)
async def open_settings(message: Message) -> None:
    await message.answer(
        "Настройки генерации:\n\n"
        f"{user_settings_text(message.from_user.id)}",
        reply_markup=settings_keyboard(),
    )


@dp.message(F.text == TEMPERATURE_BUTTON)
async def choose_temperature(message: Message) -> None:
    await message.answer(
        "Выберите температуру:",
        reply_markup=option_keyboard(
            list(available_temperatures.keys()),
            back_button=SETTINGS_BACK_BUTTON,
        ),
    )


@dp.message(F.text == MAX_TOKENS_BUTTON)
async def choose_max_tokens(message: Message) -> None:
    await message.answer(
        "Выберите лимит токенов:",
        reply_markup=option_keyboard(
            list(available_max_tokens.keys()),
            back_button=SETTINGS_BACK_BUTTON,
        ),
    )


@dp.message(F.text == SETTINGS_BACK_BUTTON)
async def back_to_settings(message: Message) -> None:
    await message.answer(
        "Настройки генерации:\n\n"
        f"{user_settings_text(message.from_user.id)}",
        reply_markup=settings_keyboard(),
    )


@dp.message(F.text == BACK_BUTTON)
async def back_to_main(message: Message) -> None:
    await message.answer("Главное меню.", reply_markup=main_keyboard())


@dp.message(F.text.in_(available_models.keys()))
async def set_model(message: Message) -> None:
    context_manager.set_user_model(message.from_user.id, message.text)
    await message.answer(
        f"Модель выбрана: {message.text}",
        reply_markup=main_keyboard(),
    )


@dp.message(F.text.in_(available_temperatures.keys()))
async def set_temperature(message: Message) -> None:
    context_manager.set_user_temperature(
        message.from_user.id,
        available_temperatures[message.text],
    )
    await message.answer(
        f"Температура выбрана: {message.text}",
        reply_markup=main_keyboard(),
    )


@dp.message(F.text.in_(available_max_tokens.keys()))
async def set_max_tokens(message: Message) -> None:
    context_manager.set_user_max_tokens(
        message.from_user.id,
        available_max_tokens[message.text],
    )
    await message.answer(
        f"Max tokens выбрано: {message.text}",
        reply_markup=main_keyboard(),
    )


@dp.message(F.text)
async def chat(message: Message) -> None:
    user_id = message.from_user.id
    user_text = message.text

    context_manager.add_user_message(user_id, user_text)
    model_display_name = context_manager.get_user_model(user_id)
    model_id = available_models[model_display_name]

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        answer = await api_client.create_chat_completion(
            model=model_id,
            messages=context_manager.get_context(user_id),
            temperature=context_manager.get_user_temperature(user_id),
            max_tokens=context_manager.get_user_max_tokens(user_id),
        )
    except RuntimeError as error:
        logger.warning("Could not get assistant response for user %s: %s", user_id, error)
        await message.answer(
            "Не получилось получить ответ от API. Попробуйте еще раз чуть позже.",
            reply_markup=main_keyboard(),
        )
        return

    context_manager.add_assistant_message(user_id, answer)
    await message.answer(answer, reply_markup=main_keyboard())


async def main() -> None:
    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
