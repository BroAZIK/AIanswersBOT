import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ContextTypes
from settings import TOKEN
from details.handlers import button_callbacks, start, ignore_channel_posts, text, photo, stats

# Loggerni sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app yaratish
flask_app = Flask(__name__)

# Global bot o'zgaruvchisi
bot = None

# Botni ishga tushirish
def initialize_bot():
    global bot
    try:
        # Botni yaratish
        bot = Bot(token=TOKEN)
        logger.info("Bot muvaffaqiyatli yaratildi")
        return True
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik: {e}")
        return False

# Context yaratish
def create_context():
    class SimpleContext:
        def __init__(self):
            self.bot = bot
    return SimpleContext()

# Async funksiyani ishga tushirish (yaxshilangan versiya)
def run_async(coro):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(coro)
            return result
        except Exception as e:
            logger.error(f"Async funksiyada xatolik: {e}")
            return None
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Event loop yaratishda xatolik: {e}")
        return None

# Webhook endpoint
@flask_app.route('/webhook', methods=['POST'])
def webhook():
    try:
        if not bot:
            logger.error("Bot ishga tushmagan")
            return "Error: Bot not initialized", 500

        if request.method == "POST":
            json_data = request.get_json(force=True)
            logger.info("Qabul qilingan yangi xabar")
            
            update = Update.de_json(json_data, bot)
            context = create_context()
            
            # Update turi bo'yicha handlerlarni chaqirish
            try:
                if update.message:
                    if update.message.text and update.message.text.startswith('/'):
                        if update.message.text == '/start':
                            run_async(start(update, context))
                        elif update.message.text == '/about':
                            run_async(stats(update, context))
                        elif update.message.photo:
                            run_async(photo(update, context))
                        else:
                            run_async(text(update, context))
                    elif update.message.photo:
                        run_async(photo(update, context))
                    elif update.message.text:
                        run_async(text(update, context))
                elif update.callback_query:
                    run_async(button_callbacks(update, context))
                elif update.channel_post:
                    run_async(ignore_channel_posts(update, context))
                    
                logger.info("Update muvaffaqiyatli qayta ishlandi")
            except Exception as e:
                logger.error(f"Update ni qayta ishlashda xatolik: {e}")
            
        return "OK"
    except Exception as e:
        logger.error(f"Webhook da xatolik: {e}")
        return "Error", 500

# Webhook ni o'rnatish
@flask_app.route('/set_webhook', methods=['GET'])
def set_webhook():
    try:
        if not bot:
            return "Bot not initialized", 500
            
        webhook_url = f"https://iqmatebot.pythonanywhere.com/webhook"
        
        success = run_async(bot.set_webhook(
            webhook_url,
            allowed_updates=['message', 'callback_query', 'channel_post'],
            drop_pending_updates=True
        ))
        
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
        if not bot:
            return "Bot not initialized", 500
            
        success = run_async(bot.delete_webhook())
        if success:
            return "✅ Webhook o'chirildi"
        else:
            return "❌ Webhook o'chirish muvaffaqiyatsiz"
    except Exception as e:
        return f"❌ Xatolik: {e}"

# Webhook ma'lumotlarini ko'rish (xatolikni bartaraf qilgan versiya)
@flask_app.route('/webhook_info', methods=['GET'])
def webhook_info():
    try:
        if not bot:
            return "Bot not initialized", 500
            
        info = run_async(bot.get_webhook_info())
        if info is None:
            return "❌ Webhook ma'lumotlarini olish muvaffaqiyatsiz tugadi"
        
        # to_dict() metodini tekshirish
        if hasattr(info, 'to_dict'):
            return f"Webhook ma'lumotlari: {info.to_dict()}"
        else:
            return f"Webhook ma'lumotlari: {str(info)}"
    except Exception as e:
        return f"❌ Xatolik: {e}"

# Bot holatini tekshirish
@flask_app.route('/bot_info', methods=['GET'])
def bot_info():
    try:
        if not bot:
            return "Bot not initialized", 500
            
        # Oddiy bot ma'lumotlarini olish
        me = run_async(bot.get_me())
        if me:
            return f"Bot ma'lumotlari: {me.first_name} (@{me.username})"
        else:
            return "❌ Bot ma'lumotlarini olish muvaffaqiyatsiz"
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
        <li><a href="/bot_info">Bot ma'lumotlari</a></li>
    </ul>
    """

# Botni ishga tushirish
try:
    if initialize_bot():
        logger.info("Bot muvaffaqiyatli ishga tushdi")
        
        # Bot ma'lumotlarini tekshirish
        me = run_async(bot.get_me())
        if me:
            logger.info(f"Bot: {me.first_name} (@{me.username})")
        else:
            logger.warning("Bot ma'lumotlarini olish muvaffaqiyatsiz")
            
    else:
        logger.error("Botni ishga tushirib bo'lmadi")
except Exception as e:
    logger.error(f"Botni ishga tushirishda xatolik: {e}")

if __name__ == "__main__":
    flask_app.run(debug=True)
