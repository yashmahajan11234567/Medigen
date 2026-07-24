
import sqlite3
conn = sqlite3.connect(r'C:\Users\hitoy\Downloads\Medigen\medigen.db')
cursor = conn.cursor()
cursor.execute('SELECT name, sql FROM sqlite_master WHERE type="index" AND name LIKE "uq_%"')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]}')
conn.close()

