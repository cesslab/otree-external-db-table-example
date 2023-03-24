import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchem.ext.declarative import declarative_base

engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()