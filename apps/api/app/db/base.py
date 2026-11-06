"""Shared SQLAlchemy declarative base for Phase 1 models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for ORM models added in the relevant implementation phase."""
