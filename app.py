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

bot_app = Application.builder().token(TOKEN).build()

bot_app.add_handler(CallbackQueryHandler(button_callbacks))
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("about", stats))
bot_app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, ignore_channel_posts))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
bot_app.add_handler(MessageHandler(filters.PHOTO, photo))


@flask_app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(silent=True)
        print("Kelgan xom data:", request.data)
        print("Kelgan JSON:", data)

        if not data:
            return "No JSON received", 400

        update = Update.de_json(data, bot_app.bot)
        asyncio.get_event_loop().create_task(bot_app.process_update(update))
        return "ok", 200
    except Exception as e:
        import traceback
        print("Webhook error:", traceback.format_exc())
        return "Internal Server Error", 500



@flask_app.route("/webhook/", methods=["GET"])
def stage():
    return "Webhook is running...!"


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(bot_app.initialize())
    loop.create_task(bot_app.start())

    print("Webhook server ishlayapti 🚀")
    flask_app.run(host="0.0.0.0", port=5000, debug=True)

application = flask_app
