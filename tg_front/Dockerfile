FROM python:3.13-slim

LABEL maintainer="Kostiantyn Zivenko <kos.zivenko@gmail.com>"

# за замовчення всі операції виконуються з правами рута. Це не добра практика.
# докладніше - тут https://habr.com/ru/post/448480/
# наступні шість рядків необхідні для стоврення користувача, який не є рутом
# докладно про ARG ENV - https://vsupalov.com/docker-arg-env-variable-gui
ARG UID=1000
ARG GID=1000
ENV UID=${UID}
ENV GID=${GID}

RUN wget -qO- https://astral.sh/uv/install.sh | sh

RUN useradd -m -u ${UID} docker_user
# тут ми сворюємо користувача з ім'м docker_user, який не є рутом, і його UID за
# замовченням буде 1000 (раніше тут було ARG UID=1000 ENV UID=${UID}), він може бути
# замінений при старті контейнера передачою змінної або в файлі docker-compose.yaml
# або як аргумент команди docker

USER docker_user

WORKDIR /home/docker_user/tlg

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
