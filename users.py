import hashlib

from database import DB

from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired
)

SECRET_KEY = 'kAo@iNwkkm^vT.ic$^x0qxNppsm3ou$*Gxje4j1^Yg0alrrmyqfy0c!8euc@t*e!e'


class User:
    def __init__(self, id, email, password, name, address, telephone):
        self.id = id
        self.email = email
        self.password = password
        self.name = name
        self.address = address
        self.telephone = telephone

    def create(self):
        with DB() as db:
            db.execute(
                '''
                INSERT INTO users (email, password, name, address, telephone)
                VALUES ({}, {}, {}, {}, {})
                '''.format(
                    self.email,
                    self.password,
                    self.name,
                    self.address,
                    self.telephone))
            return self

    @staticmethod
    def all():
        with DB() as db:
            rows = db.execute('SELECT * FROM users').fetchall()
            return [User(*row) for row in rows]

    @staticmethod
    def to_dict(user):
        return {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'address': user.address,
            'telephone': user.telephone
        }

    @staticmethod
    def find_by(column, data):
        if not data:
            return None
        with DB() as db:
            row = db.execute(
                'SELECT * FROM users WHERE {} = {}'.format(column, data)
            ).fetchone()
            if row:
                return User(*row)

    @staticmethod
    def update(id, column, data):
        with DB() as db:
            db.execute(
                '''
                UPDATE users
                SET {} = "{}"
                WHERE id = {}
                '''.format(column, data, id))
        return

    @staticmethod
    def delete(id):
        with DB() as db:
            db.execute(
                '''
                DELETE FROM users
                WHERE id = {}
                '''.format(id))
        return

    @staticmethod
    def get_bought_ads(id):
        with DB() as db:
            db.execute(
                "SELECT * FROM ads WHERE owner_id={} AND is_active=0".format(id))
            bought_ads = db.fetchall()
        return bought_ads

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verify_password(self, password):
        return self.password == hashlib.sha256(password.encode('utf-8')).hexdigest()

    def generate_token(self):
        s = Serializer(SECRET_KEY, expires_in=604800)
        return s.dumps({'email': self.email})

    @staticmethod
    def verify_token(token):
        s = Serializer(SECRET_KEY)
        try:
            s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        return User.find_by('email', s.loads(token)['email'])
