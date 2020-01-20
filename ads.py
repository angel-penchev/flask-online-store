from database import DB

class Ads:
    def __init__(self, id, title, description, price, date_created, is_active, owner_id):
        self.id = id
        self.title = title
        self.description = description
        self.price = price
        self.date_created = date_created
        self.is_active = is_active
        self.owner_id = owner_id

    def create(self):
        with DB() as db:
            db.execute(
                '''
                INSERT INTO users (id, title, description, price, date_created, is_active, owner_id)
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