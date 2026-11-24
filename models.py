"""Модели SQLAlchemy для кулинарной книги."""

from sqlalchemy import JSON, CheckConstraint, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс моделей базы данных приложения."""


class Recipe(Base):
    """Рецепт с ингредиентами, временем приготовления и числом просмотров."""

    __tablename__ = "recipes"
    __table_args__ = (
        CheckConstraint("cooking_time_minutes > 0", name="positive_cooking_time"),
        CheckConstraint("views >= 0", name="nonnegative_views"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    cooking_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    ingredients: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
