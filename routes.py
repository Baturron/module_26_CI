"""Маршруты API кулинарной книги."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas
from .database import get_session


router = APIRouter()


@router.get(
    "/recipes",
    response_model=list[schemas.RecipeSummary],
    summary="Получить список рецептов по популярности",
    description=(
        "Возвращает все рецепты, отсортированные по убыванию числа просмотров, "
        "а при равенстве — по возрастанию времени приготовления. При равных "
        "значениях используется идентификатор рецепта."
    ),
    tags=["Рецепты"],
)
async def list_recipes(
    session: AsyncSession = Depends(get_session),
) -> list[schemas.RecipeSummary]:
    """Вернуть краткую информацию о рецептах, отсортированную по популярности и времени приготовления."""
    result = await session.execute(
        select(models.Recipe).order_by(
            models.Recipe.views.desc(),
            models.Recipe.cooking_time_minutes.asc(),
            models.Recipe.id.asc(),
        )
    )
    return list(result.scalars().all())


@router.get(
    "/recipes/{recipe_id}",
    response_model=schemas.RecipeDetail,
    summary="Получить подробную информацию о рецепте",
    description=(
        "Возвращает название рецепта, время приготовления, ингредиенты и описание. "
        "При каждом успешном запросе счётчик просмотров увеличивается на единицу."
    ),
    responses={404: {"description": "Рецепт с таким идентификатором не найден."}},
    tags=["Рецепты"],
)
async def get_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
) -> schemas.RecipeDetail:
    """Вернуть рецепт и увеличить счётчик его просмотров."""
    recipe = await session.get(models.Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецепт не найден",
        )

    await session.execute(
        update(models.Recipe)
        .where(models.Recipe.id == recipe_id)
        .values(views=models.Recipe.views + 1)
    )
    await session.commit()
    result = await session.execute(
        select(models.Recipe).where(models.Recipe.id == recipe_id)
    )
    return result.scalar_one()


@router.post(
    "/recipes",
    response_model=schemas.RecipeDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Создать рецепт",
    description=(
        "Создаёт рецепт с нулевым числом просмотров. Возвращаемая информация "
        "не увеличивает счётчик; он увеличивается только при GET /recipes/{recipe_id}."
    ),
    responses={422: {"description": "Тело запроса не прошло проверку."}},
    tags=["Рецепты"],
)
async def create_recipe(
    recipe_data: schemas.RecipeCreate,
    session: AsyncSession = Depends(get_session),
) -> schemas.RecipeDetail:
    """Проверить данные и сохранить новый рецепт."""
    recipe = models.Recipe(**recipe_data.model_dump())
    session.add(recipe)
    await session.commit()
    await session.refresh(recipe)
    return recipe
