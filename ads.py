from database import DB

class Ads:
    def __init__(self, id, title, description, price, date_created, is_active, owner_id, buyer_id):
        self.id = id
        self.title = title
        self.description = description
        self.price = price
        self.date_created = date_created
        self.is_active = is_active
        self.owner_id = owner_id
        self.buyer_id = buyer_id

    def create(self):
        with DB() as db:
            db.execute(
                '''
                INSERT INTO ads (id, title, description, price, date_created, is_active, owner_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.id,
                    self.title,
                    self.description,
                    self.price,
                    self.date_created,
                    self.is_active,
                    self.owner_id))
            return self

    @staticmethod
    def all():
        with DB() as db:
            rows = db.execute('SELECT * FROM ads').fetchall()
            return [Ads(*row) for row in rows]

    @staticmethod
    def find_by(column, data):
        if not data:
            return None
        with DB() as db:
            row = db.execute(
                'SELECT * FROM ads WHERE {} = ?'.format(column),
                (data,)
            ).fetchone()
            if row:
                return Ads(*row)

    @staticmethod
    def update(id, column, data):
        with DB() as db:
            db.execute(
                '''
                UPDATE ads
                SET {} = "{}"
                WHERE id = {}
                '''.format(column, data, id))
        return

    @staticmethod
    def delete(id):
        with DB() as db:
            db.execute(
                '''
                DELETE FROM ads
                WHERE id = {}
                '''.format(id))
        return
            