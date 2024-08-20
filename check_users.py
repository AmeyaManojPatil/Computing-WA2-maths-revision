import sqlite3

conn = sqlite3.connect("revision_user.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM Users")
users = cursor.fetchall()

print("Users in database:")
for user in users:
    print(user)

conn.close()
