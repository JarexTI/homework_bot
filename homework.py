import logging
import time
from http import HTTPStatus
from os import getenv
from sys import stdout

import requests
from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import (ClientErorr, ContentError, EmptyToken,
                        ServerError, StatusError)

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


def check_tokens() -> list[str]:
    """Проверяет наличие токенов и чат-id."""
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    empty_variables = [key for key, value in tokens.items() if value is None]
    return empty_variables


def send_message(bot: TeleBot, message: str) -> None:
    """Отправляет сообщение пользователю."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Собщение отправлено!')
    except Exception:
        logger.error('Собщение не отправлено! Не сработал метод send_message.')


def get_api_answer(timestamp: int):
    """Проверяет ответ API на: статус-код и формат json."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(url=ENDPOINT,
                                headers=HEADERS,
                                params=payload,
                                timeout=3)
    except requests.exceptions.ConnectTimeout as error:
        logger.warning('Время ожидания ответа превышено: %s', error)
    except requests.RequestException as error:
        logger.warning('Ошибка запроса: %s', error)

    response_code = response.status_code
    if response_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        raise ServerError(f'На сервере произошла ошибка. Код: {response_code}')
    elif response_code == HTTPStatus.UNAUTHORIZED:
        raise ClientErorr(f'Клиент неаутентифицированн. Код: {response_code}')
    elif response_code == HTTPStatus.NO_CONTENT:
        raise ContentError(f'Контент отсутствует. Код: {response_code}')

    try:
        response = response.json()
    except ValueError as error:
        logger.error('API ответ не в JSON формате: %s', error)
    return response


def check_response(response):
    """Находит и возвращает последнюю домашнюю работу."""
    if not isinstance(response, dict):
        raise TypeError(f'получен {type(response)} вместо ожидаемого словаря')

    if 'homeworks' not in response:
        raise KeyError('Отсутствует ключ homeworks.')
    elif 'current_date' not in response:
        raise KeyError('Отсутствует ключ current_date.')

    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError(
            ('В ответе API домашки под ключом `homeworks` '
             'данные приходят не в виде списка')
        )

    if not homeworks:
        logger.debug('Пришел пустой список домашних работ.')

    homework = homeworks[0]

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
    empty_tokens = check_tokens()
    if empty_tokens:
        error_message = (
            'Отсутствуют обязательные переменные окружения: %s', empty_tokens
        )
        logger.critical(error_message)
        raise EmptyToken(error_message)

    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    last_message = None

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            message: str = parse_status(homework)
            if last_message != message:
                send_message(bot, message)
                last_message = message
            else:
                logger.debug('В последней домашней работе статус не изменися.')
        except Exception as error:
            logger.error('Сбой в работе программы: %s', error)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
