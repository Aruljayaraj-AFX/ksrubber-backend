from pydantic import BaseModel

class dailyupdate(BaseModel):
    DieName :str
    CompanyName :str
    Materials :str
    Cavity :int
    Weight :int
    Pro_hr_count :float
    Price :float