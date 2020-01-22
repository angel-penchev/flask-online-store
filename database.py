import sqlite3

DB_NAME = 'database/database.sqlite3'

conn = sqlite3.connect(DB_NAME)

conn.cursor().execute('''
    CREATE TABLE IF NOT EXISTS users
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            telephone TEXT NOT NULL
        )
''')

conn.commit()

conn.cursor().execute('''
    CREATE TABLE IF NOT EXISTS ads
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            price TEXT NOT NULL,
            date_created TEXT NOT NULL,
            is_active INTEGER NOT NULL,
            owner_id INTEGER,
            buyer_id INTEGER,
            FOREIGN KEY(owner_id) REFERENCES users(id),
            FOREIGN KEY(buyer_id) REFERENCES users(id)
        )
''')

conn.commit()


class DB:
    def __enter__(self):
        self.conn = sqlite3.connect(DB_NAME)
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()
