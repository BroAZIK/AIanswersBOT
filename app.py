import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from settings import TOKEN
from details.handlers import button_callbacks, start, ignore_channel_posts, text, photo, stats


flask_app = Flask(__name__)


app = Application.builder().token(TOKEN).build()


app.add_handler(CallbackQueryHandler(button_callbacks))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("about", stats))
app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, ignore_channel_posts))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
app.add_handler(MessageHandler(filters.PHOTO, photo))


@flask_app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app.bot)
    asyncio.get_event_loop().create_task(app.process_update(update))
    return "ok", 200

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(app.initialize())
    loop.create_task(app.start())

    print("Webhook server ishlayapti 🚀")
    flask_app.run(host="0.0.0.0", port=5000, debug=True)
