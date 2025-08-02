from pydantic import BaseModel
from typing import List
from datetime import date

class ProductionFilterRequest(BaseModel):
    DieIds: List[str]
    ProductionCounts: List[int]
    date: date  # required
