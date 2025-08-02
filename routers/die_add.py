from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from schema.new_die import dailyupdate,DieUpdate
from schema.daily import ProductionFilterRequest
from services.die_add import new_die
from services.editdie import edit_diee
from services.die_detials import get_all_die_data,compute_production_hours,get_daily_production,get_die_data_by_name,get_production_by_date
from datetime import datetime,date
from models.Die_models import Die



router = APIRouter()

@router.post("/add_die")
async def add_die(data:dailyupdate, db: Session = Depends(get_db)):
    return new_die(data,db)

@router.put("/edit_die/{die_id}")
def edit_die(die_id: str, data: DieUpdate, db: Session = Depends(get_db)):
    return edit_diee(die_id,data,db)

@router.get("/get_all_die")
def get_all_die(db: Session = Depends(get_db)):
    return get_all_die_data(db)

@router.get("/get-die-by-name/")
def fetch_die_by_name(die_name: str, db: Session = Depends(get_db)):
    return get_die_data_by_name(db, die_name)

@router.get("/daily-production/")
def fetch_daily_production(db: Session = Depends(get_db)):
    return get_daily_production(db)

@router.get("/get-production-date/")
def get_by_date(input_date: date, db: Session = Depends(get_db)):
    return get_production_by_date(db, input_date)


@router.post("/calculate_production_hours")
def calculate_production_hours(request: ProductionFilterRequest, db: Session = Depends(get_db)):
    return compute_production_hours(
        die_ids=request.DieIds,
        production_counts=request.ProductionCounts,
        input_date=request.date,
        db=db
    )

