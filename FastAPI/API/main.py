from fastapi import FastAPI, Header, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from FastAPI.API.auth import *
from FastAPI.DBConn.PGConn import PGConnectionNew
from FastAPI.Constants import ALL_TOKENS

app = FastAPI()

origins = [
    "http://localhost:3000"
]

paths = ["/api/v1/pat/signin", "/api/v1/pat/signup"]

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path in paths:
        return await call_next(request)         
    else:
        token_header = request.headers.get("Authorization")
        if token_header != None:
            token_type , token = token_header.split()
            if token == None:
                return JSONResponse(content = {"conn_status":"f","message":"Authorization header not found"})
            response = decode_jwt_token(token)
            if response == JSONResponse:
                return response
            if PGConnectionNew.authenticate(response["email"], response["password"]):
                return await call_next(request)
            else:
                return JSONResponse(content = {"conn_status":"f","message":"invalid email or password"})
    return JSONResponse(content = {"conn_status":"f","message":"Authorization header not found"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.add_middleware(auth_middleware)
# app.middleware("http")(auth_middleware)

@app.get("/api/v1/pat/")
def get_startup():
    return {"hello" : "world! you are in the fast api home page"}

@app.get("/api/v1/pat/stockDict")
def  get_stockDict():
    return {"stocksDict": ALL_TOKENS}

@app.get("/api/v1/pat/stocklist/{timeFrame}/{stockListCategory}/{stockListSort}")
def get_stocklist(timeFrame:str, stockListCategory:str, stockListSort:str):
    print("data", type(timeFrame), stockListCategory, stockListSort)
    return  PGConnectionNew.get_stock_details(timeFrame, stockListCategory, stockListSort)
    
@app.put("/api/v1/pat/stocklist")
def  update_stocklist(stockDetails:dict):
    # updates 
    return {"stock_token":stockDetails["stock_token"],"time_frame": stockDetails["time_frame"],"category":stockDetails['chategory'] }

@app.get("/api/v1/pat/{stock_token}/{time_frame}")
def get_stock(stock_token: str, time_frame: str):
    stockData =   PGConnectionNew.api_get_stock_data(stock_token=stock_token, time_frame=time_frame)
    data =  PGConnectionNew.api_get_trendline_data(stock_token=stock_token, time_frame=time_frame)
    return {"stockData":stockData,"trendlineData": data["trendlineData"], "linesData": data['linesData']}

@app.post("/api/v1/pat/tradedetails")
def add_trade( tradedetails:dict):
    tradedetails = tradedetails['params']
    PGConnectionNew.add_trade_data(tradedetails)

# @app.get("/api/v1/pat/trades", dependencies=[Depends(auth_middleware)])
@app.get("/api/v1/pat/trades")
def get_trades():
    return PGConnectionNew.get_all_trades()

@app.delete("/api/v1/pat/trade/{id}")
def delete_trade(id:int):
    PGConnectionNew.delete_trade(id)


# Route to obtain JWT token (login)
@app.post("/api/v1/pat/signin")
def login_for_access_token(password: str = Header(default=None),email: str = Header(default = None)):
    email = email.lower()
    if PGConnectionNew.authenticate(email=email, password=password):
        data = {"email":email,"password":password}
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_jwt_token(data, expires_delta)
        return {"conn_status":"s","access_token": access_token, "token_type": "bearer", "message":"authorized"}
    return {"conn_status":"f","message":"wrong email or password"}

# Route to create account and get JWT token 
@app.post("/api/v1/pat/signup")
def signup_for_access_token(password: str = Header(default=None),email: str = Header(default = None), name : str = Header(default = None)):
    print({"email":email,"password":password})
    if email == None:
        return JSONResponse(content= {"conn_status":"f", "message":"email is none"})
    if password == None:
        return JSONResponse(content= {"conn_status":"f", "message":"password is none"})
    if PGConnectionNew.add_user(name= name, email=email.lower(), password=password):
        data = {"email":email,"password":password}
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_jwt_token(data, expires_delta)
        return JSONResponse(content={"access_token": access_token, "token_type": "bearer", "conn_status":"s"})
    return JSONResponse(content= {"conn_status":"f","message":"user already exists"})

