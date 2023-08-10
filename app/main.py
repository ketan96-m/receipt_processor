from fastapi import FastAPI, Query, Path
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from typing import List, Dict
from pydantic import BaseModel, Field
from datetime import date, time
from math import ceil
from uuid import uuid1, UUID
from typing_extensions import Annotated


app = FastAPI() #start the app

POINTS = {}  #e.g {'fa2e171e-37b4-11ee-a93d-34c93d08306c':'15'}

class Item(BaseModel):
  """
  Model class for items in the receipt
  """
  shortDescription: Annotated[
            str, 
            Query(description="The Short Product Description for the item.",
                  examples=["Mountain Dew 12PK"])]
  price: Annotated[
            float, 
            Query(description="The total price payed for this item.",
                  examples=[6.49])]

class Receipt(BaseModel):
  """
  Model class for the receipt
  """
  retailer: Annotated[
            str, 
            Query(description="The name of the retailer or store the receipt is from.",
                  examples=["Target"])]
  purchaseDate: Annotated[
            date, 
            Query(description="The date of the purchase printed on the receipt.",
                  examples=["2022-01-01"])]
  purchaseTime: Annotated[
            time, 
            Query(description="The time of the purchase printed on the receipt. 24-hour time expected.",
                  examples=["13:01"])]
  items: Annotated[
            List[Item], 
            Query(min_length=1)]
  total: Annotated[
            float, 
            Query(description="The total amount paid on the receipt.",
                  examples=[6.49])]


def number_of_alphanumeric(retailer: str) -> int:
  """
  Return the points based on number of alpha numeric values
  """
  return len(list(filter(str.isalnum, retailer)))

def round_dollar_amount(total: float) -> int:
  """
  Return the points whole dollar price value
  """
  return 50 if total%1==0 else 0

def multiple_quarter(total: float) -> int:
  """
  Return the points based on the price being a factor of 0.25
  """
  return 25 if total%0.25==0 else 0

def every_two_items(items: List[Item]) -> int:
  """
  Return the points for every 2 items
  """
  return (5*(len(items)//2))

def trimmed_len_multiple_three(items: List[Item]) -> int:
  """
  Return the points based on the trimmed length of each items' description
  """
  ans = 0
  for item in items:
      if len(item.shortDescription.strip())%3==0:
        ans+= ceil(item.price*0.2)
  return ans

def odd_purchase_date(purchaseDate: date) -> int:
  """
  Return the points based on purchase day
  """
  return 6 if purchaseDate.day%2==1 else 0

def purchase_time_between_two_four(purchaseTime: time) -> int:
  """
  Return the points based on purchase time
  """
  return 10 if (time.fromisoformat("16:00")>purchaseTime>time.fromisoformat("14:00")) else 0


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse("The receipt is invalid", status_code=400)

@app.post(
    "/receipts/process",
    summary="Submits a receipt for processing",
    description="Submits a receipt for processing",
)
async def process_receipts(receipt: Receipt):
  """
  Handle the post request
  One point for every alphanumeric character in the retailer name.
  50 points if the total is a round dollar amount with no cents.
  25 points if the total is a multiple of 0.25.
  5 points for every two items on the receipt.
  If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 
  and round up to the nearest integer. The result is the number of points earned.
  6 points if the day in the purchase date is odd.
  10 points if the time of purchase is after 2:00pm and before 4:00pm.
  """
  total_points = 0
  total_points += ( number_of_alphanumeric(receipt.retailer) 
                   + round_dollar_amount(receipt.total)
                   + multiple_quarter(receipt.total)
                   + every_two_items(receipt.items)
                   + trimmed_len_multiple_three(receipt.items)
                   + odd_purchase_date(receipt.purchaseDate)
                   + purchase_time_between_two_four(receipt.purchaseTime))
  id = uuid1()
  POINTS[id] = total_points
  return {"id":id}

@app.get(
    "/receipts/{id}/points",
    summary= "Returns the points awarded for the receipt",
    description= "Returns the points awarded for the receipt",
)
async def calculate_points(id: Annotated[UUID, Path(title="The ID of the receipt")]):
  """
  Handle the get request
  """
  if id not in POINTS:
    return PlainTextResponse("No receipt found for that id", status_code=404)
    # raise HTTPException(detail="No receipt found for that id",status_code=404)
  return {"points":POINTS[id]}