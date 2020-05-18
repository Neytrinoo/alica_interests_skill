from flask_app import app, db
from werkzeug.security import generate_password_hash, check_password_hash

interests_table = db.Table('interests_user',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('interest_id', db.Integer, db.ForeignKey('interests.id')))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    age = db.Column(db.String(3), default='Неизвестно')  # если захочет, пользователь может не указывать свой возраст
    gender = db.Column(db.String(20))  # male, female, none
    status_dialog = db.Column(db.String(30), default='not_in_dialog')  # not_in_dialog, in_dialog, search_dialog
    networks = db.Column(db.String(200))  # пользователь может оставить свои контакты
    about_me = db.Column(db.String(800))  # если захочет, пользователь может рассказать о себе
    interests = db.relationship('Interests', secondary=interests_table, backref=db.backref('users', lazy='dynamic'))  # связь many-to-many с таблицей интересов


class Interests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256), unique=True)  # текст интереса. каждый интерес уникален и должен быть представлен в базе данных всего один раз

    def __repr__(self):
        return '<Interest {}>'.format(self.text)
