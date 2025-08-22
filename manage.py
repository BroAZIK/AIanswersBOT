import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import pytz

from details.handlers import button_callbacks, start, ignore_channel_posts, text, photo

TOKEN = "8473456433:AAFu9z8ZNi4fWfoBpo78STSiGbvahRQ8SCw"

app = Application.builder().token(TOKEN).build()



app.add_handler(CallbackQueryHandler(button_callbacks))
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, ignore_channel_posts))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
app.add_handler(MessageHandler(filters.PHOTO, photo))


if __name__ == "__main__":
    print("Polling ishlayapti...")
    app.run_polling(
    allowed_updates=[Update.MESSAGE, Update.CALLBACK_QUERY],
    drop_pending_updates=True,
    )