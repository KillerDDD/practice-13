import sqlite3

#Устанавливаем соединение с базой данных
connection = sqlite3.connect('prodykt_db.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER PRIMARY KEY,
ussername TEXT NOT NULL,
email TEXT NOT NULL,
age INTEGER 
)
''')
connection.commit()

cursor.execute('INSERT INTO Users (ussername, email, age) VALUES (?, ?, ?)', ('newuser', 'newuser@example.com', 28))
connection.commit()

cursor.execute('SELECT * FROM Users')
users = cursor.fetchall()
for user in users:
	print(user)

cursor.execute('UPDATE Users SET age = ? WHERE ussername = ?', (29, 'newuser'))
connection.commit()

cursor.execute('SELECT * FROM Users')
users = cursor.fetchall()
for user in users:
	print(user)

cursor.execute('DELETE FROM Users WHERE ussername =?', ('newuser',))
connection.commit()

cursor.execute('SELECT * FROM Users')
users = cursor.fetchall()
for user in users:
	print(user)
#Сохраняем изменения и закрываем соединение
connection.close()
