from smartapi import SmartConnect
from FastAPI.API.ExternalAPI.kite_trade import *
from FastAPI.API.ExternalAPI.web_socketV2 import SmartWebSocketV2
from FastAPI.DBConn.PGConn import PGConnectionNew
from FastAPI.DBConn.Tables import TableSQL
from FastAPI.Modules.Utility import Utility
from FastAPI.Modules.Logging import *
from FastAPI.config import *
from FastAPI.Constants import *
from datetime import date, timedelta, datetime
from pya3 import *
import time
import pyotp
import requests
import time
from abc import ABC, abstractmethod

class API(ABC):
    @abstractmethod
    def historic_data(self):
        """Abstract method to fetch historical data for given tf, stock, from, to """
        pass
    
    @abstractmethod
    def fetch_15min_data_at_market_close(self):
        """Abstract method to fetch 15-minute time frame data every day for given stock"""
        pass

    @abstractmethod
    def fetch_1d_data_at_market_close(self):
        """Abstract method to fetch 1-day time frame data every day for given stock."""
        pass

    @abstractmethod
    def fetch_all_15min_data_for_stock(self):
        """Abstract method to fetch all 15-minute time frame data for given stock."""
        pass

    @abstractmethod
    def fetch_all_1d_data_for_stock(self):
        """Abstract method to fetch all 1-day time frame data for given stock."""
        pass
    
class AngelOneAPI(API):
    def __init__(self):
        self.obj = SmartConnect(api_key=ANGEL_APIKEY)

        # login api call
        self.data = self.obj.generateSession(ANGEL_APIUSERNAME, ANGEL_APIPASSWORD, pyotp.TOTP(ANGEL_APITOKEN).now())
        self.auth_token = self.data['data']['refreshToken']
        self.refresh_token = self.data['data']['refreshToken']
        
        # fetch the feedtoken
        self.feed_token = self.obj.getfeedToken()

        # fetch User Profile
        self.user_profile = self.obj.getProfile(self.refresh_token)
        print("session generated")
        self.api_key = ANGEL_APIKEY
        self.client_code = ANGEL_APIUSERNAME
        self.correlation_id = "priceaction"
        self.action = 1
        self.mode = 1

    def historic_data(self, time_frame:TimeFrame, stock_token:str,from_date:datetime, to_date:datetime, nb_bars:int=0)->json:
        nb_bars = Utility.get_nb_bars(time_frame=time_frame, from_date=from_date, to_date=to_date) if nb_bars == 0 else nb_bars
        additional_margin = 1
        payload = {
            "action": "Req",
            "bars": nb_bars + additional_margin,
            "duration": self.get_duration(time_frame),
            "period": "I",
            "rtype": "OHLCV",
            "sort": "ASC",
            "to": self.get_to_date_string(to_date),
            "topic": "1."+stock_token,
            "type": self.get_type(time_frame)
        }
        ANGEL_HEADERS["X-Access-Token"] = self.refresh_token
        response = requests.post(url=ANGEL_URL, headers=ANGEL_HEADERS, json=payload)
        if response.status_code != 200:
            daily_logger.error(f"Failed to get historical data for stock_token: {stock_token} time_frame: {time_frame} from_date: {from_date} to_date: {to_date} nb_bars: {nb_bars}")
            return []
        from_epoch = Utility.datetime_to_epoch(input=from_date) if from_date != datetime.min else 0
        table = Utility.get_table(time_frame=time_frame)
        return [ table(
            token = stock_token,
            time = Utility.epoch_to_datetime(epoch=entry["time"]/1000),
            open = entry["open"],
            high = entry["high"],
            low = entry["low"],
            close = entry["close"],
            volume = entry["volume"]
            ) for entry in response.json() if from_epoch < entry["time"]/1000]
           
    def fetch_15min_data_at_market_close(self, stock_token:str)->list[TableSQL]:
        from_date = PGConnectionNew.get_latest_date(stock_token=stock_token, time_frame=TimeFrame.FIFTEEN_MINUTE)
        data = self.historic_data(time_frame=TimeFrame.FIFTEEN_MINUTE, stock_token=stock_token, from_date=from_date, to_date=datetime.now())
        return data
    
    def fetch_1d_data_at_market_close(self, stock_token:str)->list[TableSQL]:
        from_date = PGConnectionNew.get_latest_date(stock_token=stock_token, time_frame=TimeFrame.ONE_DAY)
        data = self.historic_data(time_frame=TimeFrame.ONE_DAY, stock_token=stock_token, from_date=from_date, to_date=datetime.now())
        return data
    def fetch_all_15min_data_for_stock(self, stock_token:str)->list[TableSQL]:
        data = []
        to_date=datetime.now()
        while True:
            result = self.historic_data(time_frame=TimeFrame.FIFTEEN_MINUTE, stock_token=stock_token, from_date=datetime.min, to_date=to_date, nb_bars=10000) 
            if not result :
                break
            result.extend(data)
            data = result
            result = []
            if data[0].time < datetime(2016,10,3):
                break
            to_date = data[0].time - timedelta(minutes=5)
        PGConnectionNew.bulk_save(data=data)
    def fetch_all_1d_data_for_stock(self, stock_token:str)->list[TableSQL]:
        data = []
        to_date=datetime.now()
        while True:
            result = self.historic_data(time_frame=TimeFrame.ONE_DAY, stock_token=stock_token, from_date=datetime.min, to_date=to_date, nb_bars=10000) 
            if not result :
                break
            result.extend(data)
            data = result
            if data[0].time < datetime(1994,1,1):
                break
            to_date = data[0].time - timedelta(minutes=5)
        PGConnectionNew.bulk_save(data=data)
        
    def get_duration(self, time_frame:TimeFrame)->str:
        match time_frame:
            # case TimeFrame.FIVE_MINUTE:
            #     return 5
            case TimeFrame.FIFTEEN_MINUTE:
                return 15
            case TimeFrame.THIRTY_MINUTE:
                return 30
            case TimeFrame.ONE_HOUR:
                return 1
            case TimeFrame.TWO_HOUR:
                return 2
            case TimeFrame.FOUR_HOUR:
                return 4
            case TimeFrame.ONE_DAY:
                return 1
            case TimeFrame.ONE_WEEK:
                return 1
            case TimeFrame.ONE_MONTH:
                return 1
            case default:
                return 1
    
    def get_type(self, time_frame:TimeFrame)->str:
        match time_frame:
            # case TimeFrame.FIVE_MINUTE:
            #     return "m"
            case TimeFrame.FIFTEEN_MINUTE:
                return "m"
            case TimeFrame.THIRTY_MINUTE:
                return "m"
            case TimeFrame.ONE_HOUR:
                return "h"
            case TimeFrame.TWO_HOUR:
                return "h"
            case TimeFrame.FOUR_HOUR:
                return "h"
            case TimeFrame.ONE_DAY:
                return "D"
            case TimeFrame.ONE_WEEK:
                return "W"
            case TimeFrame.ONE_MONTH:
                return "M"
            case default:
                return "D"
    
    def get_to_date_string(self, to_date:datetime)->str:
        return to_date.strftime("%Y-%m-%dT%H:%M:%S.%f%z")+"+05:30"
      
    # daily run for getting latest stock data for fifteen minute
    def get_latest_candle_data(self, stock_token):
        try:
            startdate_fifteen = PGConnectionNew.get_latest_date(stock_token, "FIFTEEN_MINUTE")
            end_date = date.today()
            
            if startdate_fifteen == 0:
                self.get_all_data_smart_api_fifteentf("FIFTEEN_MINUTE", stock_token)
            else:
                startdate_fifteen += timedelta(days=1)
                self.get_latest_candle_data_from_smartAPI(startdate_fifteen.date(), end_date, stock_token, "FIFTEEN_MINUTE")
            
            startdate_daily = PGConnectionNew.get_latest_date(stock_token, "ONE_DAY")
            if startdate_daily != 0:
                startdate_daily += timedelta(days=1)
                self.get_latest_candle_data_from_smartAPI(startdate_daily.date(), end_date, stock_token, "ONE_DAY")
        except (Exception) as error:
            daily_logger.error("Failed at get_latest_candle_data method error message: " + str(error))
        finally:
            daily_logger.info(f"successfully fetched latest data for stock_token: {stock_token}")

    # this method gets data between starttime and endtine for given stock and given time frame
    def get_latest_candle_data_from_smartAPI(self, startdate_fifteen, end_date, stock_token, time_frame):
        try:
            if startdate_fifteen > end_date:
                return
            if (end_date-startdate_fifteen).days <= 30:
                rows = self.historic_api(stock_token, time_frame, fromdate = startdate_fifteen.strftime("%Y-%m-%d %H:%M"), todate = end_date.strftime("%Y-%m-%d %H:%M"))
                PGConnectionNew.add_past_data_from_smart_api(
                    stock_token, time_frame, rows)
            else:
                daily_logger.info(f"stock {stock_token} has not been updated from last 30 days")
        except (Exception) as error:
            daily_logger.error("Failed at get_latest_candle_data_fifteen method error message: " + str(error))
        finally:
            daily_logger.info(f"successfully fetched latest data for stock_token: {stock_token} and time_frame : {time_frame}")

    def get_all_data_smart_api_fifteentf(self, time_frame, stock_token):
        try:
            data = []
            for i in range(16):
                fromdate = (date.today()-timedelta(days=28*(i+1))).strftime("%Y-%m-%d %H:%M")
                todate = (date.today()-timedelta(days=28*(i))).strftime("%Y-%m-%d %H:%M")
                rows = self.historic_api(stock_token, time_frame, fromdate, todate)
                if (rows):
                    data.extend(rows)
                time.sleep(.4)
            if len(data) == 0:
                daily_logger.info(f"not found data for fifteen min tf at smart api for stock_token {stock_token}")
                return
            daily_logger.info(f"successfully fetched all fifteen tf data for stock_token: {stock_token}")
            PGConnectionNew.add_past_data_from_smart_api(
                stock_token, time_frame, data)
        except (Exception) as error:
            daily_logger.error("Failed at get_all_data_smart_api_fifteentf method error message: " + str(error))
        finally:
            daily_logger.info(f"done for stock_token : {stock_token}")
    
    # self.token_list = [{"exchangeType": 1, "tokens": ['2885', '21091', '3456','11536', '312', '9685', '18921', '3718', '3045', '20302', '13376', '14299']}]
    def Connect_Websocket(self, token_list):
        
        def on_data(wsapp, message):
            print("Ticks: {}".format(message))
            PGConnectionNew.add_ticks_data(message['token'], message)


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
    
class AlphaVantageAPI(API):
    """Alpha Vantage API class"""
    def __init__(self) -> None:
        # Enter your alpha vantage key here
        self.apikey = ALPHA_API_KEY
        
    def historic_data(self):
        pass
        
    def fetch_15min_data_at_market_close(self):
        pass
    
    def fetch_1d_data_at_market_close(self):
        pass
    
    def fetch_all_15min_data_for_stock(self):
        pass
    
    def fetch_all_1d_data_for_stock(self):
        pass 
    
class AliceBlueAntAPI(API):
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
        
    def historic_data(self):
        pass
        
    def fetch_15min_data_at_market_close(self):
        pass
    
    def fetch_1d_data_at_market_close(self):
        pass
    
    def fetch_all_15min_data_for_stock(self):
        pass
    
    def fetch_all_1d_data_for_stock(self):
        pass 
        
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
        
class ZerodhaKiteAPI(API):
    def __init__(self) -> None:
        self.enctoken = ZERODHA_ENCTOKEN
        self.kite = KiteApp(enctoken=self.enctoken)       
    
    def historic_data(self):
        url = "https://kite.zerodha.com/oms/instruments/historical/2953217/3minute?user_id=NB1759&oi=1&from=2023-11-07&to=2023-12-07"
        headers = {
            "Authorization":"enctoken +cD2wTIpC5NW6bj54OWHGk0bufR+NCiQFKWQ3xryJ2JzQgi8KRoE7PaLnq1l88TiCyyw5hBgJa7jvLHECIRBQMcGmkrsm0USjs4xTYFsabHvL8G2ldHjdQ==",        
            "Accept":"*/*",
            "Cookie":"cf_clearance=UcAS3zWyye0J8GN4ctAZAYXHekk2mc4_O.rRWLSyEf8-1701538566-0-1-7ba06e6e.b17f233a.90482a30-160.0.0; _cfuvid=gkkk9M.a2p79AgiTQcnxiS4.8Yvo2GkTsNJ3xhB.iHA-1701864492924-0-604800000; kf_session=fvPRgvzPm1iSrYLN56IXDwfV2OoYXGVG; user_id=NB1759; public_token=Xk6oZjIkoC49uYVx8jejkPiQwjTztnsn; enctoken=+cD2wTIpC5NW6bj54OWHGk0bufR+NCiQFKWQ3xryJ2JzQgi8KRoE7PaLnq1l88TiCyyw5hBgJa7jvLHECIRBQMcGmkrsm0USjs4xTYFsabHvL8G2ldHjdQ==; __cf_bm=rqeq.Ytlgzz0dgsCBR.pcN2QzfLg43DZp06C4y5OeHA-1701891858-0-AZFdgVwxIRRUlJrqvhWfwhRaHADiInl/WBh5SmonuzHQHQmRzT3aWouqyPqDEWq6AMH+KVZ3beW/46+dF828iDA=",
            "Accept-Encoding":"gzip, deflate, br",
            "Accept-Language":"en-US,en;q=0.9",
            "Referer":"https://kite.zerodha.com/static/build/chart-beta.html?v=3.3.0",
            'Sec-Ch-Ua-Mobile':"?0",
            "Sec-Ch-Ua-Platform":"Windows",
            'Sec-Fetch-Dest':"empty",
            "Sec-Fetch-Mode":"cors",
            "Sec-Fetch-Site":'same-origin',
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            }
        response = requests.get(url, headers=headers)
        print(response.text)
            
    def fetch_15min_data_at_market_close(self):
        pass
    
    def fetch_1d_data_at_market_close(self):
        pass
    
    def fetch_all_15min_data_for_stock(self):
        pass
    
    def fetch_all_1d_data_for_stock(self):
        pass 
    
class MoneyControlAPI(API):
    def __init__(self) -> None:
        pass
    
    def historic_data(self, fromdate, todate, stocksymbol, timeFrame, count_back):
        headers = {
            "Accept":"*/*",
            "Accept-Encoding":"gzip, deflate, br",
            "Accept-Language":"en-US,en;q=0.9",
            "Origin":"https://www.moneycontrol.com",
            "Referer":"https://www.moneycontrol.com/",
            'Sec-Ch-Ua-Mobile':"?0",
            "Sec-Ch-Ua-Platform":"Windows",
            'Sec-Fetch-Dest':"empty",
            "Sec-Fetch-Mode":"cors",
            "Sec-Fetch-Site":'same-site',
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        params = {
            "symbol": stocksymbol,
            "resolution": self.get_resolution(timeFrame),
            "from": fromdate,
            "countback":count_back,
            "to": todate,
            "currencyCode": "INR",
        }
        
        url = f"https://priceapi.moneycontrol.com/techCharts/indianMarket/stock/history"
        
        response = requests.get(url, headers=headers, params=params)
        # data = response.json()
        for epoch_seconds in response.json()['t']:
            print((datetime.utcfromtimestamp(epoch_seconds) +timedelta(hours=5.5)).strftime('%Y-%m-%d %H:%M:%S %Z'))
    
    def fetch_15min_data_at_market_close(self):
        pass
    
    def fetch_1d_data_at_market_close(self):
        pass
    
    def fetch_all_15min_data_for_stock(self):
        pass
    
    def fetch_all_1d_data_for_stock(self):
        pass
    
    def get_resolution(self, timeFrame):
        match timeFrame:
            case TimeFrame.FIVE_MINUTE:
                return "5"
            case TimeFrame.FIFTEEN_MINUTE:
                return "15"
            case TimeFrame.THIRTY_MINUTE:
                return "30"
            case TimeFrame.ONE_HOUR:
                return "60"
            case TimeFrame.ONE_DAY:
                return "1D"
            case default:
                return "1D"
   
class NseIndiaAPI(API):
    def __init__(self) -> None:
        self.deliveryPercentageUrl = "https://www.nseindia.com/api/historical/securityArchives?from=30-11-2022&to=30-11-2023&symbol=TATAPOWER&dataType=priceVolumeDeliverable&series=ALL"
        self.historicalDataUrl = "https://www.nseindia.com/api/historical/cm/equity?symbol=TATAPOWER"
        
    def historic_data(self):
        pass
        
    def fetch_15min_data_at_market_close(self):
        pass
    
    def fetch_1d_data_at_market_close(self):
        pass
    
    def fetch_all_15min_data_for_stock(self):
        pass
    
    def fetch_all_1d_data_for_stock(self):
        pass 