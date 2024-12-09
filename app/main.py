from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.database import db,  get_db
from app import crud, schemas
from app.schemas import BorrowLogResponse, BookResponse
import jwt
from passlib.context import CryptContext
from datetime import date, datetime, timedelta
from app.crud import get_borrow_logs





app = FastAPI()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#SECRET_KEY = "your-secret-key"  # Replace with a secure secret key

# Initialize CryptContext for password hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




# Secret key used for encoding and decoding JWT
SECRET_KEY = "your-secret-key"  # Use a more secure key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Set expiration time for the token

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Creates a JWT token with the given data.
    
    :param data: The data to encode in the token (e.g., user_id, is_admin)
    :param expires_delta: How long the token will be valid (default is 30 minutes)
    :return: JWT token as a string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Define the expiration time (in UTC)
    expire = datetime.utcnow() + expires_delta

    # Add expiration and data to the JWT payload
    to_encode = data.copy()
    to_encode.update({"exp": expire})

    # Encode the token using the secret key and the specified algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt





# **Function to decode the token and extract user information**



def get_user_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(f"Decoded payload: {payload}")  # For debugging purposes
        user_id = payload.get("user_id")
        is_admin = payload.get("is_admin", True)
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user_id, is_admin
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    





# **User registration endpoint **



@app.post("/register/", response_model=dict)
async def register_user(user: schemas.UserCreate):
    # Check if the user already exists
    existing_user = await db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    try:
        # Create the user (admin or regular user)
        created_user = await crud.create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Return a tailored response based on the user type
    if user.is_admin:
        return {"message": "Admin created successfully", "data": created_user}
    else:
        return {"message": "User created successfully", "data": created_user}








#**login for user and admin**



@app.post("/login/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Fetch the user from the database
    user = await db.users.find_one({"username": form_data.username})
    
    # Verify user existence and password
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Determine if the user is an admin
    is_admin = user.get("is_admin", False)  # Default to False if is_admin is missing
    
    # Determine user type and comment
    user_type = "admin" if is_admin else "user"
    message = f"{user_type.capitalize()} logged in successfully"
    
    # Create the JWT token with required fields
    token = create_access_token(data={
        "user_id": str(user["_id"]),
        "is_admin": is_admin
    })
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "message": message
    }









# **Admin-only create book endpoint**



@app.post("/books/", response_model=schemas.BookResponse)
async def create_book_endpoint(book: schemas.BookCreate, token: str = Depends(oauth2_scheme)):
    user_id, is_admin = get_user_from_token(token)
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    return await crud.create_book(db, book, user_id)





# **Admin-only update book endpoint**




@app.put("/books/{book_id}", response_model=schemas.BookResponse)
async def update_book_endpoint(book_id: str, book: schemas.BookCreate, token: str = Depends(oauth2_scheme)):
    user_id, is_admin = get_user_from_token(token)
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    return await crud.update_book(db, book_id, book, user_id)

@app.patch("/books/{book_id}", response_model=schemas.BookResponse)
async def partial_update_book_endpoint(book_id: str, book: schemas.BookCreate, token: str = Depends(oauth2_scheme)):
    user_id, is_admin = get_user_from_token(token)
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    return await crud.update_book(db, book_id, book, user_id)






# **Admin-only delete book endpoint**



@app.delete("/books/{book_id}", response_model=dict)
async def delete_book_endpoint(book_id: str, token: str = Depends(oauth2_scheme)):
    user_id, is_admin = get_user_from_token(token)
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    return await crud.delete_book(db, book_id, user_id)





# **Fetch all books**




@app.get("/books/", response_model=list[BookResponse])
async def fetch_all_books():
    books = await crud.get_books(db)
    if not books:
        raise HTTPException(status_code=404, detail="No books found")
    return books









# **Search books with filters (title, author, genre)**




@app.get("/books/search", response_model=List[schemas.BookResponse])
async def search_books(
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    db=Depends(get_db)
):
    books = await crud.search_books_db(db, title=title, author=author, genre=genre)
    return books







#**filter using genre**



@app.get("/books/genre", response_model=List[schemas.BookResponse])
async def filter_books(
    genre: str  # Required query parameter for genre
):
    books = await crud.filter_books_by_genre(db, genre=genre)
    return books







#**borrow books**




@app.post("/borrow/request", response_model=schemas.BorrowRequestResponse)
async def create_borrow_request(
    borrow_request: schemas.BorrowRequest, token: str = Depends(oauth2_scheme)
):
    # Access user_id and book_id from the request body
    return await crud.create_borrow_request(db, borrow_request.user_id, borrow_request.book_id)







# **Accept a borrow request (admin only)**



@app.put("/borrow/request/{request_id}/accept")
async def accept_borrow_request(request_id: str, token: str = Depends(oauth2_scheme)):
    user_id, is_admin = get_user_from_token(token)
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    # Accept the borrow request
    return await crud.accept_borrow_request(db, request_id)







# **Deny a borrow request (admin only)**




@app.put("/borrow/request/{request_id}/deny")
async def deny_borrow_request(request_id: str, token: str = Depends(oauth2_scheme)):
    user_id, is_admin = get_user_from_token(token)
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    # Deny the borrow request
    return await crud.deny_borrow_request(db, request_id)







#** Log book return**



@app.put("/borrow/log/{borrow_log_id}/return")
async def return_book(borrow_log_id: str, token: str = Depends(oauth2_scheme)):
    user_id, is_admin = get_user_from_token(token)
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    return await crud.log_book_return(db, borrow_log_id)






# ** fetching all logs **



@app.get("/borrow/logs", response_model=List[BorrowLogResponse])
async def view_borrow_logs(db=Depends(get_db)):
    """
    Fetch all borrow logs from the database.
    """
    return await get_borrow_logs(db)

