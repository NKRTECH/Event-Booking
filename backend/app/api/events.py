from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict

from app import models, schemas, db

router = APIRouter()


@router.get("/", summary="List events (paginated)")
def list_events(page: int = Query(1, ge=1), size: int = Query(20, ge=1), db: Session = Depends(db.get_db)) -> Dict:
    skip = (page - 1) * size
    total = db.query(models.Event).count()
    items = db.query(models.Event).offset(skip).limit(size).all()
    # convert ORM models to Pydantic objects for safe JSON serialization
    pyd_items = [schemas.Event.from_orm(ev) for ev in items]
    return {"items": pyd_items, "total": total}


@router.post("/", response_model=schemas.Event, status_code=status.HTTP_201_CREATED)
def create_event(event_in: schemas.EventCreate, db: Session = Depends(db.get_db)):
    ev = models.Event(
        title=event_in.title,
        description=event_in.description,
        start_time=event_in.start_time,
        end_time=event_in.end_time,
        capacity=event_in.capacity,
        seats_remaining=event_in.capacity,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


@router.get("/{event_id}", response_model=schemas.Event)
def get_event(event_id: int, db: Session = Depends(db.get_db)):
    ev = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return ev


@router.put("/{event_id}", response_model=schemas.Event)
def update_event(event_id: int, event_in: schemas.EventUpdate, db: Session = Depends(db.get_db)):
    ev = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    data = event_in.dict(exclude_unset=True)
    # handle capacity change by adjusting seats_remaining accordingly
    if "capacity" in data:
        new_capacity = data["capacity"]
        delta = new_capacity - ev.capacity
        ev.seats_remaining = max(0, ev.seats_remaining + delta)
        ev.capacity = new_capacity

    for field, value in data.items():
        if field == "capacity":
            continue
        setattr(ev, field, value)

    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(db.get_db)):
    ev = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    db.delete(ev)
    db.commit()
    return None
