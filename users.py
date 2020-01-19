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
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    self.email,
                    self.password,
                    self.name,
                    self.address,
                    self.telephone))
            return self

    @staticmethod
    def find_by_email(email):
        if not email:
            return None
        with DB() as db:
            row = db.execute(
                'SELECT * FROM users WHERE email = ?',
                (email,)
            ).fetchone()
            if row:
                return User(*row)

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verify_password(self, password):
        return self.password == hashlib.sha256(password.encode('utf-8')).hexdigest()

    def generate_token(self):
        s = Serializer(SECRET_KEY, expires_in=6000)
        return s.dumps({'email': self.email})

    @staticmethod
    def verify_token(token):
        s = Serializer(SECRET_KEY)
        try:
            s.loads(token)
        except SignatureExpired:
            return False
        except BadSignature:
            return False
        return True
