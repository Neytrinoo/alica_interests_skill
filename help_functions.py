def search_numbers(entities):  # проверяет, есть ли в запросе пользователя числовые данные
    for token in entities:
        if token['type'] == 'YANDEX.NUMBER':
            return token['value']
    return False
