from telegram import Update, Bot, InlineKeyboardMarkup
from telegram.constants import ParseMode, ChatAction
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
from .image_request import vision_responser

bot = Bot(token=TOKEN)


async def log_saver(user_id, full_name,  text, answer, caption=None, rassm=None):
    if rassm != None:
        try:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=rassm, caption=f"<a href='tg://user?id={user_id}'>{full_name}</a>:\n-{text}\n-{caption}\n\n@IQmate_bot\n-{answer}", parse_mode=ParseMode.HTML)
            insert(table="question", data={"user_id": user_id,"savol": text, "full_name": full_name, "photo": rassm})
        except:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=rassm, caption=f"<a href='tg://user?id={user_id}'>{full_name}</a>:\n-{text}\n-{caption}\n\n@IQmate_bot\n-Javob berildi !", parse_mode=ParseMode.HTML)
            insert(table="question", data={"user_id": user_id,"savol": text, "full_name": full_name, "photo": rassm})
    else:
        try:
            await bot.send_message(chat_id=CHANNEL_ID, text=f"\n<a href='tg://user?id={user_id}'>{full_name}</a>:\n-{text}\n\n@IQmate_bot\n-{answer}", parse_mode=ParseMode.HTML)
        except:
            await bot.send_message(chat_id=CHANNEL_ID, text=f"\n<a href='tg://user?id={user_id}'>{full_name}</a>:\n{text}\n\n@IQmate_bot\n-Javob berildi  !", parse_mode=ParseMode.HTML)
        insert(table="question", data={"user_id": user_id,"savol": text, "full_name": full_name, "photo": rassm})

    print("loglar muammosiz jo'natildi")

async def start(update: Update, context):
    user_id = update.message.chat_id
    full_name = update.effective_chat.full_name
    
    member = await context.bot.get_chat_member(chat_id=NEWS_CHANNEL_ID, user_id=user_id)
    if member.status not in ['member', 'administrator', 'creator']:
        await update.message.reply_text(text="Botning yangiliklar kanaliga a'zo bo'ling❗️",
                                        reply_markup=InlineKeyboardMarkup(channel_but))
    else:
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

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

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
    member = await context.bot.get_chat_member(chat_id=NEWS_CHANNEL_ID, user_id=user_id)
    if query.data == "check":
        if member.status not in ['member', 'administrator', 'creator']:
            await query.answer(text="Siz xali kanalga a'zo emassiz❌")
        else:
            insert(table="users", user_id=user_id, data={
                "name": query.from_user.full_name,
                "mode": "medium"
            })

            await context.bot.delete_message(chat_id=user_id, message_id=query.message.message_id)
            
            await query.message.reply_text(
            text=start_message
            )

    

            mode = get(table="users", user_id=user_id)['mode']
    
            if mode == "short":
                await query.message.reply_text(
                text=choice_mode_text,
                reply_markup=InlineKeyboardMarkup(short_but)
                )
            if mode == "complete":
                await query.message.reply_text(
                text=choice_mode_text,
                reply_markup=InlineKeyboardMarkup(complete_but)
                )    
    
            if mode == "medium":
                await query.message.reply_text(
                text=choice_mode_text,
                reply_markup=InlineKeyboardMarkup(medium_but)
                )

    elif query.data != mode:
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
    await update.message.set_reaction("👍")
    rasm = update.message.photo[-1].file_id
    tg_file = await context.bot.get_file(rasm)
    caption = update.message.caption
    file_path = os.path.join("details", "test.jpg")
    user_id = update.effective_chat.id
    mode = get(table="users", user_id=user_id)['mode']

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    await tg_file.download_to_drive(file_path)
    print("Rasm yuklandi")
    # ocr_text = OCRres(file_path)

    
    if caption:
        await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
        )
        
        ai_text = vision_responser(text=f"user.{user_id} | {caption} | mode.{mode}")

        # ai_text = ai_request(text=f"user.{user_id} | {ocr_text} | {caption} | mode.{mode}")
        await log_saver(user_id=user_id, full_name=update.effective_chat.full_name, text=caption ,caption=caption, answer=ai_text, rassm=rasm)
    
    else:
        await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
        )

        ai_text = vision_responser(text=f"user.{user_id} | kaptcha malumoti yo'q | mode.{mode}")
        # ai_text = ai_request(text=f"user.{user_id} | {ocr_text} | mode.{mode}")
        await log_saver(user_id=user_id, full_name=update.effective_chat.full_name, text=" ", answer=ai_text,rassm=rasm)
    


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



        
