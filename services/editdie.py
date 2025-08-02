from sqlalchemy.orm import Session
from models.Die_models import Die
import uuid
from datetime import datetime, timedelta,date
from fastapi import APIRouter, Depends, HTTPException

def edit_diee(die_id,data,db:Session):
    try:
        die = db.query(Die).filter(Die.DieId == die_id).first()

        if not die:
            raise HTTPException(status_code=404, detail="Die not found")

        # Update fields if provided
        for field, value in data.dict(exclude_unset=True).items():
            setattr(die, field, value)

        die.updated_at = datetime.utcnow()  # Optional: add updated_at field
        db.commit()
        db.refresh(die)
        return {"status": "success", "data": die}
    except Exception as e:
        return {"status": "error", "message": "Failed to update die", "details": str(e)}