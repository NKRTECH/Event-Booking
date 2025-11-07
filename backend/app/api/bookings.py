from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, db

router = APIRouter()


@router.post("/events/{event_id}/book", response_model=schemas.Booking, status_code=status.HTTP_201_CREATED)
def book_event(event_id: int, booking_in: schemas.BookingCreate, db: Session = Depends(db.get_db)):
    """Create a booking for an event in a transaction-safe way.

    This uses row-level locking (SELECT FOR UPDATE) to avoid overbooking.
    """
    if booking_in.seats <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seats must be at least 1")

    # validate user exists (return clear error instead of relying on FK failure)
    user = db.query(models.User).filter(models.User.id == booking_in.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Start a transaction
    try:
        # lock the event row for this transaction
        ev = db.query(models.Event).filter(models.Event.id == event_id).with_for_update().first()
        if not ev:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

        if ev.seats_remaining < booking_in.seats:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not enough seats available")

        # create booking and decrement seats atomically within the transaction
        bk = models.Booking(event_id=event_id, user_id=booking_in.user_id, seats=booking_in.seats)
        ev.seats_remaining = ev.seats_remaining - booking_in.seats
        db.add(bk)
        db.add(ev)
        db.commit()
        db.refresh(bk)
        return bk
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Booking failed")


@router.post("/events/{event_id}/book_atomic", response_model=schemas.Booking, status_code=status.HTTP_201_CREATED)
def book_event_atomic(event_id: int, booking_in: schemas.BookingCreate, db: Session = Depends(db.get_db)):
    """Create a booking using a single atomic UPDATE to decrement seats.

    This endpoint demonstrates the atomic UPDATE approach (UPDATE ... WHERE seats_remaining >= :n).
    It updates the event row first and then creates the booking within the same transaction.
    """
    if booking_in.seats <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seats must be at least 1")

    # validate user exists
    user = db.query(models.User).filter(models.User.id == booking_in.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        # perform atomic update
        from sqlalchemy import update as sa_update

        stmt = (
            sa_update(models.Event)
            .where(models.Event.id == event_id)
            .where(models.Event.seats_remaining >= booking_in.seats)
            .values(seats_remaining=(models.Event.seats_remaining - booking_in.seats))
        )
        res = db.execute(stmt)
        # res.rowcount may be 0 if condition didn't match
        if res.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not enough seats available or event not found")

        # create booking record
        bk = models.Booking(event_id=event_id, user_id=booking_in.user_id, seats=booking_in.seats)
        db.add(bk)
        db.commit()
        db.refresh(bk)
        return bk
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Booking failed (atomic)")


@router.post("/bookings/{booking_id}/cancel", response_model=schemas.Booking)
def cancel_booking(booking_id: int, db: Session = Depends(db.get_db)):
    bk = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not bk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if bk.status == "canceled":
        return bk

    try:
        # lock the event row before updating seats
        ev = db.query(models.Event).filter(models.Event.id == bk.event_id).with_for_update().first()
        if not ev:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found for booking")

        bk.status = "canceled"
        ev.seats_remaining = ev.seats_remaining + bk.seats
        db.add(bk)
        db.add(ev)
        db.commit()
        db.refresh(bk)
        return bk
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cancellation failed")


@router.get("/users/{user_id}/bookings", response_model=list[schemas.Booking])
def list_user_bookings(user_id: int, db: Session = Depends(db.get_db)):
    items = db.query(models.Booking).filter(models.Booking.user_id == user_id).all()
    # FastAPI + Pydantic (with from_attributes=True) will convert ORM models to response models
    return items
