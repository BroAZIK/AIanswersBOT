import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from settings import TOKEN
from details.handlers import button_callbacks, start, ignore_channel_posts, text, photo, stats

# Loggerni sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app yaratish
flask_app = Flask(__name__)

# Global application o'zgaruvchisi
telegram_app = None

# Global event loop
event_loop = None

# Botni ishga tushirish
def initialize_bot():
    global telegram_app, event_loop
    try:
        # Yangi event loop yaratish
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        
        # Telegram Bot Application yaratish
        telegram_app = Application.builder().token(TOKEN).build()
        logger.info("Telegram app muvaffaqiyatli yaratildi")

        # Handlerlarni Telegram app ga qo'shish
        telegram_app.add_handler(CallbackQueryHandler(button_callbacks))
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(CommandHandler("about", stats))
        telegram_app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, ignore_channel_posts))
        telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
        telegram_app.add_handler(MessageHandler(filters.PHOTO, photo))
        logger.info("Barcha handlerlar qo'shildi")

        # Application ni ishga tushirish
        event_loop.run_until_complete(telegram_app.initialize())
        logger.info("Telegram app initialized")

        return True
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik: {e}")
        return False

# Async funksiyani ishga tushirish
def run_async(coro):
    try:
        if event_loop and not event_loop.is_closed():
            return event_loop.run_until_complete(coro)
        else:
            # Agar event loop yopiq bo'lsa, yangi yaratish
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
    except Exception as e:
        logger.error(f"Async funksiyani ishga tushirishda xatolik: {e}")
        raise

# Webhook endpoint
@flask_app.route('/webhook', methods=['POST'])
def webhook():
    try:
        if not telegram_app:
            logger.error("Telegram app ishga tushmagan")
            return "Error: Bot not initialized", 500

        if request.method == "POST":
            json_data = request.get_json(force=True)
            logger.info(f"Qabul qilingan yangi xabar")
            
            update = Update.de_json(json_data, telegram_app.bot)
            
            # Update ni qayta ishlash
            run_async(telegram_app.process_update(update))
            logger.info("Update muvaffaqiyatli qayta ishlandi")
            
        return "OK"
    except Exception as e:
        logger.error(f"Webhook da xatolik: {e}")
        return "Error", 500

# Webhook ni o'rnatish
@flask_app.route('/set_webhook', methods=['GET'])
def set_webhook():
    try:
        if not telegram_app:
            return "Bot not initialized", 500
            
        webhook_url = f"https://iqmatebot.pythonanywhere.com/webhook"
        
        success = run_async(telegram_app.bot.set_webhook(webhook_url))
        
        if success:
            logger.info(f"Webhook muvaffaqiyatli o'rnatildi: {webhook_url}")
            return f"✅ Webhook o'rnatildi: {webhook_url}"
        else:
            logger.error("Webhook o'rnatish muvaffaqiyatsiz tugadi")
            return "❌ Webhook o'rnatish muvaffaqiyatsiz tugadi"
            
    except Exception as e:
        logger.error(f"Webhook o'rnatishda xatolik: {e}")
        return f"❌ Xatolik: {e}"

# Webhook ni o'chirish
@flask_app.route('/delete_webhook', methods=['GET'])
def delete_webhook():
    try:
        if not telegram_app:
            return "Bot not initialized", 500
            
        success = run_async(telegram_app.bot.delete_webhook())
        if success:
            return "✅ Webhook o'chirildi"
        else:
            return "❌ Webhook o'chirish muvaffaqiyatsiz"
    except Exception as e:
        return f"❌ Xatolik: {e}"

# Webhook ma'lumotlarini ko'rish
@flask_app.route('/webhook_info', methods=['GET'])
def webhook_info():
    try:
        if not telegram_app:
            return "Bot not initialized", 500
            
        info = run_async(telegram_app.bot.get_webhook_info())
        return f"Webhook ma'lumotlari: {info.to_dict()}"
    except Exception as e:
        return f"❌ Xatolik: {e}"

# Asosiy sahifa
@flask_app.route('/')
def index():
    return """
    <h1>Telegram Bot</h1>
    <p>Bot ishlamoqda!</p>
    <ul>
        <li><a href="/set_webhook">Webhook ni o'rnatish</a></li>
        <li><a href="/delete_webhook">Webhook ni o'chirish</a></li>
        <li><a href="/webhook_info">Webhook ma'lumotlari</a></li>
    </ul>
    """

# Botni ishga tushirish
try:
    if initialize_bot():
        logger.info("Bot muvaffaqiyatli ishga tushdi")
    else:
        logger.error("Botni ishga tushirib bo'lmadi")
except Exception as e:
    logger.error(f"Botni ishga tushirishda xatolik: {e}")

if __name__ == "__main__":
    flask_app.run(debug=True)
