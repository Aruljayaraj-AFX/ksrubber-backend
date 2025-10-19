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
        input_date=request.production_date,
        sub_flag=request.sub_flag,  
        tea=request.tea,
        water = request.water,
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
    sub_flag: int = 0,  # <-- New parameter to control deletion logic
    db: Session = Depends(get_db)
):
    # --- Step 0: Validation ---
    if len(die_ids) != len(production_counts):
        return {
            "status": "error",
            "message": "DieIds and ProductionCounts must have the same length"
        }

    result = []
    hours_list = []

    # --- Step 1: Calculate production hours ---
    for idx, die_id in enumerate(die_ids):
        die = db.query(Die).filter(Die.DieId == die_id).first()
        if not die:
            result.append({
                "DieId": die_id,
                "error": "Die not found"
            })
            hours_list.append(None)
            continue

        production_count = production_counts[idx]
        try:
            hours = round(production_count / die.Pro_hr_count, 2) if die.Pro_hr_count else None
        except ZeroDivisionError:
            hours = None

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

    # --- Step 2: Apply deletion logic (skip if Sunday or sub_flag != 1) ---
    del_value = 8 if sub_flag == 1 else 0
    if input_date and input_date.weekday() == 6:  # Sunday = 6
        del_value = 0

    updated_hours = hours_list.copy()
    delete_list = [0] * len(updated_hours)

    for i in range(len(updated_hours)):
        h = updated_hours[i]
        if h is None:
            continue
        if del_value <= 0:
            break
        if h >= del_value:
            delete_list[i] = del_value
            updated_hours[i] = round(h - del_value, 2)
            del_value = 0
        else:
            delete_list[i] = h
            updated_hours[i] = 0
            del_value -= h

    # --- Step 3: Multiply updated_hours by Price ---
    price_list = []
    total_price = 0
    for i in range(len(result)):
        h = updated_hours[i]
        price = result[i].get("Price")
        if h is not None and price is not None:
            calculated_price = round(h * price, 2)
            price_list.append(calculated_price)
            total_price += calculated_price
        else:
            price_list.append(None)

    # --- Step 4: Construct Daily_Production-like object (no DB save) ---
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

    # --- Return serialized result ---
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


@router.get("/get_month_income/")
def get_month_income(
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """
    Get income for a given month and year from MonthIncome table.
    """
    month_income = db.query(MonthIncome).filter(
        extract('year', MonthIncome.date) == year,
        extract('month', MonthIncome.date) == month
    ).first()

    if not month_income:
        return {
            "status": "error",
            "message": f"No income record found for {month:02d}-{year}"
        }

    return {
        "status": "success",
        "data": {
            "month": month_income.date.strftime("%B %Y"),
            "income": round(month_income.income, 2),
            "recorded_on": month_income.created_at
        }
    }


@router.delete("/delete_production/{sno}")
def delete_production(sno: int, db: Session = Depends(get_db)):
    try:
        # Find the record by sno
        production = db.query(Daily_Production).filter(Daily_Production.sno == sno).first()
        if not production:
            return {"status": "error", "message": "Production record not found"}

        # Parse monthy_pay safely
        old_value = float(production.monthy_pay) if production.monthy_pay else 0.0

        # Find matching MonthIncome
        month_income = db.query(MonthIncome).filter(
            extract("month", MonthIncome.date) == production.date.month,
            extract("year", MonthIncome.date) == production.date.year,
        ).first()

        if month_income:
            month_income.income = max(month_income.income - old_value, 0)

        # Delete production
        db.delete(production)
        db.commit()

        return {
            "status": "success",
            "message": f"Production sno={sno} deleted successfully",
            "updated_income": round(month_income.income, 2) if month_income else None,
        }

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": f"Failed to delete: {str(e)}"}
    
