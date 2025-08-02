from pydantic import BaseModel
from typing import Optional

class dailyupdate(BaseModel):
    DieName :str
    CompanyName :str
    Materials :str
    Cavity :int
    Weight :int
    Pro_hr_count :float
    Price :float


class DieUpdate(BaseModel):
    DieName: Optional[str]
    CompanyName: Optional[str]
    Materials: Optional[str]
    Cavity: Optional[int]
    Weight: Optional[float]
    Pro_hr_count: Optional[int]
    Price: Optional[float]
