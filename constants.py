sessionStorage = {}
HELLO_MESSAGE = 'Привет! Этот навык поможет вам найти человека по вашим интересам для знакомства с ним. Если вкратце: любой желающий добавляет сюда свою анкету и после этого может просматривать анкеты других пользователей. Для того, чтобы начать, вам нужно создать свою анкету. Для этого скажите: «Создай анкету».'  # сообщение, которое выводится новому пользователю

CREATE_PROFILE = {
    0: 'Укажите свое имя. Оно будет показываться другим пользователям',
    1: 'Сколько вам полных лет?\nP.S.Принимая во внимание биологические особенности человека, я не смогу создать человека с возрастом большим, чем 999 годиков',
    2: 'Вы мужчина или женщина?',
    3: 'Как только ваша анкета попадется какому-нибудь человеку, есть вероятность, что он захочет с вами связаться.\n'
       'Дайте ссылку на свою страницу Вконтакте, или на Одноклассники, или telegram, или на все сразу.',
    4: 'Сейчас я прошу вас вкратце расписать кто вы и зачем вы здесь. Можете написать что-то о себе, о том, какого человека вы бы хотели найти.'
       'Эту информацию увидят люди, которым попадется ваша анкета, и во многом исходя из нее они решат для себя, подходите ли вы им или нет. Только кратко, '
       'количество символов ограничено 500',
    5: 'Анкеты рекомендуются пользователям исходя из их интересов. Если Вася начнет поиск анкеты, а у Пети будут совпадать с ним интересы, то есть вероятность, '
       'что анкета Пети порекомендуется Васе. Вам нужно указать свои интересы, через запятую, не используя лишних знаков препинания. '
       'Максимум вы можете указать 20 интересов, поэтому подумайте, что именно вы сейчас напишете'
}

ERRORS_CREATE_PROFILE = {
    0: 'Ваше имя слишком длинное(\nМаксимальная длина 50 символов, повторите попытку',
    1: 'Указанный вами возраст некорректен. Пожалуйста, повторите попытку',
    2: 'Указанного гендера не существует. Вы мужчина или женщина?',
    3: 'Максимальная длина ваших соцсетей не должна превышать 150 символов. Повторите попытку',
    4: 'Вы превысили лимит в 500 символов. Повторите попытку',
    5: {'interests_count_error': 'Вы указали больше 20 интересов. Подумайте, какие из них вам не так важны, и повторите попытку, исключив их',
        'len_interest_text_error': 'Длина одного из ваших интересов больше 100 символов, это недопустимо. Пожалуйста, повторите попытку'}
}
AFTER_CREATED_PROFILE = 'Поздравляю! Теперь у вас есть анкета. Теперь вы можете попросить меня показать вам анкету какого-нибудь человека, с которым у вас совпадают интересы, ' \
                        'просто сказав "покажи анкету". Если таких пользователей пока нет, я покажу вам случайную анкету. ' \
                        'Вам также доступна команды "редактировать анкету" и "как выглядит моя анкета"'

NOT_USER_TO_RECOMMENDATION = 'К сожалению в данный момент не осталось анкет, которые вы не видели. Как только появятся новые пользователи, это изменится'
SHOW_RECOMMENDATION_PROFILE_COMMAND = [{'покажи', 'анкету'}, {'показать', 'анкету'}]
SHOW_MY_PROFILE_COMMAND = {'как', 'выглядит', 'моя', 'анкета'}
EDITING_PROFILE_COMMAND = [{'редактировать', 'анкету'}, {'отредактировать', 'анкету'}, {'отредактируй', 'анкету'}, {'редактируй', 'анкету'}]
AVAILABLE_COMMANDS = 'Доступные команды:\n"Показать анкету"\n"Как выглядит моя анкета"\n"Редактировать анкету"'
AVAILABLE_FIELDS_FOR_EDITING = 'Вы можете отредактировать все поля вашей анкеты. Для этого просто скажите, что вы хотите отредактировать:\n' \
                               '"Имя"\n' \
                               '"Возраст"\n' \
                               '"Пол"\n' \
                               '"Контакты"\n' \
                               '"Обо мне"\n' \
                               '"Интересы"\n' \
                               'Чтобы выйти из режима редактирование, скажите: "выйти"'
COMMAND_NOT_ALLOWED = 'Я не поняла, что вы хотите.\n' + AVAILABLE_COMMANDS
ARRAY_OF_AVAILABLE_COMMANDS = ['Показать анкету', 'Как выглядит моя анкета', 'Редактировать анкету', 'Помощь']
HELP_COMMAND = {'что', 'ты', 'умеешь'}
