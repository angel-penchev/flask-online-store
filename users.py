import hashlib

from database import DB

from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired
)

SECRET_KEY = 'kAo@iNwkkm^vT.ic$^x0qxNppsm3ou$*Gxje4j1^Yg0alrrmyqfy0c!8euc@t*e!e'


class User:
    def __init__(self, id, username, password, name, address, telephone):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.address = address
        self.telephone = telephone

    def create(self):
        with DB() as db:
            db.execute(
                '''
                INSERT INTO users (username, password, name, address, telephone)
                VALUES (?, ?, ?, ?, ?,)
                ''', (
                    self.username,
                    self.password,
                    self.name,
                    self.address,
                    self.telephone))
            return self
