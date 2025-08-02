from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.die_add import router
from apscheduler.schedulers.background import BackgroundScheduler
from utils.automatic_income_update import insert_monthly_income_if_new_month_task
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import uvicorn


load_dotenv()


scheduler = BackgroundScheduler()

# Lifespan context for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(insert_monthly_income_if_new_month_task, "interval", hours=24)
    scheduler.start()
    print("[Scheduler] Background job started.")
    yield
    scheduler.shutdown()
    print("[Scheduler] Background job stopped.")

# FastAPI app with lifespan handler
app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your routers
app.include_router(router, prefix="/afx/pro_ksrubber/v1", tags=["ksrubber"])

# Run the app
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
