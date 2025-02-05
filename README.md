# Бот-ассистент (RU)

Описание проекта
---
Telegram-бота, который взаимодействует с API сервиса Практикум Домашка, чтобы проверять статус отправленной домашней работы: взята ли она на ревью, проверена ли она, а если проверена — принял ли её ревьюер или вернул на доработку.

Бот должен:
- Каждые 10 минут опрашивать API сервиса Практикум Домашка для проверки статуса отправленной домашней работы.
- При обновлении статуса анализировать ответ API и отправлять соответствующее уведомление в Telegram.
- Логировать свою работу и сообщать о важных проблемах через сообщения в Telegram.

Основные задачи
---
✔️ Настроить опрос API для получения обновлений статуса домашней работы  
✔️ Реализовать функции для обработки статусов домашней работы и отправки уведомлений в Telegram  
✔️ Обеспечить корректную работу логирования и обработки ошибок в работе бота

Стек технологий
---
- Python 3.9
- pyTelegramBotAPI 4.14

Установка проекта из репозитория (Windows)
---
1. Клонировать репозиторий:
```bash
git clone git@github.com:JarexTI/homework_bot.git
```
2. Перейти в папку проекта:
```bash
cd homework_bot
```
3. Создать и активировать виртуальное окружение:
```bash
python -m venv venv

source venv/Scripts/activate
```
4. Установить зависимости из файла `requirements.txt`:
```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```
5. Создать файл .env с переменными окружения, со следующим содержанием:
```
TELEGRAM_TOKEN=<Bot Token>
TELEGRAM_CHAT_ID=<Chat ID>
PRACTICUM_TOKEN=<API Access Token>
```
6. Запустить проект:
```bash
python homework.py
```
<br>

# Assistant Bot (EN)

Project Description
---
A Telegram bot that interacts with the Practicum Homework API to check the status of submitted homework: whether it has been taken for review, reviewed, and if reviewed—whether the reviewer accepted it or returned it for revision.

The bot should:

- Poll the Practicum Homework API every 10 minutes to check the status of submitted homework.
- Upon status updates, analyze the API response and send the corresponding notification to Telegram.
- Log its actions and report any important issues through Telegram messages.

Key Tasks
---
✔️ Set up API polling to receive homework status updates  
✔️ Implement functions to process homework statuses and send notifications to Telegram  
✔️ Ensure proper logging and error handling in the bot's operation

Technology Stack
---
- Python 3.9
- pyTelegramBotAPI 4.14

Project Installation from Repository (Windows)
---
1. Clone the repository:

```bash
git clone git@github.com:JarexTI/homework_bot.git
```

2. Navigate to the project folder:

```bash
cd homework_bot
```

3. Create and activate a virtual environment:

```bash
python -m venv venv

source venv/Scripts/activate
```

4. Install dependencies from the `requirements.txt` file:

```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```

5. Create a `.env` file with the following environment variables:

```
TELEGRAM_TOKEN=<Bot Token>
TELEGRAM_CHAT_ID=<Chat ID>
PRACTICUM_TOKEN=<API Access Token>
```

6. Run the project:

```bash
python homework.py
```
