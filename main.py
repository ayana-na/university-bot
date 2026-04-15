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

# إعداد Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


async def post_init(app: Application):
    """يتم تنفيذه بعد تشغيل البوت - يقوم بتهيئة قاعدة البيانات"""
    try:
        logger.info("جاري تهيئة قاعدة البيانات...")
        
        # إنشاء الجدول إذا لم يكن موجوداً
        await database.init_db()
        
        # تحميل البيانات من الملف
        count = await database.load_from_json("backup_data.json")
        
        logger.info(f"✅ تم تهيئة البوت بنجاح. عدد الأسئلة المحملة: {count}")
        
    except Exception as e:
        logger.error(f"❌ خطأ أثناء تهيئة قاعدة البيانات: {e}", exc_info=True)
        
        # محاولة ثانية بعد تأخير قصير (fallback)
        try:
            logger.info("محاولة ثانية لتهيئة قاعدة البيانات...")
            await asyncio.sleep(3)
            await database.init_db()
            count = await database.load_from_json("backup_data.json")
            logger.info(f"✅ تم التهيئة بنجاح في المحاولة الثانية. عدد الأسئلة: {count}")
        except Exception as e2:
            logger.critical(f"❌ فشلت كل محاولات تهيئة قاعدة البيانات: {e2}", exc_info=True)


def main():
    """الدالة الرئيسية لبدء البوت"""
    logger.info("جاري تشغيل البوت...")

    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)      # تنفيذ تهيئة قاعدة البيانات
        .build()
    )

    # إضافة الـ Handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("stats", stats_handler))
    app.add_handler(CommandHandler("reload", reload_handler))
    
    # معالجة كل الرسائل النصية غير الأوامر
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # معالج الأخطاء
    app.add_error_handler(error_handler)

    logger.info("✅ البوت يعمل الآن باستخدام Polling...")
    
    # تشغيل البوت
    app.run_polling(
        allowed_updates=["message"],
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
