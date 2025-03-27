from mysql.connector import connect, Error
import datetime

try:
    with connect(
        host='localhost',
        user='root',
        password='Mimir@042008',
        database = 'Mimir'
    ) as connection:
        create_table_users = '''
        CREATE TABLE users(
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        user BIGINT NOT NULL
        )
        '''

        create_table_dictionaries = '''
        CREATE TABLE dictionaries(
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        dictionary VARCHAR(100) NOT NULL,
        user_id BIGINT NOT NULL,
        FOREIGN KEY (user_id) references users(id)
        )
        '''

        create_table_words = '''
        CREATE TABLE words(
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        rus VARCHAR(100) NOT NULL,
        eng VARCHAR(100) NOT NULL,
        repeats BIGINT NOT NULL,
        status BIGINT NOT NULL,
        dict_id BIGINT NOT NULL,
        FOREIGN KEY (dict_id) references dictionaries(id)
        )
        '''

        create_table_temporary = '''
        CREATE TABLE temporary(
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        rus VARCHAR(100) NOT NULL,
        eng VARCHAR(100) NOT NULL,
        user_id BIGINT NOT NULL,
        FOREIGN KEY (user_id) references users(id)
        )
        '''

        create_table_repeats456 = '''
        CREATE TABLE repeats456(
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        repeat456 BIGINT NOT NULL,
        date VARCHAR(100) NOT NULL
        )
        '''

        with connection.cursor() as cursor:
            for i in [create_table_users, create_table_dictionaries, create_table_words, create_table_temporary, create_table_repeats456]:
                cursor.execute(i)
            connection.commit()
            print('Таблицы созданы')

        with connection.cursor() as cursor:
            for i in range(4, 7):
                cursor.execute(f"INSERT INTO repeats456(repeat456, date) VALUES ({i}, '{str(datetime.datetime.now().date())[5:]}')")
            connection.commit()
            print('Дата добавлена')

except Error as e:
    print(e)