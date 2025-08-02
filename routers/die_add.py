from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from schema.new_die import dailyupdate
from services.die_add import new_die

router = APIRouter()

@router.post("/add_die")
async def add_die(data:dailyupdate, db: Session = Depends(get_db)):
    return new_die(data,db)
