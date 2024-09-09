import psycopg2

conn = psycopg2.connect(database="chatbot",
        host="postgres",
        user="postgres",
        password="MySecretPassword123!@#",
        port="5432")

cursor = conn.cursor()

cursor.execute("SELECT * FROM session;")

print(cursor.fetchall())


