from sqlalchemy.orm import Session
from models.Die_models import Die
import uuid
from datetime import datetime, timedelta,date

# REMOVE async
def new_die(data, db: Session):
    try:
        new_die = Die(
            DieId="KSD" + str(uuid.uuid4())[:8],
            DieName=data.DieName,
            CompanyName=data.CompanyName,
            Materials=data.Materials,
            Cavity=data.Cavity,
            Weight=data.Weight,
            Pro_hr_count=data.Pro_hr_count,
            Price=data.Price,
            created_at=datetime.utcnow()
        )
        db.add(new_die)
        db.commit()
        db.refresh(new_die)  
        return new_die
    except Exception as e:
        return {"status": "error", "message": "cannot add the new die", "details": str(e)}
