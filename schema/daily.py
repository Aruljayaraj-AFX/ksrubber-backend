from pydantic import BaseModel
from typing import List, Optional   
from datetime import date

class ProductionFilterRequest(BaseModel):
    DieIds: List[str]
    ProductionCounts: List[int]
    production_date: Optional[date] = None
    sub_flag: Optional[int] = 1  # optional, default normal day
    tea:Optional[int] = 0
    water : Optional[int]=0