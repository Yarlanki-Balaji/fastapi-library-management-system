from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# ------------------ DATA ------------------

books = [
    {"id": 1, "title": "Python Basics", "author": "John", "genre": "Tech", "is_available": True},
    {"id": 2, "title": "AI Guide", "author": "Smith", "genre": "Science", "is_available": True},
    {"id": 3, "title": "History of India", "author": "Raj", "genre": "History", "is_available": False},
    {"id": 4, "title": "Data Science", "author": "Anna", "genre": "Tech", "is_available": True},
    {"id": 5, "title": "Fiction Story", "author": "Leo", "genre": "Fiction", "is_available": True},
    {"id": 6, "title": "Machine Learning", "author": "David", "genre": "Science", "is_available": False}
]

borrow_records = []
record_counter = 1

# ------------------ HELPERS ------------------

def find_book(book_id):
    for b in books:
        if b["id"] == book_id:
            return b
    return None

def calculate_due_date(days, member_type):
    if member_type == "premium":
        days = min(days, 60)
    else:
        days = min(days, 30)
    return f"Return by Day {15 + days}"

def filter_books_logic(genre=None, author=None, is_available=None):
    result = books

    if genre is not None:
        result = [b for b in result if b["genre"].lower() == genre.lower()]

    if author is not None:
        result = [b for b in result if author.lower() in b["author"].lower()]

    if is_available is not None:
        result = [b for b in result if b["is_available"] == is_available]

    return result

# ------------------ MODELS ------------------

class BorrowRequest(BaseModel):
    member_name: str = Field(..., min_length=2)
    book_id: int = Field(..., gt=0)
    borrow_days: int = Field(..., gt=0, le=30)
    member_id: str = Field(..., min_length=4)
    member_type: str = "regular"

# ------------------ APIs ------------------

@app.get("/")
def home():
    return {"message": "Welcome to City Public Library"}

@app.get("/books")
def get_books():
    available = sum(1 for b in books if b["is_available"])
    return {
        "total": len(books),
        "available_count": available,
        "books": books
    }

@app.get("/books/summary")
def summary():
    available = sum(1 for b in books if b["is_available"])
    borrowed = len(books) - available

    genre_count = {}
    for b in books:
        genre_count[b["genre"]] = genre_count.get(b["genre"], 0) + 1

    return {
        "total": len(books),
        "available": available,
        "borrowed": borrowed,
        "genres": genre_count
    }

@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    return {"error": "Book not found"}

@app.get("/borrow-records")
def get_records():
    return {
        "total": len(borrow_records),
        "records": borrow_records
    }

@app.post("/borrow")
def borrow(data: BorrowRequest):
    global record_counter

    book = find_book(data.book_id)
    if not book:
        return {"error": "Book not found"}

    if not book["is_available"]:
        return {"error": "Book already borrowed"}

    book["is_available"] = False

    record = {
        "record_id": record_counter,
        "member_name": data.member_name,
        "book_id": data.book_id,
        "due_date": calculate_due_date(data.borrow_days, data.member_type)
    }

    borrow_records.append(record)
    record_counter += 1

    return record

@app.get("/books/filter")
def filter_books(genre: Optional[str] = None, author: Optional[str] = None, is_available: Optional[bool] = None):
    data = filter_books_logic(genre, author, is_available)
    return {"count": len(data), "books": data}
