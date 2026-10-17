"""Cached SQLAlchemy engine and session factory."""

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL


@lru_cache(maxsize=1)
def get_engine():
    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://") :]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return create_engine(
        url,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
    )


@lru_cache(maxsize=1)
def get_session_factory():
    return sessionmaker(bind=get_engine(), expire_on_commit=False)
