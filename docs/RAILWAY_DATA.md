# Данные: локально vs Railway

## Две разные базы

| Где | Где лежат данные |
|-----|------------------|
| **Локально** (`docker compose`) | Postgres в Docker, том `postgres_data` на вашем ПК |
| **Railway** | Отдельный managed Postgres |

Они **не связаны**. Слова из локальной разработки **сами не появятся** на Railway.

Пустой список слов в Mini App на проде — это нормально, если вы ещё не переносили дамп и не добавляли слова через бота на проде.

## База подключена или нет?

Если API и бот **Running**, Postgres-переменные `${{Postgres.*}}` заданы, миграции прошли — БД **подключена**, просто **пустая** (или нет строк для вашего Telegram ID).

Проверка:

1. Отправьте боту на проде английское слово (например `hello`).
2. Откройте Mini App → **WORDS** — слово должно появиться.
3. Если появилось — БД работает, старые локальные данные просто в другой БД.

Если слово **не** сохраняется — смотрите **api** → Deployments → Logs (ошибки Postgres / alembic).

## Почему не видно старых слов

### 1. Другая база (главная причина)

Локальные слова остались в Docker Postgres. Railway — новая пустая БД.

### 2. Другой `tg_user_id`

Слова привязаны к `tg_user_id`. В Telegram — ваш реальный ID. Локально в браузере часто использовался `123456789`.

Даже после переноса дампа слова с `tg_user_id=123456789` не видны под вашим реальным Telegram ID.

## Перенос данных с локального Postgres на Railway

### Экспорт (на ПК, при запущенном `docker compose`)

```bash
docker compose exec db pg_dump -U postgres -d english_vocabulary -F c -f /tmp/backup.dump
docker compose cp db:/tmp/backup.dump ./backup.dump
```

### Импорт в Railway

1. Railway → **Postgres** → **Connect** → скопируйте `DATABASE_URL` или host/port/user/password.
2. Установите [Railway CLI](https://docs.railway.com/guides/cli) или используйте `psql` / pgAdmin с публичным подключением (если включено).
3. Пример через `pg_restore` (подставьте свои данные из Railway):

```bash
pg_restore -h <PGHOST> -p <PGPORT> -U <PGUSER> -d <PGDATABASE> --clean --if-exists backup.dump
```

Пароль запросит из Variables Railway.

**Внимание:** `--clean` перезапишет таблицы на Railway. Сделайте бэкап, если на проде уже есть новые данные.

### Без переноса

Просто пользуйтесь продом с нуля: слова через бота / Mini App — они сохранятся в Railway Postgres.

## Миграции схемы

При деплое **api** в `railway.toml` выполняется `alembic upgrade head` — таблицы создаются. Пустые таблицы ≠ «БД не подключена».
