from sqlalchemy import Column, Integer, Float, DateTime, func,String
from sqlalchemy.ext.declarative import declarative_base

Base5 = declarative_base()

class Userbase(Base5):
    __tablename__ = 'pre_come_user'

    id = Column(Integer, primary_key=True, index=True)
    income = Column(String, nullable=False)
    created_at = Column(DateTime,server_default=func.now(),nullable=False)