from sqlalchemy import Column, String, Integer, DateTime, Float, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base1 = declarative_base()

class Die(Base1):
    __tablename__ = 'Die'

    DieId = Column(String, primary_key=True, nullable=False)
    DieName = Column(String, nullable=False)
    CompanyName = Column(String, nullable=False)
    Materials = Column(String, nullable=False)
    Cavity = Column(Integer, nullable=False)
    Weight = Column(Float, nullable=False)
    Pro_hr_count = Column(Float, nullable=False)
    Price = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('DieName', 'Cavity', name='uix_die_name_cavity'),
    )
