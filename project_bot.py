import telebot
from mysql.connector import connect, Error
import random
import threading
import datetime
token = '8058792536:AAFEnnX90hV2M4ncgsA4jEWEXbP2TteamDE'

def group1():
  threading.Timer(3600.0, group1).start()
  update_tables('words', 'status = 1', 'repeats = 1')
def group2():
  threading.Timer(86400.0, group2).start()
  update_tables('words', 'status = 1', 'repeats = 2')
def group3():
  threading.Timer(259200.0, group3).start()
  update_tables('words', 'status = 1', 'repeats = 3')
def group4():
  threading.Timer(86400.0, group4).start()
  date = select_where('repeats456', 'date', 'repeat456 = 4')
  if date[0][0][5:] == str(datetime.datetime.now().date()):
      update_tables('words', 'status = 1', 'repeats = 4')
def group5():
  threading.Timer(86400.0, group5).start()
  date = select_where('repeats456', 'date', 'repeat456 = 5')
  if date[0][0][5:] == str(datetime.datetime.now().date()):
    update_tables('words', 'status = 1', 'repeats = 5')
def group6():
  threading.Timer(86400.0, group6).start()
  date = select_where('repeats456', 'date', 'repeat456 = 6')
  if date[0][0] == str(datetime.datetime.now().date()):
    update_tables('words', 'status = 1', 'repeats = 6')

def change_status(message, repeats, bot):
    try:
        ind_user = select_where('users', 'id', f'user={message}')
        row = select_where('dictionaries', 'dictionary', f'user_id={ind_user[0][0]}')
        if row != None:
            for i in row:
                ind_dict = select_where('dictionaries', 'id', f'user_id={ind_user[0][0]} and dictionary="{i[0]}"')
                update_tables('words', 'status = 1', f'repeats = {repeats} AND dict_id = {ind_dict[0][0]}')
        bot.send_message(message, 'Пора повторить слова')
    except:
        pass

def update_tables(table_name, values, where):
    try:
        with connect(
                host='localhost',
                user='root',
                password='Mimir@042008',
                database='Mimir'
        ) as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"UPDATE {table_name} SET {values} WHERE {where}")
                    connection.commit()
            finally:
                connection.close()

    except Error as e:
        print(e)

def delete_tables(table_name):
    try:
        with connect(
                host='localhost',
                user='root',
                password='Mimir@042008',
                database='Mimir'
        ) as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"DELETE FROM {table_name}")
                    connection.commit()
            finally:
                connection.close()

    except Error as e:
        print(e)

def insert_tables(table_name, column, values):
    try:
        with connect(
                host='localhost',
                user='root',
                password='Mimir@042008',
                database='Mimir'
        ) as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT {column} FROM {table_name}")
                    row = cursor.fetchall()

                    try:
                        ind = row.index((values,))
                    except:
                        with connection.cursor() as cursor:
                            insert_query = f"INSERT INTO {table_name} ({column}) VALUES ({values})"
                            cursor.execute(insert_query)
                            connection.commit()
                    try:
                        ind = row.index((values,))
                        return ind

                    except:
                        pass

            finally:
                connection.close()

    except Error as e:
        print(e)

def insert_dict(table_name, column1, column2, values1, values2):
    try:
        with connect(
                host='localhost',
                user='root',
                password='Mimir@042008',
                database='Mimir'
        ) as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT {column1} FROM {table_name}")
                    row = cursor.fetchall()
                    try:
                        val = ''
                        for i in values1:
                            if i != "'":
                                val += i
                            else:
                                break
                        if row == [] or row == None:
                            ind = row.index((values1,))
                        else:
                            for i in row:
                                if val in i[0]:
                                    pass
                                else:
                                    ind = row.index((values1,))

                    except:
                        with connection.cursor() as cursor:
                            insert_query = f"INSERT INTO {table_name} ({column1}, {column2}) VALUES ('{values1}', {values2})"
                            cursor.execute(insert_query)
                            connection.commit()
                    try:
                        ind = row.index((values1,))
                        return ind

                    except:
                        pass

            finally:
                connection.close()

    except Error as e:
        print(e)


def select_where(table_name, column, where):
    try:
        with connect(
                host='localhost',
                user='root',
                password='Mimir@042008',
                database='Mimir'
        ) as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT {column} FROM {table_name} WHERE {where}")
                    row = cursor.fetchall()
                    return row

            finally:
                connection.close()

    except Error as e:
        print(e)

def delete_where(table_name, where):
    try:
        with connect(
                host='localhost',
                user='root',
                password='Mimir@042008',
                database='Mimir'
        ) as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"DELETE FROM {table_name} WHERE {where}")
                    connection.commit()
            finally:
                connection.close()

    except Error as e:
        print(e)

def delete_something(message, bot):
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Удалить слово", callback_data="delete_word")
    button2 = telebot.types.InlineKeyboardButton(text="Удалить словарь", callback_data="delete_dict")
    keyboard.add(button1)
    keyboard.add(button2)
    bot.send_message(message, "Что вы хотите удалить?", reply_markup=keyboard)

def keyboard(message, bot):
    keyboard = telebot.types.InlineKeyboardMarkup()

    button_repeat_words = telebot.types.InlineKeyboardButton(text="Повторить слова", callback_data="repeat_words")
    button_new_word = telebot.types.InlineKeyboardButton(text="Добавить новое слово", callback_data="new_word")
    button_dictionaries = telebot.types.InlineKeyboardButton(text="Словари", callback_data="dictionaries")
    button_delete = telebot.types.InlineKeyboardButton(text="Удалить", callback_data="delete")
    keyboard.add(button_repeat_words)
    keyboard.add(button_new_word)
    keyboard.add(button_dictionaries)
    keyboard.add(button_delete)

    bot.send_message(message.chat.id, "Меню", reply_markup=keyboard)

def all_dicts(message, bot, command):
    try:
        ind = select_where('users', 'id', f'user={message}')
        row = select_where('dictionaries', 'dictionary', f'user_id={ind[0][0]}')
        keyboard = telebot.types.InlineKeyboardMarkup()
        if row != None:
            for i in row:
                button = telebot.types.InlineKeyboardButton(text=i[0].title(), callback_data=f"{command}{i[0]}")
                keyboard.add(button)

        button_dict = telebot.types.InlineKeyboardButton(text="Добавить словарь", callback_data="new_dict")
        keyboard.add(button_dict)
        bot.send_message(message, "Выберите словарь", reply_markup=keyboard)
    except:
        bot.send_message(message, "Что-то пошло не так. Попробуйте ещё раз")

def new_word(list_word, message, bot):
    try:
        ind_user = select_where('users', 'id', f'user={message}')
        ind_dict = select_where('dictionaries', 'id', f'user_id={ind_user[0][0]} and dictionary="{list_word[0]}"')
        insert_dict('words', 'rus, eng', 'repeats, dict_id, status', f"{list_word[1].lower()}', '{list_word[2].lower()}", f'1, {ind_dict[0][0]}, 1')
        bot.send_message(message, f'«{list_word[1].lower()} - {list_word[2].lower()}» добавлено в словарь «{list_word[0]}»')
    except:
        bot.send_message(message, 'Что-то пошло не так. Попробуйте ещё раз')
def print_dict(name_dict, message, bot):
    ind_user = select_where('users', 'id', f'user={message}')
    ind_dict = select_where('dictionaries', 'id', f'user_id={ind_user[0][0]} and dictionary="{name_dict.lower()}"')
    row = select_where('words', 'rus, eng', f'dict_id={ind_dict[0][0]}')
    if row == []:
        bot.send_message(message, f'В словаре «{name_dict.title()}» нет слов')
    else:
        row_str = ''
        for i in row:
            row_str = row_str + '\n'+ i[1] + ' - ' + i[0]
        bot.send_message(message, f'Словарь «{name_dict.title()}»:\n{row_str}')

def repeat_words(message, bot):
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_repeat_words = telebot.types.InlineKeyboardButton(text="Все слова", callback_data="repeat_all_words")
    button_dictionaries = telebot.types.InlineKeyboardButton(text="Слова из словаря", callback_data="dictionary_words")
    keyboard.add(button_repeat_words)
    keyboard.add(button_dictionaries)

    bot.send_message(message, "Какие слова вы хотите повторить?", reply_markup=keyboard)

def all_words(message, bot):
    delete_tables('temporary')
    ind_user = select_where('users', 'id', f'user={message}')
    ind_dict = select_where('dictionaries', 'id', f'user_id={ind_user[0][0]}')
    words_dict = {}
    if ind_dict != None:
        for i in ind_dict:
            row = select_where('words', 'rus, eng', f'dict_id={i[0]} and status = 1')
            for j in row:
                words_dict[j[0]] = j[1]
    if words_dict=={}:
        bot.send_message(message, "Слов для повторения нет")
    elif len(words_dict) < 10:
        bot.send_message(message, "Слов для повторения должно быть минимум десять")
        words_dict = {}
        return words_dict
    else:
        bot.send_message(message, 'За раз я буду отправлять 10 слов для повторения')
        strr = 'Слова, которые нужно повторить:\n\n'
        n = random.sample(list(words_dict.keys()), k=10)
        new_dict = {}
        for key in n:
            new_dict[key] = words_dict[key]
            strr = strr + new_dict[key] + ' - ' + key + '\n'

        bot.send_message(message, strr)
        bot.send_message(message, "Поехали!")
        return new_dict

def dictionary_words(message, bot, name_dict):
    name_dict = name_dict.lower()
    try:
        delete_tables('temporary')
        ind_user = select_where('users', 'id', f'user={message}')
        ind_dict = select_where('dictionaries', 'id', f'user_id={ind_user[0][0]} and dictionary="{name_dict}"')
        row = select_where('words', 'rus, eng', f'dict_id={ind_dict[0][0]} and status = 1')
        words_dict = {}
        for j in row:
            words_dict[j[0]] = j[1]
        if words_dict == {}:
            bot.send_message(message, f'В словаре «{name_dict.title()}» нет слов')
        elif len(words_dict) < 10:
            bot.send_message(message, "Слов для повторения должно быть минимум десять")
            words_dict = {}
            return words_dict
        else:
            bot.send_message(message, 'За раз я буду отправлять 10 слов для повторения')
            strr = 'Слова, которые нужно повторить:\n\n'
            n = random.sample(list(words_dict.keys()), k=10)
            new_dict = {}
            for key in n:
                new_dict[key] = words_dict[key]
                strr = strr + new_dict[key] + ' - ' + key + '\n'

            bot.send_message(message, strr)
            bot.send_message(message, "Поехали!")
            return new_dict

    except:
        bot.send_message(message, f'В словаре «{name_dict.title()}» нет слов')

def repeat(message, call_message, bot, words_dict):
    ind_user = select_where('users', 'id', f'user={message}')
    for key, values in words_dict.items():
        insert_dict('temporary', 'rus, eng', 'user_id', f"{key}', '{values}", ind_user[0][0])

group1()
group2()
group3()
group4()
group5()
group6()

def change_date(number):
    if number == 4:
        plus = 7
        month_plus = 0
    elif number == 5:
        plus = 14
        month_plus = 0
    else:
        plus = 0
        month_plus = 1
    current_time = str(datetime.datetime.now().date())[5:]
    current_time = list(current_time)
    if int[current_time[-2]+current_time[-1]] + plus > 30:
        month_plus = 1
        plus = int[(str(current_time[0]) + str(current_time[1]))] - plus
    day = int[current_time[-2]+current_time[-1]] + plus
    date = str(list(current_time)[:3]) + str(day)
    update_tables('repeats456', date, f'repeat456={number}')

def delete_word(text, chat_id, bot):
    try:
        ind_user = select_where('users', 'id', f'user={chat_id}')
        ind_dict = select_where('dictionaries', 'id', f'user_id={ind_user[0][0]}')
        delete_where('words', f"rus='{text.lower()}' and dict_id={ind_dict[0][0]}")
        bot.send_message(chat_id, f'Слово «{text.lower()}» удалено')
    except:
        bot.send_message(chat_id, f'Слова «{text.lower()}» нет среди ваших слов')

def delete_dict(chat_id, bot, text):
    ind_user = select_where('users', 'id', f'user={chat_id}')
    delete_where('dictionaries', f"user_id={ind_user[0][0]} and dictionary='{text.lower()}'")
    bot.send_message(chat_id, f'Словарь «{text.title()}» удален')

def telegram_bot(token):
    bot = telebot.TeleBot(token)


    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(message.chat.id,'Приветствую вас.\nЯ - Мимир, бот для запоминания английских слов.\nЧтобы открыть меню, введите /menu')
        insert_tables('users', 'user', message.chat.id)
        keyboard(message, bot)

    @bot.message_handler(commands=['menu'])
    def menu_message(message):
        insert_tables('users', 'user', message.chat.id)
        keyboard(message, bot)


    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        words_dict = {}
        if call.message:
            if call.data == "repeat_words":
                repeat_words(call.message.chat.id, bot)
            if call.data == "new_word":
                all_dicts(call.message.chat.id, bot, 'new_word_in_')
            if 'new_word_in_' in call.data:
                list_new_word[0] = call.data[12:]
                bot.send_message(call.message.chat.id, 'Напишите новое слово на русском')
                bot.register_next_step_handler(call.message, rus_name_new_word)
            if call.data == "dictionaries":
                all_dicts(call.message.chat.id, bot, 'dict_')
            if call.data == "new_dict":
                bot.send_message(call.message.chat.id, 'Напишите название словаря')
                bot.register_next_step_handler(call.message, name_new_dict)
            if call.data == "repeat_all_words":
                words_dict = all_words(call.message.chat.id, bot)
                if words_dict != {} and words_dict != None:
                    repeat(call.message.chat.id, call.message, bot, words_dict)
                    bot.send_message(call.message.chat.id, list(words_dict.keys())[0])
                    bot.register_next_step_handler(call.message, repeat1)
            if call.data == 'dictionary_words':
                all_dicts(call.message.chat.id, bot, 'words_from_')
            if 'words_from_' in call.data:
                words_dict = dictionary_words(call.message.chat.id, bot, call.data[11:])
                if words_dict != {} and words_dict != None:
                    repeat(call.message.chat.id, call.message, bot, words_dict)
                    bot.send_message(call.message.chat.id, list(words_dict.keys())[0])
                    bot.register_next_step_handler(call.message, repeat1)
            if call.data == 'delete':
                delete_something(call.message.chat.id, bot)
            if call.data == 'delete_word':
                bot.send_message(call.message.chat.id, 'Введите на русском слово, которое хотите удалить')
                bot.register_next_step_handler(call.message, name_delete_word)
            if call.data == 'delete_dict':
                all_dicts(call.message.chat.id, bot, 'delete_dict')
            elif 'delete_dict' in call.data:
                delete_dict(call.message.chat.id, bot, call.data[11:])
            elif 'dict_' in call.data:
                print_dict(call.data[5:], call.message.chat.id, bot)



    def name_delete_word(message):
        delete_word(message.text.lower(), message.chat.id, bot)

    def name_new_dict(message):
        ind = insert_tables('users', 'user', message.chat.id) + 1
        insert_dict('dictionaries', 'dictionary', 'user_id', message.text.lower(), ind)
        bot.send_message(message.chat.id, f"Словарь «{message.text.title()}» добавлен")

    def rus_name_new_word(message):
        list_new_word[1] = message.text.lower()
        bot.send_message(message.chat.id, 'Напишите новое слово на английском')
        bot.register_next_step_handler(message, eng_name_new_word)

    def eng_name_new_word(message):
        list_new_word[2] = message.text.lower()
        new_word(list_new_word, message.chat.id, bot)



    def rep(message, i):
        ind_user = select_where('users', 'id', f'user={message.chat.id}')
        ind_dict = select_where('dictionaries', 'id', f'user_id={ind_user[0][0]}')
        right_answer = select_where('temporary', 'eng', f'user_id={ind_user[0][0]}')
        ind_repeat = select_where('words', 'repeats', f"eng = '{right_answer[i][0]}'")
        if right_answer[i][0] == message.text.lower():
            bot.send_message(message.chat.id, 'Правильно!')
            if ind_repeat[0][0] > 6:
                bot.send_message(message.chat.id, 'Вы выучили слово!')
            else:
                update_tables('words', f'status = 0, repeats = {ind_repeat[0][0] + 1}',
                              f'eng = "{right_answer[i][0]}"')
        else:
            bot.send_message(message.chat.id, f'Вы ошиблись!\nПравильный ответ: «{right_answer[i][0]}»')
            if ind_repeat[0][0] != 1:
                update_tables('words', f'status = 1, repeats = {ind_repeat[0][0] - 1}',
                              f'eng = "{right_answer[i][0]}"')

        if ind_repeat[0][0] > 3:
            change_date(ind_repeat[0][0])
        next = select_where('temporary', 'rus', f'user_id={ind_user[0][0]}')
        if i != 9:
            bot.send_message(message.chat.id, next[i+1][0])
        else:
            pass

    def repeat1(message):
        rep(message.lower(), 0)
        bot.register_next_step_handler(message.lower(), repeat2)
    def repeat2(message):
        rep(message.lower(), 1)
        bot.register_next_step_handler(message.lower(), repeat3)
    def repeat3(message):
        rep(message.lower().lower(), 2)
        bot.register_next_step_handler(message.lower(), repeat4)
    def repeat4(message):
        rep(message.lower().lower(), 3)
        bot.register_next_step_handler(message.lower(), repeat5)
    def repeat5(message):
        rep(message.lower().lower(), 4)
        bot.register_next_step_handler(message.lower(), repeat6)
    def repeat6(message):
        rep(message.lower(), 5)
        bot.register_next_step_handler(message.lower(), repeat7)
    def repeat7(message):
        rep(message.lower(), 6)
        bot.register_next_step_handler(message.lower(), repeat8)
    def repeat8(message):
        rep(message.lower(), 7)
        bot.register_next_step_handler(message.lower(), repeat9)
    def repeat9(message):
        rep(message.lower(), 8)
        bot.register_next_step_handler(message.lower(), repeat10)
    def repeat10(message):
        rep(message.lower(), 9)
        bot.send_message(message.chat.id, 'Вы повторили все слова!')


    bot.polling(none_stop=True)


if __name__ == '__main__':
    words_dict = {}
    list_new_word = [0, 1, 2]
    telegram_bot(token)