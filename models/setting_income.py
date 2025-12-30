from sqlalchemy import Column, Integer, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base4 = declarative_base()

class dailyIncome(Base4):
    __tablename__ = 'setting_income'

    id = Column(Integer, primary_key=True, index=True)
    income = Column(Float, nullable=False)
    created_at = Column(DateTime,server_default=func.now(),nullable=False)
    updated_at = Column(DateTime,server_default=func.now(),onupdate=func.now(),nullable=False)