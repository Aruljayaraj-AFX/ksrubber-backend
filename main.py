from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uvicorn
from routers.die_add import router
from datetime import datetime, timedelta
from sqlalchemy.orm import Session


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/afx/pro_ksrubber/v1", tags=["ksrubber"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)