import os
import asyncio
from flask import Flask, request

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)


TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

app = Flask(__name__)

telegram_app = (
    Application
    .builder()
    .token(TOKEN)
    .updater(None)
    .build()
)


MODES = {
    "description": "Описание товара",
    "title": "Название товара",
    "benefits": "Преимущества",
    "seo": "SEO-ключи",
    "ad": "Рекламный текст",
    "video": "Сценарий видео",
}


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
            )
        ],

        [
            InlineKeyboardButton(
                "🔥 Преимущества",
                callback_data="benefits"
            ),
            InlineKeyboardButton(
                "🔎 SEO",
                callback_data="seo"
            )
        ],

        [
            InlineKeyboardButton(
                "📢 Реклама",
                callback_data="ad"
            ),
            InlineKeyboardButton(
                "🎬 Сценарий",
                callback_data="video"
            )
        ],

        [
            InlineKeyboardButton(
                "💎 Тариф",
                callback_data="tariff"
            )
        ]

    ])


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(

        "🤖 <b>SellAI</b>\n\n"

        "Генерирую контент для товаров.\n\n"

        "🎁 Первые 3 генерации бесплатно.\n\n"

        "Выбери нужную функцию:",

        parse_mode="HTML",

        reply_markup=menu()
    )


async def button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    mode = query.data

    if mode == "tariff":

        await query.message.reply_text(

            "💎 <b>SellAI PRO</b>\n\n"

            "⚡ Безлимитные генерации\n"
            "📝 Описания\n"
            "🏷 Названия\n"
            "🔥 Преимущества\n"
            "🔎 SEO\n"
            "📢 Реклама\n"
            "🎬 Сценарии\n\n"

            "<b>499 ₽ / месяц</b>",

            parse_mode="HTML",

            reply_markup=menu()
        )

        return


    context.user_data["mode"] = mode


    await query.message.reply_text(

        f"Выбрано: <b>{MODES[mode]}</b>\n\n"

        "Отправь название товара и его характеристики.\n\n"

        "Например:\n"

        "<i>Термокружка 500 мл, сталь, "
        "держит тепло 8 часов, чёрная</i>",

        parse_mode="HTML"
    )


def generate(mode, product):

    if mode == "description":

        return (

            "📝 <b>Описание</b>\n\n"

            f"{product}\n\n"

            "Практичный и удобный товар для "
            "ежедневного использования. "
            "Сочетает функциональность, удобство "
            "и современный дизайн."

        )


    if mode == "title":

        return (

            "🏷 <b>5 вариантов названия</b>\n\n"

            f"1. {product}\n"
            f"2. {product} | Практичный выбор\n"
            f"3. {product} | Удобный формат\n"
            f"4. {product} | Для дома и поездок\n"
            f"5. {product} | Отличный подарок"

        )


    if mode == "benefits":

        return (

            "🔥 <b>Преимущества</b>\n\n"

            "• Удобный формат\n"
            "• Простое использование\n"
            "• Практичное решение\n"
            "• Подходит для ежедневного применения\n"
            "• Универсальный вариант\n\n"

            f"Товар: {product}"

        )


    if mode == "seo":

        return (

            "🔎 <b>SEO-ключи</b>\n\n"

            f"купить {product}\n"
            f"{product} цена\n"
            f"{product} заказать\n"
            f"{product} для дома\n"
            f"{product} подарок\n"
            f"{product} отзывы"

        )


    if mode == "ad":

        return (

            "📢 <b>Рекламный текст</b>\n\n"

            f"Ищете удобный вариант? {product} "
            "создан для тех, кто ценит комфорт "
            "и функциональность.\n\n"

            "Закажите прямо сейчас и оцените "
            "удобство самостоятельно."

        )


    return (

        "🎬 <b>Сценарий короткого видео</b>\n\n"

        "0–3 сек: крупный план товара.\n"
        "3–7 сек: показываем характеристику.\n"
        "7–12 сек: демонстрируем использование.\n"
        "12–15 сек: показываем преимущество.\n"
        "15 сек: призыв перейти к товару.\n\n"

        f"Товар: {product}"

    )


async def message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    mode = context.user_data.get("mode")


    if not mode:

        await update.message.reply_text(

            "Сначала выбери функцию:",

            reply_markup=menu()

        )

        return


    product = update.message.text

    result = generate(
        mode,
        product
    )


    await update.message.reply_text(

        result,

        parse_mode="HTML",

        reply_markup=menu()

    )


    context.user_data.clear()


telegram_app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


telegram_app.add_handler(
    CallbackQueryHandler(
        button
    )
)


telegram_app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message
    )
)


async def process_update(data):

    update = Update.de_json(
        data,
        telegram_app.bot
    )

    await telegram_app.process_update(
        update
    )


@app.route(
    "/telegram",
    methods=["POST"]
)
def telegram_webhook():

    data = request.get_json(
        force=True
    )

    asyncio.run(
        process_update(data)
    )

    return "OK"


@app.route("/")
def home():

    return "SellAI is running."


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            8080
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )