from fastapi.testclient import TestClient
from .main import app, number_of_alphanumeric,round_dollar_amount, multiple_quarter, every_two_items,trimmed_len_multiple_three,\
                        odd_purchase_date,purchase_time_between_two_four, Item, Receipt
from datetime import date, time
import uuid
import json

client = TestClient(app)

fake_receipt = {
    "retailer": "Walgreens",
    "purchaseDate": "2022-01-02",
    "purchaseTime": "08:13",
    "total": "2.65",
    "items": [
        {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
        {"shortDescription": "Dasani", "price": "1.40"}
    ]
}

fake_invalid_receipt = {
    "retler": "Walgreens",
    "pureDate": "2022-01-02",
    "purchaseTime": "08:13",
    "total": "2.65",
    "items": [
        {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
        {"shortDesiption": "Dasani", "price": "1.40"}
    ]
}

def test_process_receipts():
    response = client.post("/receipts/process", json=fake_receipt)
    assert response.status_code==200
    response = client.post("/receipts/process", json=fake_invalid_receipt)
    assert response.status_code==400
    assert response.text=="The receipt is invalid"

def test_calculate_points():
    response = client.get(f"/receipts/{uuid.uuid1()}/points")
    assert response.text == "No receipt found for that id"
    assert response.status_code==404
    response = client.post("/receipts/process", json=fake_receipt)
    response = client.get(f"/receipts/{response.json()['id']}/points")
    assert response.json().get('points')==15, print(response.content)


def test_number_of_alphanumeric():
    assert number_of_alphanumeric("SDLFJH") == 6
    assert number_of_alphanumeric("1938&&&&&&dfsd") == 8
    assert number_of_alphanumeric("1938 &&&&&dfsd") == 8

def test_round_dollar_amount():
    assert round_dollar_amount(10.00)==50
    assert round_dollar_amount(10.50)==0

def test_multiple_quarter():
    assert multiple_quarter(12.25)==25
    assert multiple_quarter(12.30)==0

def test_every_two_items():
    assert every_two_items([1,2])==5
    assert every_two_items([3,4,5,6,7])==10

def test_odd_purchase_date():
    assert odd_purchase_date(date.fromisoformat("2022-01-01"))==6
    assert odd_purchase_date(date.fromisoformat("2023-01-06"))==0

def test_trimmed_len_multiple_three():
    a = Receipt.model_validate(fake_receipt)
    assert trimmed_len_multiple_three(a.items)==1

def test_purchase_time_between_two_four():
    assert purchase_time_between_two_four(time.fromisoformat("14:01"))==10
    assert purchase_time_between_two_four(time.fromisoformat("17:00"))==0