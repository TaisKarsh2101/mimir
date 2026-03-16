import mysql.connector
from mysql.connector import Error
import datetime
from config import DB_CONFIG  # Импортируем из config.py


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def get_or_create_user(telegram_id, username=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO users (telegram_id, username) VALUES (%s, %s)",
            (telegram_id, username)
        )
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
        user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user


def get_dictionaries(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM dictionaries WHERE user_id = %s ORDER BY created_at",
        (user_id,)
    )
    dicts = cursor.fetchall()

    cursor.close()
    conn.close()
    return dicts


def create_dictionary(user_id, name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO dictionaries (name, user_id) VALUES (%s, %s)",
            (name.lower(), user_id)
        )
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Ошибка создания словаря: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def add_word(dictionary_id, russian, english):
    conn = get_connection()
    cursor = conn.cursor()

    tomorrow = datetime.datetime.now().date() + datetime.timedelta(days=1)

    try:
        cursor.execute("""
            INSERT INTO words 
            (dictionary_id, russian, english, next_review_date) 
            VALUES (%s, %s, %s, %s)
        """, (dictionary_id, russian.lower(), english.lower(), tomorrow))
        conn.commit()
        return True
    except Error as e:
        print(f"Ошибка добавления слова: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def get_words_for_review(user_id, limit=10):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    today = datetime.datetime.now().date()

    cursor.execute("""
        SELECT w.*, d.name as dictionary_name 
        FROM words w
        JOIN dictionaries d ON w.dictionary_id = d.id
        WHERE d.user_id = %s 
          AND w.next_review_date <= %s
        ORDER BY w.next_review_date
        LIMIT %s
    """, (user_id, today, limit))

    words = cursor.fetchall()
    cursor.close()
    conn.close()
    return words


def get_word_by_id(word_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM words WHERE id = %s", (word_id,))
    word = cursor.fetchone()

    cursor.close()
    conn.close()
    return word


def update_word_after_review(word_id, ef, repetition, interval_days, next_review_date, quality):
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.datetime.now()

    try:
        cursor.execute("""
            UPDATE words 
            SET ef = %s,
                repetition = %s,
                interval_days = %s,
                last_reviewed = %s,
                next_review_date = %s,
                total_reviews = total_reviews + 1,
                correct_count = correct_count + %s,
                incorrect_count = incorrect_count + %s
            WHERE id = %s
        """, (
            ef,
            repetition,
            interval_days,
            today,
            next_review_date,
            1 if quality >= 3 else 0,
            1 if quality < 3 else 0,
            word_id
        ))
        conn.commit()
    except Error as e:
        print(f"Ошибка обновления слова: {e}")
    finally:
        cursor.close()
        conn.close()


def delete_word(word_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM words WHERE id = %s", (word_id,))
        conn.commit()
        return True
    except Error as e:
        print(f"Ошибка удаления слова: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def delete_dictionary(dictionary_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM dictionaries WHERE id = %s", (dictionary_id,))
        conn.commit()
        return True
    except Error as e:
        print(f"Ошибка удаления словаря: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def get_dictionary_by_name(user_id, name):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM dictionaries WHERE user_id = %s AND name = %s",
        (user_id, name.lower())
    )
    dictionary = cursor.fetchone()

    cursor.close()
    conn.close()
    return dictionary


def get_words_in_dictionary(dictionary_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM words WHERE dictionary_id = %s ORDER BY created_at",
        (dictionary_id,)
    )
    words = cursor.fetchall()

    cursor.close()
    conn.close()
    return words


def count_due_words(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.datetime.now().date()

    cursor.execute("""
        SELECT COUNT(*) 
        FROM words w
        JOIN dictionaries d ON w.dictionary_id = d.id
        WHERE d.user_id = %s AND w.next_review_date <= %s
    """, (user_id, today))

    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return count