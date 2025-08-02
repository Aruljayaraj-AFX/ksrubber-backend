# tasks/scheduler.py
import os
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import extract
from database.db import get_db  # Your DB session generator
from models.monthy import MonthIncome

def insert_monthly_income_if_new_month_task():
    db: Session = next(get_db())
    today = date.today()

    # ✅ Step 1: Only run logic if it's the 1st day of the month
    if today.day != 1:
        print("[Scheduler] Today is not 1st, skipping task.")
        return

    first_day_of_month = date(today.year, today.month, 1)

    # ✅ Step 2: Check if this month/year already exists
    existing = db.query(MonthIncome).filter(
        extract('month', MonthIncome.date) == today.month,
        extract('year', MonthIncome.date) == today.year
    ).first()

    if existing:
        print(f"[Scheduler] Income already exists for {today.strftime('%Y-%m')}.")
        return

    # ✅ Step 3: Insert default income for new month
    default_income = float(os.getenv("DEFAULT_MONTHLY_INCOME", 13000))
    new_income = MonthIncome(date=first_day_of_month, income=default_income)
    db.add(new_income)
    print(f"[Scheduler] Inserted new income for {today.strftime('%Y-%m')}")

    # ✅ Step 4: If it's a new year, delete entries older than 3 months
    if today.month == 1:  # New year just started
        three_months_ago = today - timedelta(days=90)
        db.query(MonthIncome).filter(MonthIncome.date < three_months_ago).delete()
        print(f"[Scheduler] Deleted data older than 3 months before {three_months_ago.strftime('%Y-%m-%d')}")

    db.commit()
