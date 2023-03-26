import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_DATABASE_URL = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
engine = create_engine(os.getenv("DATABASE_URL", SQLITE_DATABASE_URL))
Session = sessionmaker(bind=engine)
Base = declarative_base()

@staticmethod
def create_database_tables():
    """ Conditionally create database tables if they don't already exist """
    # Prevents unnecessary sql statements from being executed if the tables already exist
    if not engine.dialect.has_table(engine, "player_history"):
        Base.metadata.create_all(engine)
