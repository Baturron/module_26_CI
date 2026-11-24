# Recipe Book API

Асинхронный REST API кулинарной книги на FastAPI и SQLAlchemy 2.x. По умолчанию
данные хранятся в SQLite-файле `recipes.db` рядом с приложением. Адрес базы можно
переопределить переменной окружения `DATABASE_URL`.

## Запуск

Из корня репозитория установите зависимости и запустите сервер:

```bash
python -m pip install -r module_26_fastapi/homework/requirements.txt
uvicorn module_26_fastapi.homework.main:app --reload
```

Автоматическая документация OpenAPI доступна по адресу `http://127.0.0.1:8000/docs`,
альтернативная документация — `http://127.0.0.1:8000/redoc`.
Таблица создаётся автоматически при старте приложения.

## Модель рецепта

| Поле | Тип | Ограничения / значение |
|---|---|---|
| `id` | integer | Уникальный идентификатор, назначается базой данных. |
| `title` | string | Обязательное название длиной от 1 до 200 символов. |
| `cooking_time_minutes` | integer | Обязательное целое число минут, строго больше нуля. |
| `ingredients` | array of strings | Непустой обязательный список; порядок сохраняется. |
| `description` | string | Обязательный непустой текст инструкции. |
| `views` | integer | Счётчик успешных запросов деталей; при создании равен `0`. |

`views` предназначено для выдачи списка и не принимается при создании рецепта.
Просмотр увеличивается только успешным `GET /recipes/{recipe_id}`. Список сам по
себе счётчики не меняет.

## Эндпоинты

### `GET /recipes`

Возвращает массив кратких сведений обо всех рецептах. Сортировка: `views` по
убыванию, `cooking_time_minutes` по возрастанию при равном количестве просмотров,
затем `id` по возрастанию для стабильного порядка.

Успешный ответ `200 OK`:

```json
[
  {
    "id": 4,
    "title": "Tomato soup",
    "views": 12,
    "cooking_time_minutes": 30
  }
]
```

При отсутствии рецептов возвращается пустой массив `[]`.

### `GET /recipes/{recipe_id}`

Возвращает детали рецепта и атомарно увеличивает счётчик просмотров на один.
`recipe_id` — положительный integer, заданный в URL.

Успешный ответ `200 OK`:

```json
{
  "id": 4,
  "title": "Tomato soup",
  "cooking_time_minutes": 30,
  "ingredients": ["Tomatoes", "Onion", "Olive oil"],
  "description": "Simmer the vegetables, then blend until smooth."
}
```

Если рецепт не существует, возвращается `404 Not Found`:

```json
{"detail": "Рецепт не найден"}
```

### `POST /recipes`

Создаёт рецепт. Тело запроса — JSON-объект со всеми полями ниже; `id` и `views`
назначает сервер.

```json
{
  "title": "Tomato soup",
  "cooking_time_minutes": 30,
  "ingredients": ["Tomatoes", "Onion", "Olive oil"],
  "description": "Simmer the vegetables, then blend until smooth."
}
```

Успешный ответ `201 Created` содержит созданный рецепт в формате ответа
`GET /recipes/{recipe_id}`. Некорректный JSON или значения вне ограничений
возвращают `422 Unprocessable Entity` с деталями ошибки FastAPI.

## Тесты

Тесты используют `TestClient` и отдельную временную SQLite-базу для каждого теста:

```bash
pytest -q module_26_fastapi/homework/tests
```
