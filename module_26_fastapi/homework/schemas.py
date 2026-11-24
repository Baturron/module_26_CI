"""Модели запросов и ответов API на основе Pydantic."""

from pydantic import BaseModel, ConfigDict, Field


class RecipeCreate(BaseModel):
    """Поля, необходимые для создания рецепта."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Название рецепта.",
        examples=["Томатный суп"],
    )
    cooking_time_minutes: int = Field(
        ...,
        gt=0,
        description="Время подготовки и приготовления в целых минутах.",
        examples=[30],
    )
    ingredients: list[str] = Field(
        ...,
        min_length=1,
        description="Ингредиенты в виде непустого списка строк.",
        examples=[["Помидоры", "Лук", "Оливковое масло"]],
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Инструкция по приготовлению.",
        examples=["Нарежьте овощи, потушите до мягкости и измельчите блендером."],
    )


class RecipeSummary(BaseModel):
    """Поля рецепта, возвращаемые в списке популярных рецептов."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Уникальный идентификатор рецепта.")
    title: str = Field(..., description="Название рецепта.")
    views: int = Field(..., description="Число успешных запросов подробной информации.")
    cooking_time_minutes: int = Field(..., description="Время приготовления в минутах.")


class RecipeDetail(BaseModel):
    """Полная информация о рецепте, возвращаемая эндпоинтом деталей."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Уникальный идентификатор рецепта.")
    title: str = Field(..., description="Название рецепта.")
    cooking_time_minutes: int = Field(..., description="Время приготовления в минутах.")
    ingredients: list[str] = Field(
        ..., description="Ингредиенты в порядке отображения."
    )
    description: str = Field(..., description="Инструкция по приготовлению.")
