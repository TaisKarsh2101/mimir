import datetime
import threading
import time
from db import get_connection, count_due_words, get_or_create_user
from config import BOT_TOKEN
import telebot

bot = telebot.TeleBot(BOT_TOKEN)

# Хранилище: кому и когда отправляли уведомления
# last_notification[user_id] = дата последнего уведомления
last_notification = {}


def check_and_notify_users():
    """
    Проверяет всех пользователей и отправляет уведомления,
    если есть слова для повторения и уведомление еще не отправлялось сегодня
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    today = datetime.datetime.now().date()

    # Находим всех пользователей, у которых есть слова для повторения
    cursor.execute("""
        SELECT DISTINCT u.telegram_id, u.id
        FROM users u
        JOIN dictionaries d ON u.id = d.user_id
        JOIN words w ON d.id = w.dictionary_id
        WHERE w.next_review_date <= %s
    """, (today,))

    users_to_notify = cursor.fetchall()
    cursor.close()
    conn.close()

    for user in users_to_notify:
        user_id = user['telegram_id']
        db_user_id = user['id']

        # Проверяем, отправляли ли уже уведомление сегодня
        last_date = last_notification.get(user_id)

        if last_date != today:
            # Считаем точное количество слов для повторения
            due_count = count_due_words(db_user_id)

            if due_count > 0:
                try:
                    bot.send_message(
                        user_id,
                        f"📚 Напоминание: у вас {due_count} слов для повторения сегодня!\n"
                        f"Нажмите «📚 Повторить» в меню, чтобы начать."
                    )
                    # Запоминаем, что сегодня уведомление уже отправили
                    last_notification[user_id] = today
                    print(f"Уведомление отправлено пользователю {user_id}")
                except Exception as e:
                    print(f"Не удалось отправить уведомление {user_id}: {e}")


def scheduler_worker():
    """
    Фоновый поток, который запускает проверку раз в час
    """
    while True:
        # Проверяем текущее время
        now = datetime.datetime.now()

        # Отправляем уведомления (можно добавить проверку на время суток)
        check_and_notify_users()

        # Спим 1 час
        time.sleep(3600)


def start_scheduler():
    """
    Запускает планировщик в отдельном потоке
    """
    thread = threading.Thread(target=scheduler_worker, daemon=True)
    thread.start()
    print("⏰ Планировщик уведомлений запущен (проверка раз в час)")