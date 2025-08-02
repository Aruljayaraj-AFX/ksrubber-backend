from  sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.environ["DATABASE_URL"]

DB_URL= db_url
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
session=SessionLocal(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()