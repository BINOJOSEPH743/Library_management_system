import pytest
import time
from fastapi.testclient import TestClient
from app.main import app  # Import your FastAPI app
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client





def test_user_registration(client):
    user_data = {
        "username": "testuser1",
        "email": "testuser@example.com",
        "password": "Testpassword123@",
        "is_admin": False
    }

    response = client.post("/register/", json=user_data)
    print(response.json())  # Print the response for debugging
    assert response.status_code == 200



def test_login(client):
    # Register a user first
    user_data = {
        "username": "testuser1",
        "email": "testuser1@example.com",
        "password": "Testpassword123@",  # Ensure password meets requirements
        "is_admin": False
    }

  

    # Login with the registered user credentials
    login_data = {
        "username": "testuser1",
        "password": "Testpassword123@",
    }

    # Send POST request to login endpoint
    response = client.post(
        "/login/",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Assert the response
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"
    assert response_data["message"] == "User logged in successfully"




def test_create_and_update_book(client):
    # Step 1: Register an admin user
    admin_user_data = {
        "username": "adminuser",
        "email": "admin@example.com",
        "password": "AdminPassword123@",
        "is_admin": True
    }
    register_response = client.post("/register/", json=admin_user_data)
    print("Admin Registration Response:", register_response.json())  # Debugging info
    assert register_response.status_code == 200

    # Step 2: Login as the admin to get the access token
    login_data = {
        "username": "adminuser",
        "password": "AdminPassword123@",
    }
    login_response = client.post(
        "/login/",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    print("Login Response:", login_response.json())  # Debugging info
    assert login_response.status_code == 200

    token = login_response.json().get("access_token")
    assert token is not None  # Ensure token is generated

    # Step 3: Create a book using the admin token
    book_data = {
        "title": "Sample Book",
        "author": "Author Name",
        "genre": "Fiction",
        "published_date": "2024-01-01",  # Ensure this matches the required format
    }
    create_book_response = client.post(
        "/books/",
        json=book_data,
        headers={"Authorization": f"Bearer {token}"},  # Add token to the header
    )
    print("Create Book Response:", create_book_response.json())  # Debugging info
    assert create_book_response.status_code == 200

    # Step 4: Verify the response for book creation
    created_book = create_book_response.json()
    book_id = created_book["id"]
    assert created_book["title"] == "Sample Book"
    assert created_book["author"] == "Author Name"
    assert created_book["genre"] == "Fiction"
    assert created_book["published_date"] == "2024-01-01"
    assert "id" in created_book

    # Step 5: Update the book using the admin token
    updated_book_data = {
        "title": "Updated Title",
        "author": "Updated Author",
        "genre": "Non-Fiction",
        "published_date": "2025-01-01",
    }
    update_response = client.put(
        f"/books/{book_id}",
        json=updated_book_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    print("Update Book Response:", update_response.json())  # Debugging info
    assert update_response.status_code == 200

    # Step 6: Verify the updated book details
    updated_book = update_response.json()
    assert updated_book["id"] == book_id
    assert updated_book["title"] == "Updated Title"
    assert updated_book["author"] == "Updated Author"
    assert updated_book["genre"] == "Non-Fiction"
    assert updated_book["published_date"] == "2025-01-01"





def test_delete_book(client):
    # Step 1: Register an admin user
    admin_user_data = {
        "username": "adminuser1",
        "email": "admin@example.com",
        "password": "AdminPassword123@",
        "is_admin": True,
    }
    register_response = client.post("/register/", json=admin_user_data)
    assert register_response.status_code == 200

    # Step 2: Login as the admin to get the access token
    login_data = {
        "username": "adminuser1",
        "password": "AdminPassword123@",
    }
    login_response = client.post(
        "/login/",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")
    assert token is not None

    # Step 3: Create a book
    book_data = {
        "title": "Book to Delete",
        "author": "Delete Author",
        "genre": "Drama",
        "published_date": "2024-01-01",
    }
    create_response = client.post(
        "/books/",
        json=book_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 200
    book_id = create_response.json()["id"]

    # Step 4: Delete the book
    delete_response = client.delete(
        f"/books/{book_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    print("Delete Book Response:", delete_response.json())  # Debugging info
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Book deleted successfully"}




def test_fetch_all_books(client):

    # Step 4: Fetch all books
    fetch_response = client.get("/books/")
    print("Fetch All Books Response:", fetch_response.json())  # Debugging info
    assert fetch_response.status_code == 200

    books = fetch_response.json()
    assert len(books) >= 2  # At least two books should exist
    titles = [book["title"] for book in books]
    assert "Book One" in titles
    assert "Book Two" in titles



def test_search_books(client):
    # Step 4: Search books by title
    search_response = client.get("/books/search", params={"title": "Book One"})
    assert search_response.status_code == 200


    # Step 5: Search books by author
    search_response = client.get("/books/search", params={"author": "Author Two"})
    assert search_response.status_code == 200
 

    # Step 6: Search books by genre
    search_response = client.get("/books/search", params={"genre": "Fiction"})
    assert search_response.status_code == 200
   


def test_filter_books(client):
    # Step 4: Filter books by genre
    filter_response = client.get("/books/genre", params={"genre": "Fiction"})
    assert filter_response.status_code == 200








def test_create_borrow_request(client):
    # Step 1: Register a user
    user_data = {
        "username": "testuser5",
        "email": "testuser@example.com",
        "password": "TestPassword123@",
        "is_admin": True,
    }
    register_response = client.post("/register/", json=user_data)
    assert register_response.status_code == 200

    # Step 2: Login to get access token
    login_data = {
        "username": "testuser5",
        "password": "TestPassword123@",
    }
    login_response = client.post(
        "/login/",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")
    assert token is not None

    # Step 3: Create a book to be borrowed
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "genre": "Fiction",
        "published_date": "2024-01-01",
    }
    create_book_response = client.post(
        "/books/",
        json=book_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_book_response.status_code == 200
    book_id = create_book_response.json().get("id")

    # Step 4: Create borrow request
    borrow_request_data = {
        "user_id": "testuser5",  # assuming you pass the user_id here
        "book_id": book_id,
    }






















#borrow log

def test_view_borrow_logs(client):
    # Step 1: Assume we have an admin token (you can hardcode it for testing purposes)
    admin_token = "your_admin_token_here"  # Replace with a valid admin token for testing

    # Step 2: View borrow logs (admin only)
    view_borrow_logs_response = client.get(
        "/borrow/logs",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert view_borrow_logs_response.status_code == 200

    # Step 3: Validate the response
    borrow_logs = view_borrow_logs_response.json()
    assert isinstance(borrow_logs, list)  # Ensure the response is a list
    assert len(borrow_logs) > 0  # There should be at least one log







