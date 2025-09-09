from telegram import Update, Bot, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes
)
from .api_requests import *
from details.database.db import *
from details.messages import *
from details.buttons import *
from pprint import pprint
from settings import *

bot = Bot(token=TOKEN)


async def log_saver(user_id, full_name,  text, answer, rassm=None):
    if rassm != None:
        try:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=rassm, caption=f"<a href='tg://user?id={user_id}'>{full_name}</a>:\n{text}\n\n{answer}", parse_mode=ParseMode.HTML)
            insert(table="question", data={"user_id": user_id,"savol": text, "full_name": full_name, "photo": rassm})
        except:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=rassm, caption=f"<a href='tg://user?id={user_id}'>{full_name}</a>:\n{text}\n\nJavob berildi !", parse_mode=ParseMode.HTML)
            insert(table="question", data={"user_id": user_id,"savol": text, "full_name": full_name, "photo": rassm})
    else:
        try:
            await bot.send_message(chat_id=CHANNEL_ID, text=f"\n<a href='tg://user?id={user_id}'>{full_name}</a>:\n{text}\n\n{answer}", parse_mode=ParseMode.HTML)
        except:
            await bot.send_message(chat_id=CHANNEL_ID, text=f"\n<a href='tg://user?id={user_id}'>{full_name}</a>:\n{text}\n\nJavob berildi  !", parse_mode=ParseMode.HTML)
        insert(table="question", data={"user_id": user_id,"savol": text, "full_name": full_name, "photo": rassm})

    print("loglar muammosiz jo'natildi")

async def start(update: Update, context):
    user_id = update.message.chat_id
    full_name = update.effective_chat.full_name
    
    insert(table="users", user_id=user_id, data={
            "name": full_name,
            "mode": "medium"
        })

    await update.message.reply_text(
        text=start_message
    )

    

    mode = get(table="users", user_id=user_id)['mode']
    
    if mode == "short":
        await update.message.reply_text(
        text=choice_mode_text,
        reply_markup=InlineKeyboardMarkup(short_but)
        )
    if mode == "complete":
        await update.message.reply_text(
        text=choice_mode_text,
        reply_markup=InlineKeyboardMarkup(complete_but)
        )    
    
    if mode == "medium":
        await update.message.reply_text(
        text=choice_mode_text,
        reply_markup=InlineKeyboardMarkup(medium_but)
        )

async def text(update: Update, context):

    user_id = update.message.chat_id
    await update.message.set_reaction("👍")
    xabar = update.message.text
    mode = get(table="users", user_id=user_id)['mode']

    print("text ishlavotti")

    ai_text = ai_request(text=f"user.{user_id} | {xabar} | mode.{mode}")
    await log_saver(user_id=user_id, full_name=update.effective_chat.full_name, text=xabar, answer=ai_text, rassm=None)


    if mode == "short":
        await update.message.reply_text(
            text=ai_text,
            reply_markup=InlineKeyboardMarkup(short_but)
        )
    if mode == "medium":
        await update.message.reply_text(
            text=ai_text,
            reply_markup=InlineKeyboardMarkup(medium_but)
        )
    if mode == "complete":
        await update.message.reply_text(
            text=ai_text,
            reply_markup=InlineKeyboardMarkup(complete_but)
        )

async def stats(update: Update, context):
    services = get(table="answers")
    users_len = len(get(table="users"))

    await update.message.reply_text(
        text=stats_mes.format(users_len, services),
        parse_mode=ParseMode.HTML
    )

async def button_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query
    user_id = query.from_user.id
    # pprint(query.to_dict())
    mode = get(table="users", user_id=user_id)['mode']
    
    if query.data != mode:
        if query.data == "short":
            upd(table="users", user_id=user_id, data={"mode": "short"})
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(short_but))

        elif query.data == "medium":
            upd(table="users", user_id=user_id, data={"mode": "medium"})
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(medium_but))

        elif query.data == "complete":
            upd(table="users", user_id=user_id, data={"mode": "complete"})
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(complete_but))

        await query.answer("✅ Rejim o'zgardi", show_alert=True)
    else:
        await query.answer("Boshqa rejimni tanlang❗️", show_alert=False)

async def photo(update: Update, context):

    rasm = update.message.photo[-1].file_id
    tg_file = await context.bot.get_file(rasm)
    file_path = tg_file.file_path
    user_id = update.effective_chat.id
    mode = get(table="users", user_id=user_id)['mode']

    print("rasm qabul qilindi")
    ocr_text = OCRres(file_path)
    print("OCR dan xabar keldi")

    

    ai_text = ai_request(text=f"user.{user_id} | {ocr_text} | mode.{mode}")
    await log_saver(user_id=user_id, full_name=update.effective_chat.full_name, text=ocr_text, answer=ai_text,rassm=rasm)
    print("ai dan xabar keldi")


    if mode == "short":
        await update.message.reply_text(
            text=ai_text,
            reply_markup=InlineKeyboardMarkup(short_but)
        )
    if mode == "medium":
        await update.message.reply_text(
            text=ai_text,
            reply_markup=InlineKeyboardMarkup(medium_but)
        )
    if mode == "complete":
        await update.message.reply_text(
            text=ai_text,
            reply_markup=InlineKeyboardMarkup(complete_but)
        )

def ignore_channel_posts(update, context):
    print("ignor qilindi")
    return



        
