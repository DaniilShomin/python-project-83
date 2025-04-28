#!/usr/bin/env bash
# скачиваем uv и запускаем команду установки зависимостей
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
make install && psql -a -d $DATABASE_URL -f database.sql

psql -h dpg-d078e9idbo4c73amo16g-a.oregon-postgres.render.com -U mydb_4uqa_user mydb_4uqa