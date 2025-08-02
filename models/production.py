from sqlalchemy import Column, String, Integer, DateTime, func, JSON , Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Daily_Production(Base):
    __tablename__ = 'Production'

    sno = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    date = Column(Date,unique=True)
    DieId = Column(JSON, nullable=False)
    overall_production = Column(JSON, nullable=False)
    overall_time = Column(JSON, nullable=False)
    overtime = Column(JSON, nullable=False)
    delete_index_hr=Column(JSON,nullable=False)
    price = Column(JSON, nullable=False)
    monthy_pay = Column(String, nullable=False)
    CreatedAt = Column(DateTime, server_default=func.now(), nullable=False)