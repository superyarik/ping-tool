# IP-монитор

Скрипт для мониторинга доступности IP-адреса с автоматическим уведомлением через PushAll API.

## Описание

IP-монитор - это простой, но эффективный инструмент для контроля доступности сетевых устройств. Скрипт регулярно пингует заданный IP-адрес и отправляет уведомления через сервис PushAll в случае обнаружения проблем с подключением.

### Основные возможности

- Регулярный мониторинг IP-адреса с помощью ping
- Подтверждение недоступности после нескольких последовательных неудачных попыток
- Отправка уведомлений через PushAll API с ограничением частоты
- Поддержка Windows и Linux/Unix систем
- Подробное логирование всех событий

## Установка

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/username/ip-monitor.git
   cd ip-monitor
   ```

2. Установите необходимые зависимости:
   ```
   pip install requests
   ```
   
   Опционально (для работы с .env файлами):
   ```
   pip install python-dotenv
   ```
   
3. **Подготовьте API ключи PushAll**:
   - Зарегистрируйтесь на сайте [PushAll](https://pushall.ru/)
   - Получите ваши ID и KEY из личного кабинета
   - Укажите их в конфигурации (см. раздел "Настройка" ниже)

## Важно: API ключи PushAll

Для работы скрипта **ОБЯЗАТЕЛЬНО** требуются `PUSHALL_ID` и `PUSHALL_KEY` от сервиса PushAll. 
Без этих параметров скрипт запустится, но не сможет отправлять уведомления и завершит работу.

Вы должны указать эти параметры одним из следующих способов:

## Настройка

### Метод 1: Использование переменных окружения

Запустите скрипт с необходимыми переменными окружения:

```
PUSHALL_ID=ваш_id PUSHALL_KEY=ваш_ключ python ip_monitor.py
```

Дополнительные параметры (опционально):
```
PUSHALL_ID=ваш_id PUSHALL_KEY=ваш_ключ IP_ADDRESS=192.168.1.100 PING_INTERVAL=30 python ip_monitor.py
```

### Метод 2: Использование файла .env (требуется python-dotenv)

1. Создайте файл `.env` на основе `.env.example`:
   ```
   cp .env.example .env
   ```

2. Отредактируйте `.env` файл и добавьте ваши API ключи PushAll:
   ```
   PUSHALL_ID=ваш_id
   PUSHALL_KEY=ваш_ключ
   ```

3. При необходимости, измените дополнительные параметры в файле `.env`:
   ```
   IP_ADDRESS=192.168.1.1
   PING_INTERVAL=60
   CONSECUTIVE_FAILURES_THRESHOLD=3
   NOTIFICATION_COOLDOWN=300
   ```

### Метод 3: Редактирование исходного кода

Вы также можете изменить основные параметры непосредственно в скрипте:
```python
# Конфигурация
IP_ADDRESS = os.environ.get("IP_ADDRESS", "192.168.1.1")  # Измените значение по умолчанию здесь
PING_INTERVAL = int(os.environ.get("PING_INTERVAL", "60"))
CONSECUTIVE_FAILURES_THRESHOLD = int(os.environ.get("CONSECUTIVE_FAILURES_THRESHOLD", "3"))
NOTIFICATION_COOLDOWN = int(os.environ.get("NOTIFICATION_COOLDOWN", "300"))
```

## Использование

Запустите скрипт, предварительно настроив API ключи одним из методов, описанных выше:

```
python ip_monitor.py
```

Если вы не настроили API ключи через .env или переменные окружения, скрипт выдаст сообщение об ошибке:
```
ERROR - Не указаны ID или KEY для PushAll API. Установите переменные окружения PUSHALL_ID и PUSHALL_KEY
ERROR - Пример запуска: PUSHALL_ID=your_id PUSHALL_KEY=your_key python ip_monitor.py
```

Скрипт будет работать в фоновом режиме, проверяя доступность указанного IP-адреса и отправляя уведомления при необходимости.

### Запуск в фоновом режиме (Linux)

Для запуска скрипта в фоновом режиме в Linux можно использовать nohup:

```
nohup python ip_monitor.py > ip_monitor_output.log 2>&1 &
```

### Автозапуск при загрузке системы

#### Linux (systemd)

1. Создайте файл службы:
   ```
   sudo nano /etc/systemd/system/ip-monitor.service
   ```

2. Добавьте следующее содержимое (изменив пути на соответствующие):
   ```
   [Unit]
   Description=IP Monitor Service
   After=network.target

   [Service]
   User=your_username
   WorkingDirectory=/path/to/ip-monitor
   ExecStart=/usr/bin/python /path/to/ip-monitor/ip_monitor.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. Включите и запустите службу:
   ```
   sudo systemctl enable ip-monitor.service
   sudo systemctl start ip-monitor.service
   ```

#### Windows

1. Создайте файл с расширением .bat с содержимым:
   ```
   @echo off
   python C:\path\to\ip_monitor.py
   ```

2. Добавьте этот файл в автозагрузку или создайте задачу в Планировщике заданий.

## Логирование

Информация о работе скрипта записывается в файл `ip_monitor.log` в директории скрипта. Лог также выводится в консоль.

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности смотрите в файле LICENSE.

## Вклад в проект

Буду рад любым предложениям по улучшению проекта! Создавайте issues или pull requests.
