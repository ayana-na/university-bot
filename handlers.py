import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction

import database
import search_engine

logger = logging.getLogger(__name__)

NO_ANSWER_MSG = "عذراً، هذا السؤال خارج نطاق الشؤون الجامعية. يمكنك مراجعة الإدارة."

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f" أهلاً {user.first_name}!\n"
        " أنا مساعد الشؤون الجامعية. اسألني أي سؤال عن الأنظمة، وسأجيبك مباشرة من قاعدة البيانات الرسمية.\n\n"
        " الأوامر:\n"
        "/stats – عدد الأسئلة المتاحة\n"
        "/reload – إعادة تحميل قاعدة البيانات (للمشرف)"
    )

async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = await database.get_total_count()
    await update.message.reply_text(f" عدد الأسئلة المحفوظة حالياً: <b>{count}</b>", parse_mode=ParseMode.HTML)

async def reload_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(ChatAction.TYPING)
    count = await database.load_from_json("backup_data.json")
    await update.message.reply_text(f" تم تحديث القاعدة بنجاح. عدد الأسئلة الآن: {count}")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.strip()
    if not user_msg:
        return

    await update.message.chat.send_action(ChatAction.TYPING)

    answer, score = await search_engine.find_best_answer(user_msg)
    if answer:
        await update.message.reply_text(answer, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(NO_ANSWER_MSG)

    if not answer:
        logger.info(f"Unanswered question from user {update.effective_user.id}: {user_msg}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling update:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text(" حدث خطأ غير متوقع. الرجاء المحاولة لاحقاً.")