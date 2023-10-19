from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from FastAPI import PgConnection
from FastAPI.Constants import ALL_TOKENS

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/pat/")
def get_startup():
    return {"hello" : "world! you are in the fast api home page"}

@app.get("/api/v1/pat/stockDict")
def  get_stockDict():
    return {"stocksDict": ALL_TOKENS}

@app.get("/api/v1/pat/stocklist/{timeFrame}/{stockListCategory}/{stockListSort}")
def get_stocklist(timeFrame:str, stockListCategory:str, stockListSort:str):
    print("data", type(timeFrame), stockListCategory, stockListSort)
    return  PgConnection.get_stock_details(timeFrame, stockListCategory, stockListSort)
    
@app.put("/api/v1/pat/stocklist")
def  update_stocklist(stockDetails:dict):
    # updates 
    return {"stock_token":stockDetails["stock_token"],"time_frame": stockDetails["time_frame"],"category":stockDetails['chategory'] }
    #  PgConnection.update_stock_details_table({"stock_token":stockDetails["stock_token"],"time_frame": stockDetails["time_frame"],"chategory":stockDetails['chategory'] })

@app.get("/api/v1/pat/{stock_token}/{time_frame}")
def get_stock(stock_token: str, time_frame: str):
    stockData =   PgConnection.api_get_stock_data(stock_token, time_frame)
    data =  PgConnection.api_get_trendline_data(stock_token, time_frame)
    return {"stockData":stockData,"trendlineData": data["trendlineData"], "linesData": data['linesData']}

@app.post("/api/v1/pat/tradedetails")
def add_trade( tradedetails:dict):
    tradedetails = tradedetails['params']
    PgConnection.add_trade_data(tradedetails)

@app.get("/api/v1/pat/trades")
def get_trades():
    return PgConnection.get_all_trades()

@app.delete("/api/v1/pat/trade/{id}")
def delete_trade(id:int):
    PgConnection.delete_trade(id)