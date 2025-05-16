local:
- bot_backend starts in host, port 8000. works with db: localhost:5432
- tlg_front starts in container, ports 8000:8000. works with bot_backend: localhost:8000
- db starts in container, ports 5432:5432

how to run:
```bash
>>> python -m startup_script.local_start
```

all settings in DEBUG mode
.env.local
docker-compose.local.yml

dev:
...

all settings in DEBUG mode
.env.dev
docker-compose.dev.yml

prod:
- bot_backend starts in container (service backend), ports 80:8000. Works with db: db:5432
- tlg_front starts in container (service frontend), Works with bot_backend: backend:8000
- db starts in container (service db).
- nginx starts in container (service nginx), ports 80:80. Works with bot_backend: backend:8000

all settings in PRODUCTION mode
.env.prod
docker-compose.prod.yml
