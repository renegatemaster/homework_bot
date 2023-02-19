import logging
from logging import StreamHandler
import sys
import os
import time
import requests
from http import HTTPStatus
import telegram
from dotenv import load_dotenv
from exceptions import NoStatusException, NoNameException, UnknownStatusError

load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Checks for variables in environment."""
    tokens = [
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ]
    if all(tokens):
        logger.info('В окружении все необходимые переменные.')
        return True
    else:
        logger.critical('Отсутствие обязательных переменных окружения')
        return False


def send_message(bot, message):
    """Sends messages to Telegram chat."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Удачная отправка сообщения')
    except Exception as error:
        logger.error(f'Cбой при отправке сообщения в Telegram {error}.')


def get_api_answer(timestamp):
    """Makes request to API. Returns answer in Python data type."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload
        )
    except Exception as error:
        logger.error(f'Сбой при запросе к эндпоинту. {error}')
        raise ConnectionError('Нет ответа от API.')
    else:
        if response.status_code == HTTPStatus.OK:
            logger.debug('Эндпоинт доступен')
            response = response.json()
            return response
        else:
            logger.error('Эндпоинт недоступен.')
            raise ConnectionError('Не удалось подключиься к сервису.')


def check_response(response):
    """Checks API answer."""
    if not isinstance(response, dict):
        logger.info('Cтруктура данных API не соответствует ожиданиям')
        raise TypeError('Cтруктура данных API не соответствует ожиданиям')
    if 'homeworks' not in response:
        logger.error('Отсутствие ожидаемых ключей в ответе API.')
        raise KeyError('Ответ API не содержит ключей.')
    else:
        logger.info('Ответ API соответствует документации.')
    if not isinstance(response['homeworks'], list):
        logger.info('Под ключом `homeworks` данные приходят не в виде списка.')
        raise TypeError('Данные приходят не в виде списка.')


def parse_status(homework):
    """Extracts informations about particular homework status."""
    if 'status' not in homework:
        logger.error(f'Домашняя работа {homework} не содержит статус.')
        raise NoStatusException('Домашняя работа не содержит статус.')
    if 'homework_name' not in homework:
        logger.error(f'Домашняя работа {homework} не содержит названия.')
        raise NoNameException('Домашняя работа не содержит названия.')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        logger.error('Неожиданный статус домашней работы')
        raise UnknownStatusError('Недокументированный статус домашней работы.')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    previous_homeworks = {}
    previous_message = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            timestamp = response['current_date']
            homeworks = response['homeworks']
            if len(homeworks) > 0:
                if homeworks != previous_homeworks:
                    status = parse_status(homeworks[0])
                    send_message(bot, status)
                    previous_homeworks = homeworks
            else:
                logger.debug('Нет обновлений.')
        except Exception as error:
            logger.error(error)
            message = f'Сбой в работе программы: {error}'
            if message != previous_message:
                send_message(bot, message)
                previous_message = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Работа программы остановлена.')
