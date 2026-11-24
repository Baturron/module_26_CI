"""Тесты API с отдельной базой SQLite для каждого теста."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from module_26_fastapi.homework.main import create_app


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    """Создать тестовый клиент с временной базой данных."""
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'recipes.db'}"
    with TestClient(create_app(database_url)) as test_client:
        yield test_client


def create_recipe(client: TestClient, **overrides: object) -> dict[str, object]:
    """Создать рецепт с корректными значениями по умолчанию и вернуть JSON-ответ."""
    payload = {
        "title": "Tomato soup",
        "cooking_time_minutes": 30,
        "ingredients": ["Tomatoes", "Onion"],
        "description": "Simmer the vegetables and blend until smooth.",
    }
    payload.update(overrides)
    response = client.post("/recipes", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_recipe_returns_details_with_zero_views(client: TestClient) -> None:
    """Новый рецепт сохраняется с нулевым числом просмотров деталей."""
    recipe = create_recipe(client)

    assert recipe == {
        "id": 1,
        "title": "Tomato soup",
        "cooking_time_minutes": 30,
        "ingredients": ["Tomatoes", "Onion"],
        "description": "Simmer the vegetables and blend until smooth.",
    }
    assert client.get("/recipes").json() == [
        {
            "id": 1,
            "title": "Tomato soup",
            "views": 0,
            "cooking_time_minutes": 30,
        }
    ]


def test_recipe_list_orders_by_views_then_cooking_time(client: TestClient) -> None:
    """Сначала учитывается популярность, затем при равенстве — время приготовления."""
    quick = create_recipe(
        client,
        title="Quick recipe",
        cooking_time_minutes=10,
    )
    slow = create_recipe(
        client,
        title="Slow recipe",
        cooking_time_minutes=50,
    )
    popular = create_recipe(
        client,
        title="Popular recipe",
        cooking_time_minutes=40,
    )

    client.get(f"/recipes/{popular['id']}")
    client.get(f"/recipes/{popular['id']}")

    response = client.get("/recipes")

    assert response.status_code == 200
    assert [recipe["id"] for recipe in response.json()] == [
        popular["id"],
        quick["id"],
        slow["id"],
    ]


def test_get_recipe_returns_details_and_increments_views(client: TestClient) -> None:
    """Каждый успешный запрос деталей увеличивает счётчик в списке рецептов."""
    recipe = create_recipe(client)

    response = client.get(f"/recipes/{recipe['id']}")

    assert response.status_code == 200
    assert response.json() == recipe
    assert client.get("/recipes").json()[0]["views"] == 1


def test_get_unknown_recipe_returns_404(client: TestClient) -> None:
    """Для неизвестного идентификатора возвращается ответ об отсутствии рецепта."""
    response = client.get("/recipes/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Рецепт не найден"}


def test_create_recipe_rejects_nonpositive_cooking_time(client: TestClient) -> None:
    """Время приготовления должно быть положительным числом минут."""
    response = client.post(
        "/recipes",
        json={
            "title": "Invalid recipe",
            "cooking_time_minutes": 0,
            "ingredients": ["Water"],
            "description": "Do nothing.",
        },
    )

    assert response.status_code == 422
