import datetime


def calculate_new_ef(old_ef, quality):
    """
    Рассчитывает новый E-Factor по формуле SM-2
    quality: 0-5 (оценка пользователя)
    """
    new_ef = old_ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    return max(1.3, new_ef)


def calculate_next_interval(repetition, interval_days, ef, quality):
    """
    Рассчитывает следующий интервал по SM-2
    """
    if quality < 3:
        return 1, 0

    if repetition == 0:
        return 1, 1
    elif repetition == 1:
        return 6, 2
    else:
        new_interval = round(interval_days * ef)
        return new_interval, repetition + 1


def process_sm2_review(word, quality):
    """
    Принимает слово (dict из БД) и оценку качества (0-5)
    Возвращает обновленные параметры для сохранения в БД
    """
    old_ef = word['ef']
    old_repetition = word['repetition']
    old_interval = word['interval_days']

    new_ef = calculate_new_ef(old_ef, quality)

    if quality >= 3:
        new_interval, new_repetition = calculate_next_interval(
            old_repetition, old_interval, new_ef, quality
        )
    else:
        new_interval = 1
        new_repetition = 0

    today = datetime.datetime.now().date()
    next_review = today + datetime.timedelta(days=new_interval)

    return {
        'ef': new_ef,
        'repetition': new_repetition,
        'interval_days': new_interval,
        'next_review_date': next_review,
        'last_reviewed': datetime.datetime.now()
    }


def get_quality_keyboard(is_correct):
    """
    Возвращает клавиатуру с оценками в зависимости от правильности ответа
    """
    from telebot import types

    keyboard = types.InlineKeyboardMarkup(row_width=1)

    if is_correct:
        btn5 = types.InlineKeyboardButton(
            "🟢 5 - Мгновенно, без усилий",
            callback_data="quality_5"
        )
        btn4 = types.InlineKeyboardButton(
            "🟢 4 - Быстро, немного подумал",
            callback_data="quality_4"
        )
        btn3 = types.InlineKeyboardButton(
            "🟡 3 - С трудом, но вспомнил",
            callback_data="quality_3"
        )
        keyboard.add(btn5, btn4, btn3)
    else:
        btn2 = types.InlineKeyboardButton(
            "🟠 2 - Ошибся, но слово знакомое",
            callback_data="quality_2"
        )
        btn1 = types.InlineKeyboardButton(
            "🔴 1 - Ошибся, едва вспомнил",
            callback_data="quality_1"
        )
        btn0 = types.InlineKeyboardButton(
            "⚫ 0 - Полностью забыл",
            callback_data="quality_0"
        )
        keyboard.add(btn2, btn1, btn0)

    return keyboard