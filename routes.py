from flask_app import app
from flask import request
from models import *
from constants import *
from help_functions import search_numbers
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
        sessionStorage[application_id]['create_profile'] = {}
        return


def handle_dialog(req, res):
    application_id = req['session']['application']['application_id']  # свойство user_id перестает поддерживаться
    if not User.query.filter_by(application_id=application_id).first() and application_id not in sessionStorage:  # если пользователь новый
        res['response']['text'] = HELLO_MESSAGE
        sessionStorage[application_id] = {'now_command': ['start']}
        return
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
