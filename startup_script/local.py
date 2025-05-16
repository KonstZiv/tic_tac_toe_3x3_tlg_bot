import argparse
import sys

from startup_script.utils import load_environment, check_docker, run_docker_compose, wait_for_db, run_django_commands

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


if __name__ == "__main__":
    local_start()
