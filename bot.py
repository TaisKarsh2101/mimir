import telebot
from telebot import types
import datetime
import random
import re

from config import BOT_TOKEN
from db import *
from sm2 import process_sm2_review, get_quality_keyboard
from scheduler import start_scheduler

bot = telebot.TeleBot(BOT_TOKEN)

# Хранилище состояний пользователей
# user_data[user_id] = {
#     'state': 'adding_word' | 'choosing_dict' | 'creating_dict' | 'reviewing',
#     'temp_data': {...},
#     'review_words': [],  # список слов на сегодня
#     'current_word_index': 0,
#     'current_word': None
# }
user_data = {}


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def clean_text(text):
    """Удаляет лишние пробелы и приводит к нижнему регистру"""
    return ' '.join(text.lower().split())


def show_main_menu(chat_id, text="Выберите действие:"):
    """Показывает главное меню"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📚 Повторить")
    btn2 = types.KeyboardButton("➕ Добавить слово")
    btn3 = types.KeyboardButton("📖 Мои словари")
    btn4 = types.KeyboardButton("🗑 Удалить")
    btn5 = types.KeyboardButton("📊 Статистика")
    markup.add(btn1, btn2, btn3, btn4, btn5)

    bot.send_message(chat_id, text, reply_markup=markup)


def safe_send(chat_id, text, **kwargs):
    """Безопасная отправка сообщения с обработкой ошибок"""
    try:
        bot.send_message(chat_id, text, **kwargs)
    except Exception as e:
        print(f"Ошибка отправки сообщения {chat_id}: {e}")


# ========== КОМАНДА START ==========

@bot.message_handler(commands=['start'])
def start_command(message):
    user = get_or_create_user(message.chat.id, message.from_user.username)
    show_main_menu(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! Я помогу тебе запоминать английские слова."
    )


# ========== ДОБАВЛЕНИЕ СЛОВА ==========

@bot.message_handler(func=lambda m: m.text == "➕ Добавить слово")
def add_word_start(message):
    """Начало процесса добавления слова"""
    user_id = message.chat.id
    user = get_or_create_user(user_id)

    # Получаем словари пользователя
    dicts = get_dictionaries(user['id'])

    if not dicts:
        # Если словарей нет, сразу переходим к созданию
        user_data[user_id] = {'state': 'creating_dict'}
        bot.send_message(
            user_id,
            "У вас еще нет словарей. Введите название для нового словаря:"
        )
        return

    # Показываем список словарей для выбора
    markup = types.InlineKeyboardMarkup(row_width=1)
    for d in dicts:
        btn = types.InlineKeyboardButton(
            d['name'],
            callback_data=f"select_dict_{d['id']}"
        )
        markup.add(btn)

    btn_new = types.InlineKeyboardButton("➕ Создать новый словарь", callback_data="create_new_dict")
    markup.add(btn_new)

    user_data[user_id] = {'state': 'choosing_dict'}
    bot.send_message(
        user_id,
        "Выберите словарь для добавления слова:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_dict_'))
def select_dict_callback(call):
    """Выбор существующего словаря"""
    user_id = call.message.chat.id

    if call.data == "create_new_dict":
        user_data[user_id] = {'state': 'creating_dict'}
        bot.edit_message_text(
            "Введите название для нового словаря:",
            user_id,
            call.message.message_id
        )
        return

    dict_id = int(call.data.split('_')[2])
    user_data[user_id] = {
        'state': 'adding_word',
        'dict_id': dict_id
    }

    bot.edit_message_text(
        "Отправьте слово в формате: слово - перевод\n"
        "Например: dog - собака",
        user_id,
        call.message.message_id
    )
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('state') == 'creating_dict')
def create_dict_handler(message):
    """Создание нового словаря"""
    user_id = message.chat.id
    user = get_or_create_user(user_id)
    dict_name = clean_text(message.text)

    if len(dict_name) < 1 or len(dict_name) > 50:
        bot.send_message(user_id, "Название должно быть от 1 до 50 символов. Попробуйте снова:")
        return

    dict_id = create_dictionary(user['id'], dict_name)

    if dict_id:
        user_data[user_id] = {
            'state': 'adding_word',
            'dict_id': dict_id
        }
        bot.send_message(
            user_id,
            f"Словарь «{dict_name}» создан!\n"
            "Теперь отправьте слово в формате: слово - перевод"
        )
    else:
        bot.send_message(
            user_id,
            "Ошибка при создании словаря. Возможно, такое название уже есть."
        )


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('state') == 'adding_word')
def add_word_handler(message):
    """Обработка ввода слова"""
    user_id = message.chat.id
    text = message.text.strip()

    # Проверяем формат "слово - перевод"
    if ' - ' not in text and ' -' not in text and '- ' not in text:
        bot.send_message(
            user_id,
            "Неверный формат. Используйте: слово - перевод\n"
            "Например: dog - собака"
        )
        return

    # Разделяем слово и перевод
    parts = re.split(r'\s*[-–—]\s*', text, maxsplit=1)
    if len(parts) != 2:
        bot.send_message(
            user_id,
            "Неверный формат. Используйте дефис между словом и переводом."
        )
        return

    english = clean_text(parts[0])
    russian = clean_text(parts[1])

    if not english or not russian:
        bot.send_message(
            user_id,
            "Слово и перевод не могут быть пустыми."
        )
        return

    dict_id = user_data[user_id]['dict_id']

    # Пробуем добавить слово
    success = add_word(dict_id, russian, english)

    if success:
        bot.send_message(
            user_id,
            f"✅ Добавлено: {english} - {russian}\n\n"
            "Можете добавить еще одно слово или вернуться в меню.",
            reply_markup=types.ReplyKeyboardMarkup(
                resize_keyboard=True
            ).add(types.KeyboardButton("➕ Добавить ещё"))
        )
        # Состояние остается 'adding_word' для добавления следующих слов
    else:
        bot.send_message(
            user_id,
            "❌ Это слово уже есть в словаре."
        )


@bot.message_handler(func=lambda m: m.text == "➕ Добавить ещё")
def add_more_handler(message):
    """Добавление еще одного слова"""
    user_id = message.chat.id
    if user_id in user_data and 'dict_id' in user_data[user_id]:
        bot.send_message(
            user_id,
            "Отправьте слово в формате: слово - перевод"
        )
    else:
        # Если почему-то потеряли состояние, начинаем заново
        add_word_start(message)


# ========== ПОВТОРЕНИЕ СЛОВ ==========

@bot.message_handler(func=lambda m: m.text == "📚 Повторить")
def start_review(message):
    """Начало повторения"""
    user_id = message.chat.id
    user = get_or_create_user(user_id)

    # Получаем слова для повторения
    words = get_words_for_review(user['id'], limit=10)

    if not words:
        bot.send_message(
            user_id,
            "🎉 Сегодня нет слов для повторения! Отдыхайте или добавляйте новые слова."
        )
        return

    # Перемешиваем слова (по желанию)
    random.shuffle(words)

    # Сохраняем сессию повторения
    user_data[user_id] = {
        'state': 'reviewing',
        'review_words': words,
        'current_word_index': 0,
        'current_word': words[0]
    }

    # Показываем первое слово
    show_next_word(user_id)


def show_next_word(user_id):
    """Показывает следующее слово в сессии повторения"""
    data = user_data.get(user_id)
    if not data or data['state'] != 'reviewing':
        return

    index = data['current_word_index']
    words = data['review_words']

    if index >= len(words):
        # Все слова показаны, завершаем сессию
        due_count = count_due_words(get_or_create_user(user_id)['id'])

        if due_count > 0:
            bot.send_message(
                user_id,
                f"✨ Вы повторили все слова! Но осталось ещё {due_count} слов на сегодня.\n"
                f"Нажмите «📚 Повторить», чтобы продолжить."
            )
        else:
            bot.send_message(
                user_id,
                "🎉 Поздравляю! Вы повторили все слова на сегодня!"
            )

        # Очищаем состояние
        if user_id in user_data:
            del user_data[user_id]

        show_main_menu(user_id)
        return

    current_word = words[index]
    data['current_word'] = current_word

    # Показываем русское слово
    bot.send_message(
        user_id,
        f"Слово {index + 1} из {len(words)}:\n\n"
        f"🇷🇺 {current_word['russian']}\n\n"
        f"Введите перевод на английский:"
    )


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('state') == 'reviewing')
def handle_review_answer(message):
    """Обработка ответа пользователя при повторении"""
    user_id = message.chat.id
    data = user_data.get(user_id)

    if not data or data['state'] != 'reviewing':
        return

    user_answer = clean_text(message.text)
    current_word = data['current_word']
    correct_answer = current_word['english'].lower()

    is_correct = (user_answer == correct_answer)

    # Сохраняем результат временно
    data['last_answer_correct'] = is_correct
    data['last_word_id'] = current_word['id']

    # Отправляем результат и клавиатуру с оценкой
    if is_correct:
        bot.send_message(
            user_id,
            f"✅ Правильно! Слово: {correct_answer}"
        )
    else:
        bot.send_message(
            user_id,
            f"❌ Неправильно. Правильный ответ: {correct_answer}"
        )

    # Показываем клавиатуру для оценки сложности
    keyboard = get_quality_keyboard(is_correct)
    bot.send_message(
        user_id,
        "Оцените, насколько легко было вспомнить:",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('quality_'))
def handle_quality_callback(call):
    """Обработка оценки качества ответа"""
    user_id = call.message.chat.id
    data = user_data.get(user_id)

    if not data or data['state'] != 'reviewing':
        bot.answer_callback_query(call.id, "Сессия повторения завершена")
        return

    quality = int(call.data.split('_')[1])
    word_id = data['last_word_id']

    # Получаем слово из БД
    word = get_word_by_id(word_id)

    if not word:
        bot.answer_callback_query(call.id, "Ошибка: слово не найдено")
        return

    # Применяем SM-2
    updates = process_sm2_review(word, quality)

    # Обновляем в БД
    update_word_after_review(
        word_id,
        updates['ef'],
        updates['repetition'],
        updates['interval_days'],
        updates['next_review_date'],
        quality
    )

    # Если качество < 4, слово нужно повторить сегодня (добавляем в конец очереди)
    if quality < 4:
        # Добавляем слово в конец списка для повтора сегодня
        # Но чтобы не зациклиться, проверяем, не повторяли ли мы его уже много раз
        max_repeats_per_session = 3
        repeat_count = data.get('repeat_count', {}).get(word_id, 0)

        if repeat_count < max_repeats_per_session:
            # Добавляем слово в конец списка
            data['review_words'].append(word)
            if 'repeat_count' not in data:
                data['repeat_count'] = {}
            data['repeat_count'][word_id] = repeat_count + 1

            bot.send_message(
                user_id,
                "🔄 Это слово будет показано ещё раз в конце сессии для лучшего запоминания."
            )

    # Переходим к следующему слову
    data['current_word_index'] += 1

    # Убираем клавиатуру с оценками
    bot.edit_message_reply_markup(
        user_id,
        call.message.message_id,
        reply_markup=None
    )

    # Показываем следующее слово
    show_next_word(user_id)
    bot.answer_callback_query(call.id)


# ========== МОИ СЛОВАРИ ==========

@bot.message_handler(func=lambda m: m.text == "📖 Мои словари")
def show_dictionaries(message):
    """Показывает список словарей пользователя"""
    user_id = message.chat.id
    user = get_or_create_user(user_id)
    dicts = get_dictionaries(user['id'])

    if not dicts:
        bot.send_message(
            user_id,
            "У вас пока нет словарей. Нажмите «➕ Добавить слово», чтобы создать первый."
        )
        return

    response = "📚 **Ваши словари:**\n\n"

    for d in dicts:
        # Получаем количество слов в словаре
        words = get_words_in_dictionary(d['id'])
        count = len(words)
        due = sum(1 for w in words if w['next_review_date'] <= datetime.datetime.now().date())

        response += f"📖 **{d['name']}**\n"
        response += f"   • Всего слов: {count}\n"
        response += f"   • На повторение сегодня: {due}\n\n"

    bot.send_message(user_id, response, parse_mode="Markdown")


# ========== УДАЛЕНИЕ ==========

@bot.message_handler(func=lambda m: m.text == "🗑 Удалить")
def delete_menu(message):
    """Меню выбора что удалять"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("Удалить слово", callback_data="delete_word")
    btn2 = types.InlineKeyboardButton("Удалить словарь", callback_data="delete_dict")
    markup.add(btn1, btn2)

    bot.send_message(
        message.chat.id,
        "Что хотите удалить?",
        reply_markup=markup
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('delete_') and not call.data.startswith('delete_word_select'))
def handle_delete_callback(call):
    """Обработка удаления (базовая)"""
    user_id = call.message.chat.id
    user = get_or_create_user(user_id)

    if call.data == "delete_word":
        # Показать словари для выбора слова
        dicts = get_dictionaries(user['id'])

        if not dicts:
            bot.edit_message_text(
                "У вас нет словарей.",
                user_id,
                call.message.message_id
            )
            bot.answer_callback_query(call.id)
            return

        markup = types.InlineKeyboardMarkup()
        for d in dicts:
            btn = types.InlineKeyboardButton(
                d['name'],
                callback_data=f"delete_word_select_dict_{d['id']}"
            )
            markup.add(btn)

        bot.edit_message_text(
            "Выберите словарь:",
            user_id,
            call.message.message_id,
            reply_markup=markup
        )

    elif call.data == "delete_dict":
        # Показать словари для удаления
        dicts = get_dictionaries(user['id'])

        if not dicts:
            bot.edit_message_text(
                "У вас нет словарей.",
                user_id,
                call.message.message_id
            )
            bot.answer_callback_query(call.id)
            return

        markup = types.InlineKeyboardMarkup()
        for d in dicts:
            words = get_words_in_dictionary(d['id'])
            btn = types.InlineKeyboardButton(
                f"{d['name']} ({len(words)} слов)",
                callback_data=f"confirm_delete_dict_{d['id']}"
            )
            markup.add(btn)

        bot.edit_message_text(
            "Выберите словарь для удаления:",
            user_id,
            call.message.message_id,
            reply_markup=markup
        )

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_word_select_dict_'))
def delete_word_select_dict(call):
    """Выбор слова для удаления"""
    user_id = call.message.chat.id
    dict_id = int(call.data.split('_')[-1])

    words = get_words_in_dictionary(dict_id)

    if not words:
        bot.edit_message_text(
            "В этом словаре нет слов.",
            user_id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id)
        return

    markup = types.InlineKeyboardMarkup()
    for w in words[:10]:  # Показываем не больше 10 слов
        btn = types.InlineKeyboardButton(
            f"{w['english']} - {w['russian']}",
            callback_data=f"confirm_delete_word_{w['id']}"
        )
        markup.add(btn)

    if len(words) > 10:
        bot.edit_message_text(
            "Первые 10 слов (для удаления всех обратитесь к словарю целиком):",
            user_id,
            call.message.message_id,
            reply_markup=markup
        )
    else:
        bot.edit_message_text(
            "Выберите слово для удаления:",
            user_id,
            call.message.message_id,
            reply_markup=markup
        )

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_word_'))
def confirm_delete_word(call):
    """Подтверждение удаления слова"""
    user_id = call.message.chat.id
    word_id = int(call.data.split('_')[-1])

    delete_word(word_id)

    bot.edit_message_text(
        "✅ Слово удалено.",
        user_id,
        call.message.message_id
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_dict_'))
def confirm_delete_dict(call):
    """Подтверждение удаления словаря"""
    user_id = call.message.chat.id
    dict_id = int(call.data.split('_')[-1])

    delete_dictionary(dict_id)

    bot.edit_message_text(
        "✅ Словарь удален.",
        user_id,
        call.message.message_id
    )
    bot.answer_callback_query(call.id)


# ========== СТАТИСТИКА ==========

@bot.message_handler(func=lambda m: m.text == "📊 Статистика")
def show_stats(message):
    """Показывает статистику пользователя"""
    user_id = message.chat.id
    user = get_or_create_user(user_id)

    # Получаем все словари
    dicts = get_dictionaries(user['id'])

    total_words = 0
    total_due = 0
    level_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    for d in dicts:
        words = get_words_in_dictionary(d['id'])
        total_words += len(words)

        for w in words:
            level_distribution[w['repetition']] = level_distribution.get(w['repetition'], 0) + 1
            if w['next_review_date'] <= datetime.datetime.now().date():
                total_due += 1

    if total_words == 0:
        bot.send_message(
            user_id,
            "📊 У вас пока нет слов. Добавьте первый словарь!"
        )
        return

    response = "📊 **Ваша статистика:**\n\n"
    response += f"📚 Всего словарей: {len(dicts)}\n"
    response += f"📝 Всего слов: {total_words}\n"
    response += f"⏳ Сегодня на повторение: {total_due}\n\n"

    response += "**Распределение по уровням:**\n"
    response += f"🔵 Уровень 1 (новые): {level_distribution[1]}\n"
    response += f"🟢 Уровень 2: {level_distribution[2]}\n"
    response += f"🟡 Уровень 3: {level_distribution[3]}\n"
    response += f"🟠 Уровень 4: {level_distribution[4]}\n"
    response += f"🔴 Уровень 5 (выученные): {level_distribution[5]}\n"

    bot.send_message(user_id, response, parse_mode="Markdown")


# ========== ОБРАБОТКА НЕИЗВЕСТНЫХ КОМАНД ==========

@bot.message_handler(func=lambda m: True)
def unknown_command(message):
    """Обработка любых других сообщений"""
    user_id = message.chat.id

    # Если пользователь в состоянии добавления слова, но сообщение не обработалось
    if user_id in user_data:
        state = user_data[user_id].get('state')
        if state == 'adding_word':
            bot.send_message(
                user_id,
                "Используйте формат: слово - перевод\n"
                "Или нажмите «➕ Добавить ещё» для продолжения."
            )
        elif state == 'creating_dict':
            bot.send_message(
                user_id,
                "Введите название словаря (текст до 50 символов):"
            )
        else:
            bot.send_message(
                user_id,
                "Я не понимаю эту команду. Используйте меню."
            )
    else:
        bot.send_message(
            user_id,
            "Я не понимаю эту команду. Используйте меню."
        )


# ========== ЗАПУСК ==========

if __name__ == "__main__":
    print("🤖 Бот 'Мимир' запущен...")

    # Запускаем планировщик уведомлений
    start_scheduler()

    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")