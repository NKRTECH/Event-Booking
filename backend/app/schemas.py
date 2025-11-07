from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    role: str
    # Pydantic V2: allow creating models from ORM objects / attribute access
    model_config = ConfigDict(from_attributes=True)


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    capacity: int


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    capacity: Optional[int] = None


class Event(EventBase):
    id: int
    seats_remaining: int
    # Pydantic V2: allow creating models from ORM objects / attribute access
    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    seats: int = 1


class Booking(BaseModel):
    id: int
    event_id: int
    user_id: int
    seats: int
    status: str
    created_at: datetime
    # Pydantic V2: allow creating models from ORM objects / attribute access
    model_config = ConfigDict(from_attributes=True)
