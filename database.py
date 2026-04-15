import aiosqlite
import json
import logging
import os

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

async def load_from_json(filepath="backup_data.json"):
    if not os.path.exists(filepath):
        logger.error(f"File {filepath} not found.")
        return 0

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM qa_pairs")
        await db.executemany(
            "INSERT INTO qa_pairs (question, answer, category) VALUES (?, ?, ?)",
            data
        )
        await db.commit()

    logger.info(f"Loaded {len(data)} QA pairs from {filepath}")
    return len(data)

async def get_all_questions():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, question, answer FROM qa_pairs") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_total_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM qa_pairs") as cursor:
            return (await cursor.fetchone())[0]