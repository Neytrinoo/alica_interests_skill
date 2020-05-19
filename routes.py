from flask_app import app
from flask import request
from models import *
from constants import *
from help_functions import search_numbers
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


def create_profile(res, req):
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
        age = search_numbers(req['nlu']['entities'])
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
            sessionStorage[application_id]['create_profile']['age'] = 'female'
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
    elif stage == 6:  # тут необходимо сделать проверку интересов, и это последний пункт, так что на этом этапе будет создаваться запись в бд. ДОДЕЛАТЬ!!!!!
        pass


def handle_dialog(req, res):
    application_id = req['session']['application']['application_id']  # свойство user_id перестает поддерживаться
    if User.query.filter_by(application_id=application_id) and application_id not in sessionStorage:  # если пользователь новый
        res['response']['text'] = HELLO_MESSAGE
        sessionStorage[application_id] = {'now_command': ['start']}
        return
    if sessionStorage[application_id]['now_command'][0] == 'start':
        if ('создай' in req['request']['nlu']['tokens'] or 'создать' in req['request']['nlu']['tokens']) and 'анкету' in req['request']['nlu']['tokens']:
            sessionStorage[application_id]['now_command'] = ['create_profile', 0]
            create_profile(res, req)
            return
    if sessionStorage[application_id]['now_command'][0] == 'create_profile':  # если пользователь находится на этапе создания анкеты
        create_profile(res, req)
        return
