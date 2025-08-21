import requests
import os
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler
)
from details.handlers import button_callbacks, start, ignore_channel_posts, text, photo
# from dotenv import load_dotenv, dotenv_values


TOKEN = "8473456433:AAFu9z8ZNi4fWfoBpo78STSiGbvahRQ8SCw"

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher



def register_handlers():
    
    dispatcher.add_handler(CallbackQueryHandler(button_callbacks))
    dispatcher.add_handler(CommandHandler("start", start)),
    dispatcher.add_handler(MessageHandler(Filters.update.channel_posts, ignore_channel_posts)),
    dispatcher.add_handler(MessageHandler(Filters.text, text)),
    dispatcher.add_handler(MessageHandler(Filters.photo, photo)),

    updater.start_polling() 
    print("polling ishlayapti")
    updater.idle()
register_handlers()