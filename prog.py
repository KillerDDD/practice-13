import sqlite3

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

cursor.execute('SELECT * FROM Users')
users = cursor.fetchall()
for user in users:
	print(user)

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

first_user = cursor.fetchone()
print(first_user)

first_five_user = cursor.fetchmany(5)
print(first_five_user)

all_user = cursor.fetchall()
print(all_user)

# Создаем таблицу Tasks
cursor.execute('''
CREATE TABLE IF NOT EXISTS Tasks ( id INTEGER PRIMARY KEY,
title TEXT NOT NULL,
status TEXT DEFAULT 'Not Started'
)
''')
# Функция для добавления новой задачи
def add_task(title):
	cursor.execute('INSERT INTO Tasks (title) VALUES(?)', (title,))
	connection.commit()
# Функция для обновления статуса задачи
def update_task_status(task_id, status):
	cursor.execute('UPDATE Tasks SET status = ? WHERE id = ?', (status, task_id))
	connection.commit()
# Функция для вывода списка задач
def list_tasks():
	cursor.execute('SELECT * FROM Tasks')
	tasks = cursor.fetchall()
	for task in tasks:
		print(task)
# Добавляем задачи
add_task('Подготовить презентацию')
add_task('Закончить отчет')
add_task('Подготовить ужин')
# Обновляем статус задачи 
update_task_status(2, 'In Progress')
# Выводим список задач
list_tasks()
# Закрываем соединение
connection.close()
