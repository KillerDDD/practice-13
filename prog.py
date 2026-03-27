import sqlite3

#Устанавливаем соединение с базой данных
connection = sqlite3.connect('prodykt_db.db')
cursor = connection.cursor()

#Создаем таблицу Users
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER PRIMARY KEY,
ussername TEXT NOT NULL,
email TEXT NOT NULL,
age INTEGER 
)
''')
#Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()
