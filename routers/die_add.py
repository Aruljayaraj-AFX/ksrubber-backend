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
from typing import List, Optional
from datetime import date as DateType
from models.production import Daily_Production
from sqlalchemy import extract
from models.monthy import MonthIncome



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

@router.delete("/delete_die/{die_id}")
async def delete_die(die_id: str, db: Session = Depends(get_db)):
    die_to_delete = db.query(Die).filter(Die.DieId == die_id).first()
    if not die_to_delete:
        raise HTTPException(status_code=404, detail="Die not found")
    try:
        db.delete(die_to_delete)
        db.commit()
        return {"status": "success", "message": f"Die {die_id} deleted successfully."}
    except Exception as e:
        return {"status": "error", "message": "Failed to delete die", "details": str(e)}
    

@router.post("/compute_production/")
def compute_production_api(
    die_ids: List[str],
    production_counts: List[int],
    input_date: Optional[DateType] = None,
    is_holiday: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    if len(die_ids) != len(production_counts):
        return {"status": "error", "message": "DieIds and ProductionCounts must have the same length"}

    result = []
    hours_list = []

    for idx, die_id in enumerate(die_ids):
        die = db.query(Die).filter(Die.DieId == die_id).first()
        if not die:
            result.append({"DieId": die_id, "error": "Die not found"})
            hours_list.append(None)
            continue

        production_count = production_counts[idx]
        hours = round(production_count / die.Pro_hr_count, 2) if die.Pro_hr_count else None
        hours_list.append(hours)

        result.append({
            "DieId": die.DieId,
            "DieName": die.DieName,
            "CompanyName": die.CompanyName,
            "Materials": die.Materials,
            "Cavity": die.Cavity,
            "Weight": die.Weight,
            "Pro_hr_count": die.Pro_hr_count,
            "Price": die.Price,
            "ProvidedProductionCount": production_count,
            "CalculatedHours": hours
        })

    # --- Apply deletion logic ---
    del_value = 8
    if input_date and (input_date.weekday() == 6 or is_holiday):
        del_value = 0

    updated_hours = hours_list.copy()
    delete_list = [0] * len(updated_hours)

    for i in range(len(updated_hours)):
        h = updated_hours[i]
        if h is None: continue
        if del_value <= 0: break
        if h >= del_value:
            delete_list[i] = del_value
            updated_hours[i] = round(h - del_value, 2)
            del_value = 0
        else:
            delete_list[i] = h
            updated_hours[i] = 0
            del_value -= h

    # --- Multiply hours by price ---
    price_list = []
    total_price = 0
    for i in range(len(result)):
        h = updated_hours[i]
        price = result[i].get("Price")
        calculated_price = round(h * price, 2) if h is not None and price is not None else None
        price_list.append(calculated_price)
        if calculated_price: total_price += calculated_price

    new_daily_pro = Daily_Production(
        date=input_date,
        DieId=die_ids,
        overall_production=production_counts,
        overall_time=hours_list,
        delete_index_hr=delete_list,
        price=price_list,
        overtime=updated_hours,
        monthy_pay=str(total_price)
    )

    return {
        "status": "success",
        "new_daily_pro": {
            "date": str(new_daily_pro.date) if new_daily_pro.date else None,
            "DieId": new_daily_pro.DieId,
            "overall_production": new_daily_pro.overall_production,
            "overall_time": new_daily_pro.overall_time,
            "delete_index_hr": new_daily_pro.delete_index_hr,
            "price": new_daily_pro.price,
            "overtime": new_daily_pro.overtime,
            "monthy_pay": new_daily_pro.monthy_pay
        },
        "details": result
    }