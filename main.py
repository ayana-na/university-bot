import logging
import sys
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import TELEGRAM_TOKEN
import database
from handlers import start_handler, stats_handler, reload_handler, message_handler, error_handler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def post_init(app: Application):
    await database.init_db()
    count = await database.load_from_json("backup_data.json")
    logger.info(f"✅ Bot ready with {count} questions.")

async def main_async():
    """نقوم بتشغيل البوت داخل دالة غير متزامنة لتجنب مشاكل Event Loop"""
    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("stats", stats_handler))
    app.add_handler(CommandHandler("reload", reload_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_error_handler(error_handler)

    logger.info("🤖 Starting bot...")
    await app.initialize()
    await app.updater.start_polling(allowed_updates=["message"], drop_pending_updates=True)
    await app.start()
    
    # إبقاء البوت قيد التشغيل
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

def main():
    """نقطة الدخول الرئيسية"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
