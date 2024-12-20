from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from datetime import datetime
from pydantic import field_validator
import datetime


# **User creation schema **


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_admin: bool = False


class UserResponse(BaseModel):
    username: str
    email: EmailStr
    is_admin: bool

    class Config:
        # orm_mode = True
        from_attributes = True


# **Book creation schema **


class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    published_date: date


class BookResponse(BookCreate):
    id: str
    added_by: str

    class Config:
        # orm_mode = True
        from_attributes = True


# ** BOOK BORROW REQUEST SCHEMA **


class BorrowRequest(BaseModel):
    user_id: str  # Reference to CustomUser (ObjectId as string)
    book_id: str  # Reference to Book (ObjectId as string)
    requested_date: date
    status: str  # Pending, Accepted, Denied

    @field_validator("user_id", "book_id")
    def validate_objectid(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return str(v)  # Convert ObjectId to string

    class Config:
        from_attributes = True  # Enable ORM mode for compatibility


#  **BOOK BorrowRequestResponse SCHEMA **


class BorrowRequestResponse(BorrowRequest):
    id: str  # The ObjectId as a string

    class Config:
        # orm_mode = True
        from_attributes = True
        populate_by_name = True  # Correct for Pydantic v2


#  **BOOK BorrowLogResponse SCHEMA **


class BorrowLogResponse(BaseModel):
    id: str
    user_id: str
    book_id: str
    borrow_date: date
    status: str  # Accepted, Returned
    return_date: Optional[datetime.date] = None

    class Config:
        from_attributes = True
