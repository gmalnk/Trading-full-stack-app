from smartapi import SmartConnect
from FastAPI.web_socketV2 import SmartWebSocketV2
from FastAPI import PgConnection
from FastAPI.config import *
from FastAPI.Constants import *
from pya3 import *
import time
import pyotp

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
    
    def cancle_order(self, order_id, variety):
        return self.obj.cancelOrder(order_id=order_id, variety=variety)
    
    def get_positions(self):
        return self.obj.position()
    
    def get_orderbook(self):
        return self.obj.orderBook()
    
    def cancel_all_open_orders(self):
        open_orders = self.get_orderbook()
        if open_orders["data"] != None:
            for open_order in open_orders["data"]:
                if open_order["orderstatus"] != "complete" and open_order["orderstatus"] != "rejected" and open_order["orderstatus"] != "cancelled":
                    self.cancle_order(order_id = open_order["orderid"], variety = open_order["variety"])
                    time.sleep(0.21)
    
    def close_all_open_positions(self):
        open_positions = self.get_positions()
        if open_positions["data"] != None:
            for o in open_positions["data"]:
                if int(o["netqty"]) != 0:
                    transaction_type = "SELL" if int(o["netqty"]) > 0 else "BUY"
                    self.place_order(o["variety"],
                                     o["tradingsymbol"],
                                     o["symboltoken"],
                                     transaction_type,
                                     o["ordertype"],
                                     o["producttype"],
                                     o["duration"],
                                     o["price"],
                                     o["s"])
                    time.sleep(0.21)
    
class AlphaVantageAPI:
    """Alpha Vantage API class"""
    def __init__(self) -> None:
        # Enter your alpha vantage key here
        self.apikey = ALPHA_API_KEY
        
    def get_historical_data(self, parameters):
        pass
    
class AliceBlueAntAPI:
    def __init__(self) -> None:
        self.apikey = ALICE_API_KEY
        self.username = ALICE_USERNAME
        self.password = ALICE_PASSWORD
        self.twofa = ALICE_TWOFA
        self.app_id = ALICE_APP_ID
        self.api_secret = ALICE_API_SECRET
        self.obj = Aliceblue(user_id = self.username,api_key= self.apikey)
        self.obj.get_contract_master(Exchanges.NSE)
        self.session_id = self.obj.get_session_id()
        
    def get_balance(self):
        return self.obj.get_balance()
    
    def get_profile(self):
        return self.obj.get_profile()
    
    def get_daywise_positions(self):
        return self.obj.get_daywise_positions()
    
    def get_netwise_positions(self):
        return self.obj.get_netwise_positions()
    
    def get_holding_positions(self):
        return self.obj.get_holding_positions()
    
    def get_instrument_by_symbol(self, symbol):
        return self.obj.get_instrument_by_symbol(Exchanges.NSE, symbol=symbol)
    
    def search_instruments(self, symbol):
        return self.obj.search_instruments(symbol=symbol)
    
    def place_orders(self, symbol):
        return self.obj.place_order(
                    transaction_type = TransactionType.Buy,
                    instrument = self.get_instrument_by_symbol(symbol),
                    quantity = 1,
                    order_type = OrderType.Market,
                    product_type = ProductType.Delivery,
                    price = 0.0,
                    trigger_price = None,
                    stop_loss = None,
                    square_off = None,
                    trailing_sl = None,
                    is_amo = False,
                    order_tag='order1')
        
    def modify_order(self, symbol):
        return self.obj.modify_order(
                    transaction_type = TransactionType.Buy,
                    instrument = self.get_instrument_by_symbol(symbol),
                    order_id="220803000207716",
                    quantity = 1,
                    order_type = OrderType.Limit,
                    product_type = ProductType.Delivery,
                    price=30.0,
                    trigger_price = None)
        
    def cancel_order(self, order_id):
        return self.obj.cancel_order(order_id)
    
    def get_order_history(self):
        order_history_response = self.obj.get_order_history('')
        return Alice_Wrapper.get_order_history(order_history_response)
    
    def get_order_history(self, order_id):
        return self.obj.get_order_history(order_id)
    
    def get_history_of_all_orders(self):
        return self.obj.get_order_history("")
    
    def get_trade_book(self):
        return self.obj.get_trade_book()
    
    def get_script_info(self, symbol):
        return self.obj.get_scrip_info(self.get_instrument_by_symbol(symbol))
    
    def historical_data_one_minute(self, symbol, start, end):
        return self.obj.alice.get_historical(
            self.get_instrument_by_symbol(symbol),
            start,
            end,
            '1',
            False)
    
    def historical_data_one_day(self, symbol, start, end):
        return self.obj.alice.get_historical(
            self.get_instrument_by_symbol(symbol),
            start,
            end,
            'D',
            False)