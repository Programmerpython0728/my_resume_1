import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start_func(update, context):
    update.message.reply_text(text="""Assalomu alaykum, bu bot orqali siz mening resume bilan tanishib chiqishingiz mumkin!
Здравствуйте! С помощью этого бота вы можете ознакомиться с моим резюме.
Hello! You can view my resume through this bot.

👉 /resume ni bosing.""")

def resume_inline(update, context):
    buttons = [
        [InlineKeyboardButton(text="Resume (O‘zbek)", callback_data="resume_uzb")],
        [InlineKeyboardButton(text="Resume (English)", callback_data="resume_eng")]
    ]
    update.message.reply_text(
        text="Quyidagi tugmalardan birini tanlang:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def reply_to_requests(update, context):
    query = update.callback_query
    query.answer()

    if query.data == "resume_uzb":
        with open("resumes/Khayrullayev_resume_uzb.pdf", "rb") as file:
            context.bot.send_document(chat_id=query.message.chat.id, document=file)
        query.edit_message_text(
            text="Sizga Xayrullayev Ma'murjoning resumesi yuborildi. E'tibor bilan tanishib chiqing!"
        )
    elif query.data == "resume_eng":
        with open("resumes/khayrullayev_resume_english.pdf", "rb") as file:
            context.bot.send_document(chat_id=query.message.chat.id, document=file)
        query.edit_message_text(
            text="The resume of Ma'murjon Khayrullayev has been sent to you. Please review it carefully!"
        )


def main():
    updater = Updater(token="7657405647:AAE13hEaK4qzt_swEu4Uozkf2NtwasV4WJo", use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_func))
    dispatcher.add_handler(CommandHandler("resume", resume_inline))
    dispatcher.add_handler(CallbackQueryHandler(reply_to_requests))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, resume_inline))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
