from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Response

from app.db import engine, Base

app = FastAPI(title="Event Booking Microservice", version="0.1.0")

# CORS - allow localhost dev origins by default
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # create tables for development (use Alembic for production migrations)
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok"}


# include routers
from app.api import events
from app.api import bookings

app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(bookings.router, tags=["bookings", "users", "events"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
