# Homework bot
_Телеграм-бот для проверки статуса домашней работы_

Это учебный проект, написанный в процессе обучения в "Яндекс Практикум".  
Бот проверяет статус сданного на проверку проекта и отправляет сообщения в Телеграм при изменении статуса.
В этом проекте я оттачивал знание языка Python, его встроенных и сторонних библиотек.

### Как использовать?

Клонируйте репозиторий на свой компьютер:
```bash
git clone git@github.com:renegatemaster/homework_bot.git
```

Создайте виртуальное окружение, активируйте его и установите зависимости:
```bash
python3.9 -m venv venv
source venv/bin/activate  # Для Linux и MacOS
source venv/scripts/activate  # Для Windows
pip install -r requirements.txt
```

Создайте файл .env
```bash
touch .env
```
И сохраните в него ваши данные:
```.env
PRACTICUM_TOKEN=XXXXXXXXX  # Токен от Яндекс Практикум
TELEGRAM_TOKEN=XXXXXXXXXX  # Токен вашего бота в Телеграм
TELEGRAM_CHAT_ID=XXXXXXXXX  # ID вашего аккаунта в Телеграм
```

Если у вас ещё нет аккаунта в телеграм и своего бота:
 - [Скачайте](https://desktop.telegram.org/) Telegram и зарегистрируйтесь
 - Узнайте ID вашего аккаунта с помощью [специального бота](https://t.me/userinfobot)
 - В поиске чатов найдите [BotFather](https://t.me/BotFather) и создайте свего бота командой `/newbot`
 - Получите токен бота от BotFather командой `/token`

Запустите программу:
```bash
python3 homework.py
```

Бот будет работать, пока работает устройство, на котором запущена программа.
