from sqlalchemy import Column, String, Integer, Date, DateTime, Float, func
from sqlalchemy.ext.declarative import declarative_base

Base2 = declarative_base()

class MonthIncome(Base2):
    __tablename__ = 'income'

    date = Column(Date, primary_key=True)  
    income = Column(Float, nullable=False)  
    tea = Column(String, nullable=True, default=0)
    water = Column(String, nullable=True, default=0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)