from flask_app import app
from flask import request
from constants import *
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


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    if req['session']['new']:  # если пользователь новый
        sessionStorage[user_id] = {}
        res['response']['text'] = HELLO_MESSAGE
        return
    else:
        res['response']['text'] = HELLO_MESSAGE
