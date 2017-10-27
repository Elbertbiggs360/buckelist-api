from flask_bcrypt import Bcrypt
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature, SignatureExpired
)

from app.models.baseModel import BaseModel, db
from instance.config import Config

bcrypt = Bcrypt()


class User(BaseModel):
    '''This class represents the user model'''
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    _password_hash = db.Column(db.String(255))

    @property
    def password(self):
        ''' Method that is run when password property is called '''
        return 'Password: Write Only'

    @password.setter
    def password(self, password):
        ''' Generate password hash '''
        self._password_hash = bcrypt.generate_password_hash(
            password, Config.BCRYPT_LOG_ROUNDS).decode()

    def exists(self):
        ''' Check if user exists '''
        user = User.query.filter_by(email=self.email).first()
        return user if user else False

    def verify_password(self, password):
        ''' Method to verify that user's password matches password provided '''
        return bcrypt.check_password_hash(self._password_hash, password)

    def generate_auth_token(self, duration=Config.AUTH_TOKEN_DURATION):
        ''' Method for generating a JWT authentication token '''
        serializer = Serializer(Config.SECRET_KEY, expires_in=int(duration))
        return serializer.dumps({
               'id': self.id,
               'email': self.email,
               'first_name': self.first_name,
               'last_name': self.last_name
               })

    @staticmethod
    def verify_authentication_token(token):
        ''' Method to verify authentication token '''
        serializer = Serializer(Config.SECRET_KEY)
        try:
            data = serializer.loads(token)
        except SignatureExpired:
            return False
        except BadSignature:
            return False
        return data['id'] if data['id'] else False

    def delete_user(self, deep_delete=False):
        ''' Method to delete user '''
        if not deep_delete:
            if self.deactivate():
                return True
            return False        
        if self.exists():
            self.delete()
            return True
        return False

    def save_user(self):
        ''' Method to save user '''
        user = self.exists()
        if user:
            if user.active:
                return False
            else:
                user.active = True
        self.save()
        return True

    def __repr__(self):
        return '<User %r>' % self.name()

    def __str__(self):
        return '{0}'.format(self.name())
