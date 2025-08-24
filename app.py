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

# Telegram bot application
bot_app = Application.builder().token(TOKEN).build()

# Handlers
bot_app.add_handler(CallbackQueryHandler(button_callbacks))
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("about", stats))
bot_app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, ignore_channel_posts))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
bot_app.add_handler(MessageHandler(filters.PHOTO, photo))


@flask_app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, bot_app.bot)
        await bot_app.process_update(update)
        return "ok", 200
    except Exception as e:
        import traceback
        print("Webhook error:", traceback.format_exc())
        return "Internal Server Error", 500


@flask_app.route("/webhook/", methods=["GET"])
def stage():
    return "Webhook is running...!"


if __name__ == "__main__":
    async def main():
        await bot_app.initialize()
        await bot_app.start()
        print("Webhook server ishlayapti 🚀")
        flask_app.run(host="0.0.0.0", port=5000, debug=True)

    asyncio.run(main())

# Gunicorn uchun entrypoint
application = flask_app
