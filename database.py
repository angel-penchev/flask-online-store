import sqlite3

DB_NAME = 'database/database.sqlite3'

conn = sqlite3.connect(DB_NAME)
# TODO: Create user & ad tables
conn.commit()


class DB:
    def __enter__(self):
        self.conn = sqlite3.connect(DB_NAME)
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()
