from flask_app import db

interests_table = db.Table('interests_user',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('interest_id', db.Integer, db.ForeignKey('interests.id')))
show_profile = db.Table('show_profile',
                        # чья анкета показана. будем использовать для того, чтобы показать пользователю, какое кол-во человек видели анкету
                        db.Column('showed_profile_id', db.Integer, db.ForeignKey('user.id')),
                        # кто увидел анкету. будем использовать для того, чтобы не показывать пользователю одни и те же анкеты
                        db.Column('sight_profile_id', db.Integer, db.ForeignKey('user.id')))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    application_id = db.Column(db.String(100), unique=True)  # для того, чтобы не приходилось реализовывать регистрацию, будем запоминать айди приложения, с которого был запрос
    age = db.Column(db.String(3))
    gender = db.Column(db.String(20))  # male, female
    # status_dialog = db.Column(db.String(30), default='not_in_dialog')  # not_in_dialog, in_dialog, search_dialog
    networks = db.Column(db.String(150))  # пользователь может оставить свои контакты
    about_me = db.Column(db.String(500))  # если захочет, пользователь может рассказать о себе
    interests = db.relationship('Interests', secondary=interests_table, backref=db.backref('users', lazy='dynamic'))  # связь many-to-many с таблицей интересов
    sight_profiles = db.relationship('User', secondary=show_profile, primaryjoin=(show_profile.c.showed_profile_id == id),
                                     secondaryjoin=(show_profile.c.sight_profile_id == id),
                                     backref=db.backref('showed_profile_id', lazy='dynamic'), lazy='dynamic')

    def add_sight_profile(self, user):
        if user not in self.sight_profiles:
            self.sight_profiles.append(user)

    def __str__(self):  # нужен для отображения анкет
        if self.gender == 'male':
            gen = 'мужской'
        else:
            gen = 'женский'
        res = 'Имя: {}\n\nВозраст: {}\n\nПол: {}\n\nКонтакты:\n{}\n\nОбо мне:\n{}\n\nИнтересы: '.format(self.name, self.age, gen, self.networks, self.about_me)
        for interest in self.interests:
            if len(res) + len(interest.text) + 1 <= 1020:
                res += interest.text + ','
            else:
                res = res[:-1] + '....'
        return res[:-1]


class Interests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), unique=True)  # текст интереса. каждый интерес уникален и должен быть представлен в базе данных всего один раз

    def __repr__(self):
        return '<Interest {}>'.format(self.text)
