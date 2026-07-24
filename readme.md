# Руководство по размещению Telegram-бота на Ubuntu VPS

## 1. Подключение к серверу

```bash
ssh root@IP_СЕРВЕРА
```

Обновите систему:

```bash
apt update && apt upgrade -y
```

## 2. Установка Python, Node.js и FFmpeg

```bash
apt install -y python3 python3-pip python3-venv git nodejs npm ffmpeg
```

Проверка:

```bash
python3 --version
pip3 --version
node -v
npm -v
ffmpeg -version
```

## 3. Загрузка проекта

Клонируйте репозиторий:

```bash
git clone <URL_репозитория>
cd ytdltl
```

## 4. Создание виртуального окружения

```bash
cd ytdltl
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 5. Настройка переменных окружения

В корне проекта создайте файл `.env`:

```env
BOT_TOKEN=123456:ABCDEF
PUBLIC_DOWNLOAD_BASE_URL=https://example.com/downloads
DOWNLOAD_SERVER_PORT=8000
```

Что это значит:

- `BOT_TOKEN` — токен Telegram-бота;
- `PUBLIC_DOWNLOAD_BASE_URL` — публичный URL, по которому будет доступен сервер загрузок;
- `DOWNLOAD_SERVER_PORT` — порт для локального сервера скачивания.

Важно:

- файл `.env` должен лежать рядом с `bot.py` и `config.py`;
- если вы запускаете проект через `systemd`, то `WorkingDirectory` должен указывать на каталог с `.env`.

## 6. Проверка запуска

```bash
python bot.py
```

Если бот запускается — остановите его комбинацией `Ctrl+C`.

## 7. Создание systemd-сервиса

```bash
nano /etc/systemd/system/ytdltl_bot.service
```

```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/ytdltl
EnvironmentFile=/root/ytdltl/.env
ExecStart=/root/ytdltl/venv/bin/python /root/ytdltl/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Если проект расположен в другом каталоге — замените пути.

## 8. Запуск

```bash
systemctl daemon-reload
systemctl enable ytdltl_bot
systemctl start ytdltl_bot
```

Проверка:

```bash
systemctl status ytdltl_bot
```

## 9. Просмотр логов

```bash
journalctl -u ytdltl_bot -f
```

Последние 100 строк:

```bash
journalctl -u ytdltl_bot -n 100
```

## 10. Обновление проекта

```bash
cd /root/ytdltl
git pull
systemctl restart ytdltl_bot
```

## 11. Полезные команды

Перезапуск:

```bash
systemctl restart ytdltl_bot
```

Остановка:

```bash
systemctl stop ytdltl_bot
```

Автозапуск:

```bash
systemctl enable ytdltl_bot
```

Отключить автозапуск:

```bash
systemctl disable ytdltl_bot
```

## 12. Рекомендуемая структура

```
/root/
└── ytdltl/
    ├── bot.py
    ├── requirements.txt
    ├── .env
    ├── venv/
    └── ...
```

## 13. Polling или Webhook

Для большинства ботов достаточно Polling:

- не нужен домен;
- не нужен HTTPS;
- простая настройка.

Webhook стоит использовать при высокой нагрузке или интеграции с веб-приложением.

## 14. Итог

Оптимальная схема:

- Ubuntu Server;
- Python + venv;
- Git;
- systemd;
- journalctl;
- polling;
- `.env` для токенов и публичных URL.
