from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import extract,func
from datetime import date as DateType
from models.Die_models import Die
from models.monthy import MonthIncome
from models.setting_income import dailyIncome
from models.production import Daily_Production
from schema.daily import UpdateCurrentMonthIncome
from datetime import datetime
from datetime import date, timedelta
import calendar


def get_all_die_data(db: Session):
    try:
        dies = db.query(Die).all()
        return {"status": "success", "data": dies}
    except Exception as e:
        return {"status": "error", "message": "Failed to fetch dies", "details": str(e)}

def get_die_data_by_name(db: Session, die_name: str):
    try:
        dies = db.query(Die).filter(Die.DieName == die_name).all()
        return {"status": "success", "data": dies}
    except Exception as e:
        return {"status": "error", "message": "Failed to fetch dies by name", "details": str(e)}
    

def get_daily_production(db: Session):
    try:
        daily_update=db.query(Daily_Production).all()
        return{"status":"success", "data":daily_update}
    except Exception as e:
        return {"status": "error", "message": "Failed to fetch dies", "details": str(e)}
    
def get_income(db: Session):
    try:
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        result = (
            db.query(
                func.sum(MonthIncome.income).label("total_income"),
                func.sum(MonthIncome.tea).label("total_tea"),
                func.sum(MonthIncome.water).label("total_water")
            )
            .filter(
                extract('year', MonthIncome.date) == current_year,
                extract('month', MonthIncome.date) == current_month
            )
            .first()
        )
        return {
            "total_income": result.total_income ,
            "total_tea": result.total_tea ,
            "total_water": result.total_water
        }
    except Exception as e:
        return {"status": "error", "message": "Failed to fetch monthly data", "details": str(e)}

def get_production_by_date(db: Session, input_date: DateType):
    try:
        daily_update = db.query(Daily_Production).filter(Daily_Production.date == input_date).all()
        return {"status": "success", "data": daily_update}
    except Exception as e:
        return {"status": "error", "message": "Failed to fetch production data", "details": str(e)}

def compute_production_hours(
    die_ids: List[str],
    production_counts: List[int],
    db: Session,
    input_date: Optional[DateType] = None,
    tea:Optional[int]=0,
    water:Optional[int]=0,
    sub_flag: Optional[int] = None  # default 1 → normal day
):
    if len(die_ids) != len(production_counts):
        return {
            "status": "error",
            "message": "DieIds and ProductionCounts must have the same length"
        }

    result = []
    hours_list = []

    # Step 1: Calculate production hours
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
            hours = round(production_count / die.Pro_hr_count)
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

    # Step 2: Apply deletion logic
    # Only apply deletion if sub_flag == 1 (i.e., checkbox not selected / normal day)
    del_value = 8 if sub_flag == 1 else 0

    # Skip deletion automatically if Sunday
    if input_date and input_date.weekday() == 6:
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

    # Step 3: Multiply updated_hours by Price to get price_list
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

    # Step 4: Save to DB if input_date provided
    updated_income = None
    if input_date:
        existing_entry = db.query(Daily_Production).filter(
            Daily_Production.date == input_date
        ).first()
        if existing_entry:
            return {
                "status": "error",
                "message": f"Production already exists for date {input_date}"
            }
        daily_price = 0
        daily_income_setting = db.query(dailyIncome).first()
        if daily_income_setting:
            monthly_income = daily_income_setting.income
        
            month = input_date.month
            year = input_date.year
            
            # total days in current month
            total_days = calendar.monthrange(year, month)[1]
            # calculate per-day price
            daily_price = monthly_income / total_days

        leave = 0
        if len(die_ids) == 1:
            special_dies = {"KSD223adbd2", "KSDd3a58378"}
            if len(die_ids) == 1 and die_ids[0] in special_dies:
                leave = 1 

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

        db.add(new_daily_pro)
        db.commit()

        existing = db.query(MonthIncome).filter(
            extract('month', MonthIncome.date) == input_date.month,
            extract('year', MonthIncome.date) == input_date.year
        ).first()

        if existing:
            if leave == 1:
                existing.income -= float(daily_price)
            else:
                existing.income += float(total_price)
            existing.tea+=tea
            existing.water+=water
            updated_income = round(existing.income, 2)
            db.commit()
        else:
            new_income = MonthIncome(
            date=input_date.replace(day=1),   # store 1st day of month
            income=round(float(total_price + monthly_income), 2),  
            tea=0,
            water=0
            )
            db.add(new_income)
            db.commit()
            db.refresh(new_income)
            updated_income = round(new_income.income, 2)
            
    return {
        "status": "success",
        "data": result,
        "calculated_hours": updated_hours,
        "deleted_distribution": delete_list,
        "price_list": price_list,
        "total_price": round(total_price, 2),
        "updated_income": updated_income
    }
