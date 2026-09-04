import sqlite3

DB_NAME = "zbfk.db"


def init_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            specialty TEXT NOT NULL,
            course INTEGER NOT NULL,
            subject TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_user(
    telegram_id: int,
    specialty: str,
    course: int,
    subject: str | None = None
):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users
        (telegram_id, specialty, course, subject)
        VALUES (?, ?, ?, ?)

        ON CONFLICT(telegram_id)
        DO UPDATE SET
            specialty = excluded.specialty,
            course = excluded.course,
            subject = excluded.subject
    """, (
        telegram_id,
        specialty,
        course,
        subject
    ))

    connection.commit()
    connection.close()


def get_user(telegram_id: int):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT specialty, course, subject
        FROM users
        WHERE telegram_id = ?
    """, (telegram_id,))

    result = cursor.fetchone()

    connection.close()

    return result
