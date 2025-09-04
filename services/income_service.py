from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import date
from models.monthy import MonthIncome

def add_daily_overtime(db: Session, overtime_amount: float, input_date: date):
    # find monthly row
    month_income = db.query(MonthIncome).filter(
        extract('year', MonthIncome.date) == input_date.year,
        extract('month', MonthIncome.date) == input_date.month
    ).first()
    if not month_income:
        # fallback: create base row for this month
        month_income = MonthIncome(date=date(input_date.year, input_date.month, 1), income=13000.0)
        db.add(month_income)
        db.commit()
        db.refresh(month_income)
    # update overtime
    month_income.income += overtime_amount
    db.commit()
    return {
        "status": "success",
        "month": input_date.strftime("%B %Y"),
        "updated_income": month_income.income
    }