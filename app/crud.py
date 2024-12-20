from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from passlib.context import CryptContext
from app import schemas
from datetime import datetime, date
from .utils import  validate_password
from datetime import datetime



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password hashing

def hash_password(password: str) -> str:
    return pwd_context.hash(password)





# **User creation**




async def create_user(db, user: schemas.UserCreate):
    # Validate the password
    validation_result = validate_password(user.password)
    if validation_result != "Valid":
        raise ValueError(validation_result)  # Raise validation error if invalid
    
    # Hash the password
    hashed_password = hash_password(user.password)
    
    db_user = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "is_admin": user.is_admin  # Set admin status
    }
    
    # Insert the user into the database
    result = await db.users.insert_one(db_user)
    
    # Convert MongoDB ObjectId to string
    db_user["id"] = str(result.inserted_id)
    
    # Return a response model (exclude sensitive fields like password)
    return schemas.UserResponse(
        username=db_user["username"],
        email=db_user["email"],
        is_admin=db_user["is_admin"]
    )







# **Book creation **





async def create_book(db, book: schemas.BookCreate, user_id: str):
    # Check if book.published_date is of type datetime.date
    if isinstance(book.published_date, date):  # Check if it's a datetime.date object
        # Convert datetime.date to datetime.datetime (default to midnight)
        book.published_date = datetime.combine(book.published_date, datetime.min.time())

    book_dict = book.dict()
    book_dict["added_by"] = user_id  # Associate the book with the user ID
    
    # Insert the book into the database
    result = await db.books.insert_one(book_dict)
    
    # Return the newly created book with an ID
    book_dict["id"] = str(result.inserted_id)
    return schemas.BookResponse(**book_dict)






# **Function to update a book**




async def update_book(db, book_id: str, book: schemas.BookCreate, user_id: str):
    # Convert book dict to a dictionary format (from Pydantic model)
    book_dict = book.dict(exclude_unset=True)  # This ensures only the fields that were provided are updated

    # Check if published_date is a datetime.date object and convert to datetime.datetime
    if isinstance(book_dict.get("published_date"), date):  # Use 'date' here from datetime module
        book_dict["published_date"] = datetime.combine(book_dict["published_date"], datetime.min.time())
    
    # Add information about who updated the book
    book_dict["updated_by"] = user_id

    # Try to update the book in the database
    result = await db.books.update_one(
        {"_id": ObjectId(book_id)},  # Query to match the book by its ObjectId
        {"$set": book_dict}  # Set the new values for the book
    )

    # Check if the book was found and updated
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")

    # Optionally, fetch the updated book from the database (optional)
    updated_book = await db.books.find_one({"_id": ObjectId(book_id)})

    # Convert the MongoDB document to a response model
    updated_book["id"] = str(updated_book["_id"])  # Convert ObjectId to string for the response
    return schemas.BookResponse(**updated_book)







# **Function to delete a book **




async def delete_book(db, book_id: str, user_id: str):
    result = await db.books.delete_one({"_id": ObjectId(book_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return {"message": "Book deleted successfully"}





# **Fetch all books**




async def get_books(db):
    books = []
    async for book in db.books.find():
        if "_id" in book:
            book["id"] = str(book.pop("_id"))  # Convert MongoDB's `_id` to `id` as string
        books.append(schemas.BookResponse(**book))      # Map to the BookResponse schema
    return books





# ** searching BOOK  **



async def search_books_db(
    db,
    title: Optional[str] = None,
    author: Optional[str] = None,
    genre: Optional[str] = None
) -> List[schemas.BookResponse]:
    query = {}

    if title:
        query["$text"] = {"$search": title}
    if author:
        query["$text"] = {"$search": author}
    if genre:
        query["$text"] = {"$search": genre}

    books_cursor = db.books.find(query)

    books = []
    async for book in books_cursor:
        if "_id" in book:
            book["id"] = str(book.pop("_id"))  # Convert MongoDB _id to id
        books.append(schemas.BookResponse(**book))  # Map MongoDB document to Pydantic model

    if not books:
        raise HTTPException(status_code=404, detail="No books found")

    return books






# **Function to filter books by genre **




async def filter_books_by_genre(
    db, genre: str
) -> List[schemas.BookResponse]:
    # Query to filter books by genre
    query = {"genre": genre}

    books_cursor = db.books.find(query)

    books = []
    async for book in books_cursor:
        # Convert MongoDB _id to id and map to Pydantic model
        if "_id" in book:
            book["id"] = str(book.pop("_id"))
        books.append(schemas.BookResponse(**book))  # Map MongoDB document to Pydantic model

    if not books:
        raise HTTPException(status_code=404, detail="No books found for this genre")

    return books




# Create Borrow Request




#helper function for converting date to date time


def date_to_datetime(date_obj):
    return datetime.combine(date_obj, datetime.min.time())


async def create_borrow_request(db, user_id: str, book_id: str):
    # Create the request dictionary with user_id, book_id, and requested_date
    request = {
        "user_id": user_id,
        "book_id": book_id,
        "requested_date": date_to_datetime(datetime.utcnow().date()),  # Use datetime.utcnow() for accurate timestamp
        "status": "Pending"
    }

    # Insert the request into the MongoDB collection
    result = await db.borrow_requests.insert_one(request)

    # Add the ObjectId as a string to the request dictionary
    request["id"] = str(result.inserted_id)

    # Return the BorrowRequestResponse schema populated with the inserted data
    return schemas.BorrowRequestResponse(**request)






# Accept Borrow Request



async def accept_borrow_request(db, request_id: str):
    result = await db.borrow_requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {"status": "Accepted"}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Log the borrow activity
    borrow_request = await db.borrow_requests.find_one({"_id": ObjectId(request_id)})
    borrow_log = {
        "user_id": borrow_request["user_id"],
        "book_id": borrow_request["book_id"],
        "borrow_date": datetime.utcnow(),
        "status": "Accepted"
    }
    await db.borrow_logs.insert_one(borrow_log)

    return {"message": "Request accepted and borrow log created"}






# Deny Borrow Request



async def deny_borrow_request(db, request_id: str):
    result = await db.borrow_requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {"status": "Denied"}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return {"message": "Request denied"}




# Log Book Return



async def log_book_return(db, borrow_log_id: str):
    result = await db.borrow_logs.update_one(
        {"_id": ObjectId(borrow_log_id)},
        {"$set": {"return_date": datetime.utcnow(), "status": "Returned"}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Borrow log not found")
    
    return {"message": "Book returned and borrow log updated"}








# Fetch all borrow logs


# Helper function to convert datetime to date


def datetime_to_date(dt):
    if isinstance(dt, datetime):
        return dt.date()  # Convert datetime to date (removes time)
    return dt




async def get_borrow_logs(db):
    # Fetch all borrow logs from the 'borrow_logs' collection
    borrow_logs_cursor = db.borrow_logs.find()
    
    # Convert the cursor to a list of logs
    borrow_logs = await borrow_logs_cursor.to_list(length=None)  # None means no limit
    
    # Process each log to modify the ObjectId and convert datetime to date
    for log in borrow_logs:
        log["id"] = str(log.pop("_id"))  # Convert ObjectId to string
        log["borrow_date"] = datetime_to_date(log.get("borrow_date"))  # Convert borrow_date to date
        log["return_date"] = datetime_to_date(log.get("return_date"))  # Convert return_date to date
    
    return borrow_logs