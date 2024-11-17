from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from encryptor import encrypt, decrypt
db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.LargeBinary, unique=True, nullable=False)  # Зашифрованное имя пользователя
    password = db.Column(db.LargeBinary, nullable=False)  # Зашифрованный пароль
    email = db.Column(db.LargeBinary, unique=True, nullable=False)  # Зашифрованный email
    posts = db.relationship('Post', backref='author', lazy=True)

    def set_password(self, password, key_schedule):
        self.password = encrypt(password.encode('utf-8'), key_schedule)

    def check_password(self, password, key_schedule):
        decrypted_password = decrypt(self.password, key_schedule).decode('utf-8')
        return decrypted_password == password

    def set_username(self, username, key_schedule):
        self.username = encrypt(username.encode('utf-8'), key_schedule)

    def get_username(self, key_schedule):
        return decrypt(self.username, key_schedule).decode('utf-8')

    def set_email(self, email, key_schedule):
        self.email = encrypt(email.encode('utf-8'), key_schedule)

    def get_email(self, key_schedule):
        return decrypt(self.email, key_schedule).decode('utf-8')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.LargeBinary, nullable=False)  # Хранение шифрованного контента
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
