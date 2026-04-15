import aiosqlite
import json
import logging
import os
import asyncio

logger = logging.getLogger(__name__)
DB_PATH = "qa_database.db"


async def init_db():
   
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS qa_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT DEFAULT 'university'
            )
        """)
        await db.commit()
    logger.info("✅ تم إنشاء/التحقق من جدول qa_pairs بنجاح")


async def load_from_json(filepath="backup_data.json"):
   
    if not os.path.exists(filepath):
        logger.error(f"❌ الملف {filepath} غير موجود!")
        return 0

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        
        if data and isinstance(data[0], list):
            data = [
                (item[0], item[1], item[2] if len(item) > 2 else "university")
                for item in data
            ]

        async with aiosqlite.connect(DB_PATH) as db:
            
            await db.execute("DELETE FROM qa_pairs")
            
        
            await db.executemany(
                "INSERT INTO qa_pairs (question, answer, category) VALUES (?, ?, ?)",
                data
            )
            await db.commit()

        logger.info(f"✅ تم تحميل {len(data)} سؤال وجواب بنجاح من {filepath}")
        return len(data)

    except Exception as e:
        logger.error(f"❌ خطأ أثناء تحميل الملف {filepath}: {e}", exc_info=True)
        return 0


async def get_all_questions():
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, question, answer FROM qa_pairs") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_total_count():
    
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM qa_pairs") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0



async def initialize_database():
    
    try:
        await init_db()
        count = await load_from_json("backup_data.json")
        return count
    except Exception as e:
        logger.error(f"فشل في تهيئة قاعدة البيانات: {e}", exc_info=True)
        return 0
