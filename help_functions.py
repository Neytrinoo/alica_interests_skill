from constants import sessionStorage


def search_numbers(entities):  # проверяет, есть ли в запросе пользователя числовые данные
    for token in entities:
        if token['type'] == 'YANDEX.NUMBER':
            return token['value']
    return False


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]

    sessionStorage[user_id] = session

    return suggests


def set_editable_fields(application_id, res):
    sessionStorage[application_id]['suggests'] = ['Выйти', 'Имя', 'Возраст', 'Пол', 'Контакты', 'Обо мне', 'Интересы']
    res['response']['buttons'] = get_suggests(application_id)
    return
