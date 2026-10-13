from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
@lru_cache(maxsize=1)
def get_engine():
 url=DATABASE_URL.replace('postgresql://','postgresql+psycopg://',1)
 return create_engine(url,pool_pre_ping=True,connect_args={'check_same_thread':False} if url.startswith('sqlite') else {})
@lru_cache(maxsize=1)
def get_session_factory():return sessionmaker(bind=get_engine(),expire_on_commit=False)
