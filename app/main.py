from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database.seed import seed_sources
from app.api.prices import router as price_router
from app.api.collector import router as collector_router
from app.scheduler.scheduler import start_scheduler
from app.scheduler.scheduler import stop_scheduler
from app.api.prediction import router as prediction_router



@asynccontextmanager
async def lifespan(app : FastAPI):
    print("Hi!")
    print(seed_sources())
    start_scheduler()
    yield
    stop_scheduler()
    print("By!")


app = FastAPI(lifespan = lifespan)

app.include_router(price_router)
app.include_router(prediction_router)
app.include_router(collector_router)