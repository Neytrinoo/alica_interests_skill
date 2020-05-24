from flask_app import app
from flask import request
from models import *
from constants import *
from help_functions import search_numbers, get_suggests, set_editable_fields
from flask_app import db
import logging
import json


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)
    return json.dumps(response)


def create_profile(req, res):
    application_id = req['session']['application']['application_id']
    stage = sessionStorage[application_id]['now_command'][1]
    if stage == 0:  # имя
        sessionStorage[application_id]['create_profile'] = {}
        res['response']['text'] = CREATE_PROFILE[stage]
        sessionStorage[application_id]['now_command'][1] += 1
        return
    elif stage == 1:  # возраст
        if len(req['request']['original_utterance']) > 50:  # проверка имени
            res['response']['text'] = ERRORS_CREATE_PROFILE[stage - 1]
            return
        sessionStorage[application_id]['create_profile']['name'] = req['request']['original_utterance']
        res['response']['text'] = CREATE_PROFILE[stage]
        sessionStorage[application_id]['now_command'][1] += 1
        return
    elif stage == 2:  # пол
        age = search_numbers(req['request']['nlu']['entities'])
        if not age or age <= 0 or age > 999:  # проверка возраста
            res['response']['text'] = ERRORS_CREATE_PROFILE[stage - 1]
            return
        sessionStorage[application_id]['create_profile']['age'] = age
        res['response']['text'] = CREATE_PROFILE[stage]
        sessionStorage[application_id]['now_command'][1] += 1
        return
    elif stage == 3:  # соцсети
        if 'мужчина' not in req['request']['nlu']['tokens'] and 'женщина' not in req['request']['nlu']['tokens']:  # проверка гендера
            res['response']['text'] = ERRORS_CREATE_PROFILE[stage - 1]
            return
        if 'мужчина' in req['request']['nlu']['tokens']:
            sessionStorage[application_id]['create_profile']['gender'] = 'male'
        else:
            sessionStorage[application_id]['create_profile']['gender'] = 'female'
        res['response']['text'] = CREATE_PROFILE[stage]
        sessionStorage[application_id]['now_command'][1] += 1
        return
    elif stage == 4:  # о себе
        if len(req['request']['original_utterance']) > 150:  # проверка соцсетей
            res['response']['text'] = ERRORS_CREATE_PROFILE[stage - 1]
            return
        sessionStorage[application_id]['create_profile']['networks'] = req['request']['original_utterance']
        res['response']['text'] = CREATE_PROFILE[stage]
        sessionStorage[application_id]['now_command'][1] += 1
        return
    elif stage == 5:  # интересы
        if len(req['request']['original_utterance']) > 500:  # проверка информации "о себе"
            res['response']['text'] = ERRORS_CREATE_PROFILE[stage - 1]
            return
        sessionStorage[application_id]['create_profile']['about_me'] = req['request']['original_utterance']
        res['response']['text'] = CREATE_PROFILE[stage]
        sessionStorage[application_id]['now_command'][1] += 1
        return
    elif stage == 6:  # проверка валидации интересов, создание профиля
        interests = req['request']['original_utterance'].split(',')
        if len(interests) > 20:
            res['response']['text'] = ERRORS_CREATE_PROFILE[stage - 1]['interests_count_error']
            return
        user = User(name=sessionStorage[application_id]['create_profile']['name'], application_id=application_id, age=sessionStorage[application_id]['create_profile']['age'],
                    gender=sessionStorage[application_id]['create_profile']['gender'], networks=sessionStorage[application_id]['create_profile']['networks'],
                    about_me=sessionStorage[application_id]['create_profile']['about_me'])
        db.session.add(user)
        for interest in interests:
            interest = interest.rstrip().lstrip().lower()
            if len(interest) > 100:
                db.session.rollback()
                res['response']['text'] = ERRORS_CREATE_PROFILE[stage - 1]['len_interest_text_error']
                return
            if Interests.query.filter_by(text=interest).first():  # если интерес существует, просто добавляем в него нашего пользователя
                Interests.query.filter_by(text=interest).first().users.append(user)
            else:  # если нет - создаем интерес и добавляем
                inter = Interests(text=interest)
                inter.users.append(user)
                db.session.add(inter)
        db.session.commit()
        res['response']['text'] = AFTER_CREATED_PROFILE
        sessionStorage[application_id]['now_command'] = ['free_use']
        del sessionStorage[application_id]['create_profile']
        return


def get_profile_for_user(application_id, res):  # функция рекомендации анкеты пользователю
    user = User.query.filter_by(application_id=application_id).first()
    user_with_common_interests = set()  # таблица пользователей, с которыми совпали интересы
    for interest in user.interests:
        for us in interest.users:
            if us.application_id != application_id and us not in user.sight_profiles:  # если это не тот же самый пользователь и мы его еще не рекомендовали данному user
                user_with_common_interests.add(us)  # добавляем его в множество. использование множества исключает возможность дублирования пользователей
    # сортируем найденных пользователей по совпадениям интересов с исходным user
    user_with_common_interests = sorted(user_with_common_interests, key=lambda usr: set(usr.interests) & set(user.interests))
    if user_with_common_interests:  # если вообще есть пользователи с общими интересами, берем наиболее подходящего
        user_with_common_interests = user_with_common_interests[-1]
    else:  # если нет, берем первого, которого еще не рекомендовали
        for us in User.query.all():
            if us not in user.sight_profiles and us.application_id != application_id:
                user_with_common_interests = us
                break
        if not user_with_common_interests:  # если в бд нет подходящих пользователей, сообщаем об этом
            res['response']['text'] = NOT_USER_TO_RECOMMENDATION
            return
    user.sight_profiles.append(user_with_common_interests)
    db.session.commit()
    res['response']['text'] = str(user_with_common_interests)
    return


def edit_profile(req, res):
    user = User.query.filter_by(application_id=req['session']['application']['application_id']).first()
    if 'выйти' in req['request']['nlu']['tokens']:
        sessionStorage[user.application_id]['now_command'] = ['free_use']
        sessionStorage[user.application_id]['suggests'] = ARRAY_OF_AVAILABLE_COMMANDS
        res['response']['buttons'] = get_suggests(user.application_id)
        res['response']['text'] = 'Вы вышли из режима редактирования'
        return
    if sessionStorage[user.application_id]['now_command'][1] == 'none':  # если в данный момент пользователь выбирает, какое поле редактировать
        sessionStorage[user.application_id]['suggests'] = []
        res['response']['buttons'] = get_suggests(user.application_id)
        if 'имя' in req['request']['nlu']['tokens']:
            sessionStorage[user.application_id]['now_command'][1] = 'name'
            res['response']['text'] = 'Введите новое имя'
            return
        elif 'возраст' in req['request']['nlu']['tokens']:
            sessionStorage[user.application_id]['now_command'][1] = 'age'
            res['response']['text'] = 'Введите новый возраст'
            return
        elif 'пол' in req['request']['nlu']['tokens']:
            sessionStorage[user.application_id]['now_command'][1] = 'gender'
            res['response']['text'] = 'Введите новый пол'
            return
        elif 'контакты' in req['request']['nlu']['tokens']:
            sessionStorage[user.application_id]['now_command'][1] = 'networks'
            res['response']['text'] = 'Укажите ваши новые контакты'
            return
        elif 'обо' in req['request']['nlu']['tokens'] and 'мне' in req['request']['nlu']['tokens']:
            sessionStorage[user.application_id]['now_command'][1] = 'about_me'
            res['response']['text'] = 'Укажите новую информацию о себе'
            return
        elif 'интересы' in req['request']['nlu']['tokens']:
            sessionStorage[user.application_id]['now_command'][1] = 'interests'
            res['response']['text'] = 'Укажите новые интересы. Учтите, что все предыдущие интересы будут стерты'
            return
        else:
            res['response']['text'] = 'Такого поля не существует, повторите попытку'
            set_editable_fields(user.application_id, res)
            return
    else:
        field_to_edit = sessionStorage[user.application_id]['now_command'][1]
        if field_to_edit == 'name':
            if len(req['request']['original_utterance']) > 50:  # проверка имени
                res['response']['text'] = ERRORS_CREATE_PROFILE[0]
                return
            user.name = req['request']['original_utterance']
            db.session.commit()
            res['response']['text'] = 'Ваше имя успешно изменено. Вы можете продолжить редактировать другие поля, или выйти из режима редактирования'
            sessionStorage[user.application_id]['now_command'][1] = 'none'
            set_editable_fields(user.application_id, res)
            return
        elif field_to_edit == 'age':
            age = search_numbers(req['request']['nlu']['entities'])
            if not age or age <= 0 or age > 999:  # проверка возраста
                res['response']['text'] = ERRORS_CREATE_PROFILE[1]
                return
            user.age = age
            db.session.commit()
            res['response']['text'] = 'Ваш возраст успешно изменен. Вы можете продолжить редактировать другие поля, или выйти из режима редактирования'
            sessionStorage[user.application_id]['now_command'][1] = 'none'
            set_editable_fields(user.application_id, res)
            return
        elif field_to_edit == 'gender':
            if 'мужчина' not in req['request']['nlu']['tokens'] and 'женщина' not in req['request']['nlu']['tokens'] and 'мужской' not in req['request']['nlu'][
                'tokens'] and 'женский' not in req['request']['nlu']['tokens']:  # проверка гендера
                res['response']['text'] = ERRORS_CREATE_PROFILE[2]
                return
            if 'мужчина' in req['request']['nlu']['tokens'] or 'мужской' in req['request']['nlu']['tokens']:
                user.gender = 'male'
            else:
                user.gender = 'female'
            db.session.commit()
            res['response']['text'] = 'Ваш пол успешно изменен. Вы можете продолжить редактировать другие поля, или выйти из режима редактирования'
            sessionStorage[user.application_id]['now_command'][1] = 'none'
            set_editable_fields(user.application_id, res)
            return
        elif field_to_edit == 'networks':
            if len(req['request']['original_utterance']) > 150:
                res['response']['text'] = ERRORS_CREATE_PROFILE[3]
                return
            user.networks = req['request']['original_utterance']
            db.session.commit()
            res['response']['text'] = 'Ваши контакты успешно изменены. Вы можете продолжить редактировать другие поля, или выйти из режима редактирования'
            sessionStorage[user.application_id]['now_command'][1] = 'none'
            set_editable_fields(user.application_id, res)
            return
        elif field_to_edit == 'about_me':
            if len(req['request']['original_utterance']) > 500:
                res['response']['text'] = ERRORS_CREATE_PROFILE[4]
                return
            user.about_me = req['request']['original_utterance']
            db.session.commit()
            res['response']['text'] = 'Ваша информация о себе успешно изменена. Вы можете продолжить редактировать другие поля, или выйти из режима редактирования'
            sessionStorage[user.application_id]['now_command'][1] = 'none'
            set_editable_fields(user.application_id, res)
            return
        elif field_to_edit == 'interests':
            interests = req['request']['original_utterance'].split(',')
            if len(interests) > 20:
                res['response']['text'] = ERRORS_CREATE_PROFILE[5]['interests_count_error']
                return
            user.interests = []
            for interest in interests:
                interest = interest.rstrip().lstrip().lower()
                if len(interest) > 100:
                    db.session.rollback()
                    res['response']['text'] = ERRORS_CREATE_PROFILE[5]['len_interest_text_error']
                    return
                if Interests.query.filter_by(text=interest).first():  # если интерес существует, просто добавляем в него нашего пользователя
                    Interests.query.filter_by(text=interest).first().users.append(user)
                else:  # если нет - создаем интерес и добавляем
                    inter = Interests(text=interest)
                    inter.users.append(user)
                    db.session.add(inter)
            db.session.commit()
            res['response']['text'] = 'Ваши интересы успешно изменены. Вы можете продолжить редактировать другие поля, или выйти из режима редактирования'
            sessionStorage[user.application_id]['now_command'][1] = 'none'
            set_editable_fields(user.application_id, res)
            return


def handle_dialog(req, res):
    application_id = req['session']['application']['application_id']  # свойство user_id перестает поддерживаться
    if not User.query.filter_by(application_id=application_id).first() and application_id not in sessionStorage:  # если пользователь новый
        sessionStorage[application_id]['suggests'] = ['Создай анкету']
        res['response']['text'] = HELLO_MESSAGE
        res['response']['buttons'] = get_suggests(application_id)
        sessionStorage[application_id] = {'now_command': ['start']}
        return
    if User.query.filter_by(application_id=application_id).first() and application_id not in sessionStorage:
        sessionStorage[application_id] = {
            'now_command': ['free_use']
        }
    if sessionStorage[application_id]['now_command'][0] == 'start':
        if ('создай' in req['request']['nlu']['tokens'] or 'создать' in req['request']['nlu']['tokens']) and 'анкету' in req['request']['nlu']['tokens']:
            sessionStorage[application_id]['now_command'] = ['create_profile', 0]
            create_profile(req, res)
            return
        else:
            res['response']['text'] = COMMAND_NOT_ALLOWED
            return

    if sessionStorage[application_id]['now_command'][0] == 'create_profile':  # если пользователь находится на этапе создания анкеты
        create_profile(req, res)
        return
    if sessionStorage[application_id]['now_command'][0] == 'free_use':
        sessionStorage[application_id]['suggests'] = ARRAY_OF_AVAILABLE_COMMANDS

        if SHOW_RECOMMENDATION_PROFILE_COMMAND[0] <= set(req['request']['nlu']['tokens']) or SHOW_RECOMMENDATION_PROFILE_COMMAND[1] <= set(
                req['request']['nlu']['tokens']):  # показать рекомендованную анкету
            get_profile_for_user(application_id, res)
            res['response']['buttons'] = get_suggests(application_id)
            return
        elif SHOW_MY_PROFILE_COMMAND <= set(req['request']['nlu']['tokens']):  # показать анкету пользователя
            res['response']['text'] = str(User.query.filter_by(application_id=application_id).first())
            res['response']['buttons'] = get_suggests(application_id)
            return
        elif EDITING_PROFILE_COMMAND[0] <= set(req['request']['nlu']['tokens']) or EDITING_PROFILE_COMMAND[1] <= set(req['request']['nlu']['tokens']) or EDITING_PROFILE_COMMAND[
            2] <= set(req['request']['nlu']['tokens']) or EDITING_PROFILE_COMMAND[3] <= set(req['request']['nlu']['tokens']):  # заход в ветвь редактирования анкеты
            sessionStorage[application_id]['now_command'] = ['edit_profile', 'none']
            res['response']['text'] = AVAILABLE_FIELDS_FOR_EDITING
            sessionStorage[application_id]['suggests'] = ['Выйти', 'Имя', 'Возраст', 'Пол', 'Контакты', 'Обо мне', 'Интересы']
            res['response']['buttons'] = get_suggests(application_id)
            return
        elif 'помощь' in req['request']['nlu']['tokens'] or HELP_COMMAND <= set(req['request']['nlu']['tokens']):
            res['response']['text'] = AVAILABLE_COMMANDS
            sessionStorage[application_id]['suggests'] = ARRAY_OF_AVAILABLE_COMMANDS
            res['response']['buttons'] = get_suggests(application_id)
            return
        else:
            res['response']['text'] = COMMAND_NOT_ALLOWED
            res['response']['buttons'] = get_suggests(application_id)
            return
    if sessionStorage[application_id]['now_command'][0] == 'edit_profile':
        edit_profile(req, res)
        return
    if 'помощь' in req['request']['nlu']['tokens'] or HELP_COMMAND <= set(req['request']['nlu']['tokens']):
        res['response']['text'] = AVAILABLE_COMMANDS
        sessionStorage[application_id]['suggests'] = ARRAY_OF_AVAILABLE_COMMANDS
        res['response']['buttons'] = get_suggests(application_id)
        return
