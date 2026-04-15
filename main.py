import logging
import sys
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import TELEGRAM_TOKEN
import database
from handlers import (
    start_handler,
    stats_handler,
    reload_handler,
    message_handler,
    error_handler
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


async def post_init(app: Application):
    
    try:
        logger.info("جاري تهيئة قاعدة البيانات...")
        await database.init_db()
        count = await database.load_from_json("backup_data.json")
        logger.info(f"✅ تم تحميل {count} سؤال بنجاح.")
    except Exception as e:
        logger.error(f"❌ خطأ في تهيئة قاعدة البيانات: {e}", exc_info=True)


async def main():
    
    logger.info("جاري تشغيل البوت...")

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

    logger.info("✅ البوت يعمل الآن...")

    
    await app.initialize()
    await app.start()
    await app.run_polling(
        allowed_updates=["message"],
        drop_pending_updates=True,
        close_loop=False
    )


if __name__ == "__main__":
    asyncio.run(main())
