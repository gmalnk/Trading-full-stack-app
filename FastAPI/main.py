from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import PgConnection
from tokens import tokens

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def get_startup():
    return {"hello" : "world! you are in the fast api home page"}

@app.get("/stocklist")
def get_stocklist():
    return tokens

@app.get("/{stock_token}/{time_frame}")
def get_stock(stock_token: int, time_frame: str):
    return PgConnection.api_get_stock_data(stock_token, time_frame)

@app.get("/trendlines/{stock_token}/{time_frame}")
def get_trendline(stock_token: int, time_frame: str):
    return PgConnection.api_get_trendline_data(stock_token, time_frame)