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

async def main_async():
    """تهيئة قاعدة البيانات أولاً، ثم تشغيل البوت"""

    # ✅ 1. تهيئة قاعدة البيانات وتحميل الأسئلة قبل أي شيء
    await database.init_db()
    count = await database.load_from_json("backup_data.json")
    logger.info(f"✅ Database ready with {count} questions.")

    # ✅ 2. بناء التطبيق وتشغيله
    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("stats", stats_handler))
    app.add_handler(CommandHandler("reload", reload_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_error_handler(error_handler)

    logger.info("🤖 Bot is polling...")
    await app.initialize()
    await app.updater.start_polling(allowed_updates=["message"], drop_pending_updates=True)
    await app.start()

    # إبقاء البوت يعمل
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
