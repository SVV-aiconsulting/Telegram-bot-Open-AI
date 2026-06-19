# Telegram AI Bot

Простой учебный Telegram-бот на Python: `aiogram 3.x` + OpenAI Chat Completions API через `aiohttp`.

Бот хранит историю сообщений каждого пользователя, отправляет ее в OpenAI API и сохраняет контекст между перезапусками в `data/context.json`.

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка

Создайте файл `.env` рядом с кодом:

```env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
API_BASE_URL=https://api.openai.com/v1
PROXY_URL=socks5://127.0.0.1:1080
```

`API_BASE_URL` можно не указывать, тогда будет использован адрес `https://api.openai.com/v1`.

`PROXY_URL` нужен, если `api.telegram.org` или OpenAI API недоступны напрямую. Поддерживаются `http://`, `https://`, `socks5://`. Примеры для Clash/V2Ray: `http://127.0.0.1:7890` или `socks5://127.0.0.1:1080`.

## Запуск

```bash
python bot.py
```

## Кнопки

- `🧹 Очистить диалог` очищает историю текущего пользователя, но не сбрасывает выбранную модель.
- `🤖 Выбрать модель` открывает клавиатуру выбора модели.
- `ℹ️ Помощь` показывает краткую справку.
- `⬅️ Назад` возвращает главное меню.

## Модели

Доступные варианты:

- `GPT-4.1`
- `GPT-4.1 mini`
- `GPT-3.5 Turbo`

Выбранная модель хранится отдельно для каждого пользователя и сохраняется в `data/context.json`.

## Контекст

Файл `data/context.json` создается автоматически вместе с папкой `data`, если их нет. Если JSON пустой или поврежден, бот не падает: он начинает с пустого контекста и пишет warning в лог.

Контекст хранится в `data/context.json` до тех пор, пока пользователь не очистит диалог кнопкой `🧹 Очистить диалог` или пока файл не будет удален вручную.
