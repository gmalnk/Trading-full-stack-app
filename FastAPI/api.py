from smartapi import SmartConnect
from web_socketV2 import SmartWebSocketV2
import pyotp
import PgConnection
from config import *

class TradingAPI:
    def __init__(self):
        self.obj = SmartConnect(api_key=APIKEY)

        # login api call
        self.data = self.obj.generateSession(USERNAME, APIPASSWORD, pyotp.TOTP(TOKEN).now())
        self.auth_token = self.data['data']['refreshToken']
        self.refresh_token = self.data['data']['refreshToken']
        
        # fetch the feedtoken
        self.feed_token = self.obj.getfeedToken()

        # fetch User Profile
        self.user_profile = self.obj.getProfile(self.refresh_token)
        print("session generated")
        self.api_key = APIKEY
        self.client_code = USERNAME
        self.correlation_id = "priceaction"
        self.action = 1
        self.mode = 1


        # self.token_list = [{"exchangeType": 1, "tokens": ['2885', '21091', '3456','11536', '312', '9685', '18921', '3718', '3045', '20302', '13376', '14299']}]
    def Connect_Websocket(self, token_list):
        
        def on_data(wsapp, message):
            print("Ticks: {}".format(message))
            PgConnection.add_ticks_data(message['token'], message)


        def on_open(wsapp):
            print("on open")
            self.sws.subscribe(self.correlation_id, self.mode, self.token_list)


        def on_error(wsapp, error):
            print(error)


        def on_close(wsapp):
            print("Close")

        self.token_list = [{"exchangeType": 1, "tokens": token_list}]
        if token_list:
            print("token list is provided")
            self.sws = SmartWebSocketV2(self.auth_token, self.api_key, self.client_code, self.feed_token)

            # Assign the callbacks.
            self.sws.on_open = on_open
            self.sws.on_data = on_data
            self.sws.on_error = on_error
            self.sws.on_close = on_close
            
            self.sws.connect()


    def log_out_session(self):
        try:
            self.obj.terminateSession(self.client_code)
            print("Logout Successfull")
        except Exception as e:
            print("Logout failed: {}".format(e.message))
            
    def historic_api(self,stock_token, time_frame, fromdate, todate):
        try:
            historicParam = {
                "exchange": "NSE",
                "symboltoken": stock_token,
                "interval": time_frame,
                "fromdate": fromdate,
                "todate": todate
                # "fromdate": "2021-02-08 09:00",
                # "todate": "2021-02-08 09:16"
            }
            data = self.obj.getCandleData(historicParam)
            return data["data"]
        except Exception as e:
            print(
                f"Historic Api failed: {e.message}\nparams------\n stock_token: {stock_token}\n time_frame: {time_frame}\n fromdate: {fromdate}\n todate: {todate}\n  ")

    def place_order(self, variety, tradingsymbol, symboltoken, transactiontype, ordertype, producttype, duration, price, squareoff, stoploss, quantity):
        try:
            orderparams = {
                "variety": variety,
                "tradingsymbol": tradingsymbol,
                "symboltoken": symboltoken,
                "transactiontype": transactiontype,
                "exchange": "NSE",
                "ordertype": ordertype,
                "producttype": producttype,
                "duration": duration,
                "price": price,
                "squareoff": squareoff,
                "stoploss": stoploss,
                "quantity": quantity
                }
            orderId=self.obj.placeOrder(orderparams)
            print("The order id is: {}".format(orderId))
        except Exception as e:
            print("Order placement failed: {}".format(e.message))