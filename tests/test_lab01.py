"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""
import copy
 
import pytest
from jsonschema import ValidationError, validate
 
from tools import get_book_schema

def test_list_books_empty_returns_empty_array(client):
    response = client.get("/books")
 
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json() == []

def test_id_books_not_exist_returns_404_and_json(client):
    response = client.get("/books/9999")

    assert response.status_code == 404
    assert response.content_type == "application/json"
    assert response.get_json()["code"] == "NOT_FOUND"

def test_post_book_with_only_author_returns_400_and_errors(client):
    response = client.post("books", json={"author": "Me"})

    assert response.status_code == 400
    body = response.get_json()
    assert body["code"] == "VALIDATION_ERROR"
    fields = {error["field"] for error in body["errors"]}
    assert "title" in fields

def test_post_valid_book_delete_get_returns_404(client):
    created = client.post("/books", json={"title": "Temp", "author": "Someone"})

    assert created.status_code == 201
    book_id = created.get_json()["id"]
 
    assert client.delete(f"/books/{book_id}").status_code == 204
 
    getback = client.get(f"/books/{book_id}")
    assert getback.status_code == 404
    assert getback.get_json()["code"] == "NOT_FOUND"

def test_response_extra_field_blocked(client):
    schema = get_book_schema()
    created = client.post(
        "/books",
        json={
            "title": "API Design Patterns",
            "author": "J.J. Geewax",
            "year": 2021,
            "isbn": "9781617295850",
        },
    )
    assert created.status_code == 201
    book = created.get_json()
 
    validate(book, schema)
 
    leaky = copy.deepcopy(book)
    leaky["password_hash"] = "should-never-be-returned"
    with pytest.raises(ValidationError):
        validate(leaky, schema)


