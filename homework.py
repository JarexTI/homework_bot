import logging
import time
from http import HTTPStatus
from os import getenv
from sys import stdout

import requests
from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import ClientErorr, ContentError, ServerError, StatusError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stream=stdout)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv()

PRACTICUM_TOKEN = getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens() -> bool:
    """Проверяет наличие токенов и чат-id."""
    if (PRACTICUM_TOKEN is None
            or TELEGRAM_TOKEN is None
            or TELEGRAM_CHAT_ID is None):
        return True
    return False


def send_message(bot: TeleBot, message: str) -> None:
    """Отправляет сообщение пользователю."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Собщение отправлено!')
    except Exception:
        logger.error('Собщение не отправлено!')


def get_api_answer(timestamp: int):
    """Проверяет ответ API на: статус-код и формат json."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(url=ENDPOINT,
                                headers=HEADERS,
                                params=payload,
                                timeout=3)
    except requests.exceptions.ConnectTimeout as error:
        logger.warning(f'Время ожидания ответа превышено: {error}')
    except requests.RequestException as error:
        logger.warning(f'Ошибка запроса: {error}')

    response_code = response.status_code
    if response_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        raise ServerError(f'На сервере произошла ошибка. Код: {response_code}')
    elif response_code == HTTPStatus.UNAUTHORIZED:
        raise ClientErorr(f'Клиент неаутентифицированн. Код: {response_code}')
    elif response_code == HTTPStatus.NO_CONTENT:
        raise ContentError(f'Контент отсутствует. Код: {response_code}')
    else:
        try:
            response = response.json()
        except ValueError as error:
            logger.error(f'API ответ не в JSON формате: {error}')
        return response


def check_response(response):
    """Находит и возвращает последнюю домашнюю работу."""
    if not isinstance(response, dict):
        raise TypeError(f'получен {type(response)} вместо ожидаемого словаря')

    if 'homeworks' not in response:
        raise KeyError('Отсутствует homeworks')

    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError(
            ('В ответе API домашки под ключом `homeworks` '
             'данные приходят не в виде списка')
        )

    if not homeworks:
        logger.debug('Пришел пустой список домашних работ.')

    max_id = max([item.get('id') for item in homeworks])
    homework = list(filter(lambda x: x.get('id') == max_id, homeworks))[0]

    return homework


def parse_status(homework) -> str:
    """Достает название и текущий статус последней домашней работы.
    Возвращает сроку для сообщения.
    """
    if 'homework_name' not in homework:
        raise KeyError('в ответе API домашки нет ключа "homework_name"')

    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise StatusError('Пришел недокументированный статус домашней работы.')

    homework_name = homework.get('homework_name')
    verdict = HOMEWORK_VERDICTS.get(status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """Основная логика работы бота."""
    if check_tokens():
        logger.critical('Отсутствуют обязательные переменные окружения.')
        return

    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
