from stackquery import app
from stackquery.database import Base
from stackquery.models import DictSerializable
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from sqlalchemy import Column, Integer, String


class AuthUser(Base, DictSerializable):
    '''Authenticated user database representation'''
    __tablename__ = 'auth_user'
    id = Column(Integer, primary_key=True)
    username = Column('username', String(20), index=True)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=60):
        serializer = Serializer(app.config['SECRET_KEY'],
                                expires_in=expiration)
        return serializer.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        serializer = Serializer(app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = AuthUser.query.get(data['id'])
        return user
