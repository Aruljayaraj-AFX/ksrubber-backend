from  sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URL= "postgresql://postgres:Arul123arul12@db.tppoaztcksactarjkrix.supabase.co:5432/postgres"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
session=SessionLocal(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()