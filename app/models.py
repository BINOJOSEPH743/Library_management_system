from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime


# **user model**


class CustomUser(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    is_admin: bool = False

    class Config:

        from_attributes = True


# **book model**


class Book(BaseModel):
    title: str
    author: str
    genre: str
    published_date: date

    class Config:

        from_attributes = True  # Enable ORM mode for compatibility


# **BorrowRequest**


class BorrowRequest(BaseModel):
    user_id: str
    book_id: str
    requested_date: date
    status: str  # Pending, Accepted, Denied

    class Config:
        from_attributes = True


# **BorrowLog **


class BorrowLog(BaseModel):
    user_id: str
    book_id: str
    borrow_date: date
    return_date: Optional[datetime]
    status: str  # Accepted, Returned

    class Config:
        from_attributes = True


class MessageRequest(BaseModel):
    sender_id: str
    receiver_id: str
    message: str