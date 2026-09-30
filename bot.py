import os
import logging
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

FREE_LIMIT = 3
DB_FILE = Path("users.txt")

logging.basicConfig(level=logging.INFO)

MODES = {
    "description": "Описание товара",
    "title": "Название товара",
    "benefits": "Преимущества",
    "seo": "SEO-ключи",
    "ad": "Рекламный текст",
    "video": "Сценарий видео",
}


def get_count(user_id):
    if not DB_FILE.exists():
        return 0

    for line in DB_FILE.read_text(encoding="utf-8").splitlines():
        parts = line.split(":")

        if len(parts) == 2 and parts[0] == str(user_id):
            return int(parts[1])

    return 0


def set_count(user_id, count):
    rows = []
    found = False

    if DB_FILE.exists():
        for line in DB_FILE.read_text(encoding="utf-8").splitlines():
            parts = line.split(":")

            if len(parts) == 2 and parts[0] == str(user_id):
                rows.append(f"{user_id}:{count}")
                found = True
            elif line.strip():
                rows.append(line)

    if not found:
        rows.append(f"{user_id}:{count}")

    DB_FILE.write_text("\n".join(rows), encoding="utf-8")


def menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📝 Описание",
                callback_data="description"
            ),
            InlineKeyboardButton(
                "🏷 Название",
                callback_data="title"
            ),
        ],
        [
            InlineKeyboardButton(
                "🔥 Преимущества",
                callback_data="benefits"
            ),
            InlineKeyboardButton(
                "🔎 SEO",
                callback_data="seo"
            ),
        ],
        [
            InlineKeyboardButton(
                "📢 Реклама",
                callback_data="ad"
            ),
            InlineKeyboardButton(
                "🎬 Сценарий",
                callback_data="video"
            ),
        ],
        [
            InlineKeyboardButton(
                "💎 Тариф",
                callback_data="tariff"
            )
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "🤖 <b>SellAI</b>\n\n"
        "Генерирую тексты для товаров за несколько секунд.\n\n"
        "🎁 Первые 3 генерации бесплатно.\n\n"
        "Выбери, что нужно создать:",
        parse_mode="HTML",
        reply_markup=menu(),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    mode = query.data

    if mode == "tariff":
        await query.message.reply_text(
            "💎 <b>Тарифы</b>\n\n"
            "🎁 Free — 3 генерации\n"
            "⚡ Pro — 499 ₽/месяц\n\n"
            "Оплата будет подключена после тестирования MVP.",
            parse_mode="HTML",
            reply_markup=menu(),
        )
        return

    context.user_data["mode"] = mode

    await query.message.reply_text(
        f"Выбрано: <b>{MODES[mode]}</b>.\n\n"
        "Отправь название товара и его характеристики.\n\n"
        "Например:\n"
        "<i>Термокружка 500 мл, нержавеющая "
        "сталь, держит тепло 8 часов, чёрная.</i>",
        parse_mode="HTML",
    )


def generate_content(mode, product):

    if mode == "description":
        return (
            "📝 <b>Описание</b>\n\n"
            f"{product}\n\n"
            "Практичный товар с понятными преимуществами "
            "и удобным использованием. Подходит для "
            "повседневных задач и станет полезным "
            "дополнением для дома, работы или поездок."
        )

    if mode == "title":
        return (
            "🏷 <b>Варианты названия</b>\n\n"
            f"1. {product}\n"
            f"2. {product} | Практичный выбор на каждый день\n"
            f"3. {product} | Удобный и функциональный\n"
            f"4. {product} | Идеально для дома и поездок\n"
            f"5. {product} | Подарочный вариант"
        )

    if mode == "benefits":
        return (
            "🔥 <b>Преимущества</b>\n\n"
            "• Удобное использование\n"
            "• Практичный формат\n"
            "• Подходит для ежедневного применения\n"
            "• Универсальный вариант\n"
            "• Простая эксплуатация\n\n"
            f"Товар: {product}"
        )

    if mode == "seo":
        return (
            "🔎 <b>SEO-ключи</b>\n\n"
            f"{product}\n"
            f"купить {product}\n"
            f"{product} цена\n"
            f"{product} заказать\n"
            f"{product} для дома\n"
            f"{product} подарок"
        )

    if mode == "ad":
        return (
            "📢 <b>Рекламный текст</b>\n\n"
            f"Ищете удобный и практичный вариант? "
            f"{product} создан для тех, кто ценит "
            "функциональность и комфорт. Узнайте "
            "подробности и выберите подходящий вариант."
        )

    return (
        "🎬 <b>Сценарий короткого видео</b>\n\n"
        "0–3 сек: Показываем товар крупным планом.\n"
        "3–7 сек: Показываем ключевую характеристику.\n"
        "7–12 сек: Демонстрируем товар в использовании.\n"
        "12–15 сек: Показываем главный плюс и призыв "
        "посмотреть товар.\n\n"
        f"Товар: {product}"
    )


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mode = context.user_data.get("mode")

    if not mode:
        await update.message.reply_text(
            "Сначала выбери действие в меню.",
            reply_markup=menu(),
        )
        return

    user_id = update.effective_user.id
    count = get_count(user_id)

    if count >= FREE_LIMIT:
        await update.message.reply_text(
            "🎁 Бесплатный лимит закончился.\n\n"
            "💎 Pro: 499 ₽/месяц.\n\n"
            "Оплату подключим после тестирования.",
            reply_markup=menu(),
        )
        return

    product = update.message.text.strip()

    result = generate_content(mode, product)

    set_count(user_id, count + 1)

    await update.message.reply_text(
        result
        + f"\n\n"
        f"<i>Осталось бесплатных генераций: "
        f"{FREE_LIMIT - count - 1}</i>",
        parse_mode="HTML",
        reply_markup=menu(),
    )

    context.user_data.clear()


def main():

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "Не задан TELEGRAM_BOT_TOKEN"
        )

    app = (
        Application
        .builder()
        .token(token)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(button)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message
        )
    )

    print(
        "SellAI запущен. "
        "Ctrl+C для остановки."
    )

    app.run_polling()


if __name__ == "__main__":
    main()