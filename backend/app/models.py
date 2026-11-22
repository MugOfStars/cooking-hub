from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Recipe(Base):
    __tablename__ = "recipes"
    __table_args__ = (
        # Text + CHECK rather than a Postgres ENUM: equally strict, but adding a new
        # source type later is a one-line migration instead of an ALTER TYPE dance.
        CheckConstraint("source_type IN ('url', 'book', 'manual')", name="source_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    source_type: Mapped[str] = mapped_column(String(10))
    source_url: Mapped[str | None] = mapped_column(Text)
    book_title: Mapped[str | None] = mapped_column(String(200))
    book_page: Mapped[int | None]
    # Stored as a list of objects, e.g. [{"raw": "2 cups flour"}], so parsed fields
    # (name, quantity, unit) can be added later for pantry matching without a migration.
    ingredients: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, server_default=text("'[]'::jsonb")
    )
    instructions: Mapped[list[str]] = mapped_column(JSONB, server_default=text("'[]'::jsonb"))
    image_url: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default=text("'{}'"))
    # The database sets this, so it's correct no matter which client inserts the row.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cook_logs: Mapped[list[CookLog]] = relationship(back_populates="recipe")


class CookLog(Base):
    __tablename__ = "cook_logs"
    __table_args__ = (CheckConstraint("rating BETWEEN 1 AND 5", name="rating_range"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    # RESTRICT: deleting a recipe that has cook history is refused rather than
    # silently erasing the logs. Indexed because we'll often list logs per recipe.
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="RESTRICT"), index=True
    )
    cooked_on: Mapped[date] = mapped_column(Date)
    rating: Mapped[int] = mapped_column(SmallInteger)
    notes: Mapped[str | None] = mapped_column(Text)
    modifications: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(Text)

    recipe: Mapped[Recipe] = relationship(back_populates="cook_logs")
