#!/usr/bin/env python3
import argparse
import socket
import subprocess
import sys
import time
import warnings
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


def load_environment(filename: str = ".env.local"):
    """Завантаження змінних середовища з filename файлу."""
    env_path = BASE_DIR / filename
    if env_path.exists():
        load_dotenv(env_path)
    else:
        warnings.warn(f"Попередження: Файл {filename} не знайдено. Використовуються системні змінні середовища.")


def check_docker():
    """Перевірка, чи встановлений і запущений Docker."""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        subprocess.run(["docker", "info"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        warnings.warn("Помилка: Docker не встановлений або не запущений.")
        sys.exit(1)


def run_docker_compose(compose_file: str):
    """Запуск docker-compose з указаним файлом."""
    compose_file = BASE_DIR / compose_file
    if not compose_file.exists():
        warnings.warn(f"Помилка: Файл {compose_file} не знайдено.")
        sys.exit(1)

    print(f"Запуск docker-compose з файлом {compose_file}...")
    try:
        subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "up", "-d"],
            check=True,
            text=True,
            capture_output=True,
        )
        print("Контейнери запущено.")
    except subprocess.CalledProcessError as e:
        warnings.warn(f"Помилка при запуску docker-compose: {e.stderr}")
        sys.exit(1)


def wait_for_db(host: str = "localhost", port: int = 5432):
    """Очікування готовності бази даних через wait_for_db.py."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Очікування готовності бази даних на {host}:{port}...", end="")
    while True:
        print(".", end="", flush=True)
        try:
            s.connect((host, port))
            s.close()
            print(f"\033[92m\nБаза даних готова до роботи.\033[0m")
            break
        except socket.error as ex:
            time.sleep(1)


def run_django_commands(
        manage_py: str = "bot_backend/manage.py",  # Шлях до manage.py
        text_commands: dict[str, str] | None = None,  # Список команд для виконання: key - команда, value - опис
        description: list[str] | None = None,  # Опис команд для відображення в консолі, необовʼязково
):
    """Виконання Django-команд: makemigrations, migrate, runserver."""
    manage_py = BASE_DIR / manage_py
    if not manage_py.exists():
        print(f"Помилка: Файл {manage_py} не знайдено. Переконайтеся, що ви в корені Django-проєкту.")
        sys.exit(1)

    command_begin = (sys.executable, str(manage_py))
    commands: dict[tuple, str] = {}
    if text_commands is None:
        commands = {
            command_begin + ("makemigrations",): "Створення міграцій",
            command_begin + ("migrate",): "Застосування міграцій",
            command_begin + ("runserver", "localhost:8000",): "Запуск сервера: localhost:8000",
        }
    else:
        for cmd in text_commands:
            commands[command_begin + tuple(cmd.split())] = text_commands[cmd]


    last_command = None
    for cmd, desc in commands.items():
        if "runserver" in " ".join(cmd):
            last_command = cmd
            continue
        try:
            print(f"\nВиконання команди: {desc}...")
            subprocess.run(cmd, check=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Помилка при виконанні {desc}: {e.stderr}")
            sys.exit(1)
    if last_command:
        print(f"\nВиконання команди: {commands[last_command]}...")
        try:
            process = subprocess.Popen(last_command, text=True, stdout=sys.stdout, stderr=sys.stderr)
            time.sleep(1)
            if process.poll() is not None:
                print(f"Помилка: Django-сервер не запустився (код завершення: {process.returncode}).")
                sys.exit(1)
            print(f"Команду {commands[last_command]} запущено у фоновому режимі.")
        except Exception as e:
            print(f"Помилка при виконанні {last_command}: {e.stderr}")
            sys.exit(1)


def local_start():
    """Головна функція скрипта."""
    # Налаштування аргументів командного рядка
    parser = argparse.ArgumentParser(description="Запуск Docker і Django-застосунку")
    parser.add_argument(
        "--compose-file",
        type=str,
        default="docker-compose.local.yaml",
        help="Шлях до docker-compose файлу (за замовчуванням: docker-compose.local.yaml)"
    )
    parser.add_argument(
        "--env-file",
        type=str,
        default=".env.local",
        help="Шлях до файлу змінних середовища (за замовчуванням: .env.local)"
    )
    args = parser.parse_args()

    # Налаштування кодування консолі
    if sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    # Завантаження змінних середовища
    load_environment()

    # Перевірка Docker
    check_docker()

    # Запуск docker-compose
    run_docker_compose(args.compose_file)

    # Очікування бази даних
    wait_for_db()

    # Виконання Django-команд
    run_django_commands()

