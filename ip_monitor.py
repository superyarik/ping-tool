#!/usr/bin/env python3
import subprocess
import time
import requests
import datetime
import platform
import logging
import os
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ip_monitor.log"),
        logging.StreamHandler()
    ]
)

# Попытка импорта python-dotenv (но не обязательно)
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.info("Файл .env успешно загружен")
except ImportError:
    logging.warning("Модуль python-dotenv не установлен. Переменные среды будут взяты из системы.")
    logging.warning("Для установки модуля выполните: pip install python-dotenv")

# Конфигурация
IP_ADDRESS = os.environ.get("IP_ADDRESS", "192.168.1.1")  # Измените на IP, который хотите мониторить
PING_INTERVAL = int(os.environ.get("PING_INTERVAL", "60"))  # Проверка каждую минуту (в секундах)
CONSECUTIVE_FAILURES_THRESHOLD = int(os.environ.get("CONSECUTIVE_FAILURES_THRESHOLD", "3"))  # Количество последовательных сбоев для подтверждения недоступности
NOTIFICATION_COOLDOWN = int(os.environ.get("NOTIFICATION_COOLDOWN", "300"))  # Отправка уведомлений максимум раз в 5 минут (в секундах)

# Параметры API PushAll
PUSHALL_URL = "https://pushall.ru/api.php"
PUSHALL_ID = os.environ.get("PUSHALL_ID", "")  # ID из PushAll (обязательный параметр)
PUSHALL_KEY = os.environ.get("PUSHALL_KEY", "")  # Ключ из PushAll (обязательный параметр)
PUSHALL_PARAMS = {
    "type": "self",
    "id": PUSHALL_ID,
    "key": PUSHALL_KEY,
    "text": "НЕДОСТУПНОСТЬ"
}

def ping(host):
    """
    Возвращает True, если хост отвечает на ping-запрос, иначе False.
    Адаптирует команду ping в зависимости от операционной системы.
    """
    # Проверка операционной системы
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Формирование команды
    command = ['ping', param, '1', host]

    # Выполнение команды ping
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def send_notification():
    """
    Отправляет уведомление через API PushAll.
    Возвращает True в случае успеха, иначе False.
    """
    try:
        response = requests.post(PUSHALL_URL, data=PUSHALL_PARAMS)
        if response.status_code == 200:
            logging.info(f"Уведомление успешно отправлено. Ответ: {response.text}")
            return True
        else:
            logging.error(f"Не удалось отправить уведомление. Код статуса: {response.status_code}, Ответ: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Ошибка при отправке уведомления: {e}")
        return False

def main():
    # Проверка наличия API ключей
    if not PUSHALL_ID or not PUSHALL_KEY:
        logging.error("Не указаны ID или KEY для PushAll API. Установите переменные окружения PUSHALL_ID и PUSHALL_KEY")
        logging.error("Пример запуска: PUSHALL_ID=your_id PUSHALL_KEY=your_key python ip_monitor.py")
        return

    consecutive_failures = 0
    last_notification_time = None
    
    logging.info(f"Запуск мониторинга IP {IP_ADDRESS}")
    logging.info(f"Интервал пинга: {PING_INTERVAL} секунд")
    logging.info(f"Порог уведомления: {CONSECUTIVE_FAILURES_THRESHOLD} последовательных сбоев")
    logging.info(f"Период ожидания между уведомлениями: {NOTIFICATION_COOLDOWN} секунд")
    
    while True:
        current_time = datetime.datetime.now()
        is_reachable = ping(IP_ADDRESS)
        
        if is_reachable:
            if consecutive_failures > 0:
                logging.info(f"IP {IP_ADDRESS} снова доступен после {consecutive_failures} последовательных сбоев")
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            logging.warning(f"IP {IP_ADDRESS} недоступен. Последовательных сбоев: {consecutive_failures}")
            
            # Проверка, нужно ли отправлять уведомление
            if consecutive_failures >= CONSECUTIVE_FAILURES_THRESHOLD:
                # Проверка, можно ли отправить уведомление (с учетом периода ожидания)
                if last_notification_time is None or (current_time - last_notification_time).total_seconds() >= NOTIFICATION_COOLDOWN:
                    logging.warning(f"IP {IP_ADDRESS} подтверждена недоступность ({consecutive_failures} последовательных сбоев). Отправка уведомления...")
                    if send_notification():
                        last_notification_time = current_time
                else:
                    time_since_last = (current_time - last_notification_time).total_seconds()
                    logging.info(f"Период ожидания активен. Последнее уведомление было {time_since_last:.1f} секунд назад")
        
        # Ожидание до следующей проверки
        time.sleep(PING_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Мониторинг остановлен пользователем")
    except Exception as e:
        logging.error(f"Непредвиденная ошибка: {e}")
