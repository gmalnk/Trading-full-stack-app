import PgConnection
from tokens import tokens
import time
from datetime import date
from datetime import timedelta
import yfinance as yf
from api import TradingAPI

api = TradingAPI()

# daily run for getting latest stock data for fifteen minute
def get_latest_candle_data(stock_token):
    try:
        startdate_fifteen = PgConnection.get_latest_date(stock_token, "FIFTEEN_MINUTE")
        end_date = date.today()
        
        if startdate_fifteen == 0:
            get_all_data_smart_api_fifteentf("FIFTEEN_MINUTE", stock_token)
        else:
            startdate_fifteen += timedelta(days=1)
            get_latest_candle_data_fifteen(startdate_fifteen.date(), end_date, stock_token, "FIFTEEN_MINUTE")
    except (Exception) as error:
        print("Failed at get_latest_candle_data method error message: ", error)
    finally:
        print(f"successfully fetched latest data for stock_token: {stock_token}")


# this method gets data between starttime and endtine for given stock and given time frame
def get_latest_candle_data_fifteen(startdate_fifteen, end_date, stock_token, time_frame):
    try:
        if startdate_fifteen > end_date:
            return
        if (end_date-startdate_fifteen).days <= 30:
            rows = api.historic_api(stock_token, time_frame, fromdate = startdate_fifteen.strftime("%Y-%m-%d %H:%M"), todate = end_date.strftime("%Y-%m-%d %H:%M"))
            PgConnection.add_past_data_from_smart_api(
                stock_token, time_frame, rows)
        else:
            print(f"stock {stock_token} has not been updated from last 30 days")
    except (Exception) as error:
        print("Failed at get_latest_candle_data_fifteen method error message: ", error)
    finally:
        print(f"successfully fetched latest data for stock_token: {stock_token} and time_frame : {time_frame}")


def get_all_data_smart_api_fifteentf(time_frame, stock_token):
    try:
        data = []
        for i in range(16):
            fromdate = (date.today()-timedelta(days=28*(i+1))).strftime("%Y-%m-%d %H:%M")
            todate = (date.today()-timedelta(days=28*(i))).strftime("%Y-%m-%d %H:%M")
            rows = api.historic_api(stock_token, time_frame, fromdate, todate)
            if (rows):
                data.extend(rows)
            time.sleep(.4)
        if len(data) == 0:
            print(f"not found data for fifteen min tf at smart api for stock_token {stock_token}")
            return
        print(f"successfully fetched all fifteen tf data for stock_token: {stock_token}")
        PgConnection.add_past_data_from_smart_api(
            stock_token, time_frame, data)
    except (Exception) as error:
        print("Failed at get_all_data_smart_api_fifteentf method error message: ", error)
    finally:
        print(f"done for stock_token : {stock_token}")


# not being used for getting the latest data
# def get_latest_candle_data_daily(symbol, startdate_daily, end_date, stock_token):
#     try:
#         symboldata = yf.download(
#             symbol, start=startdate_daily, end=end_date, interval='1d')
#         if symboldata.empty:
#             print(f"not found data for daily tf at yfinance for stock_token {stock_token}, startdate_daily {startdate_daily}, end_date [end_date]")
#             return
#         symboldata['Date'] = symboldata.index
#         PgConnection.add_past_data_from_yfinance(stock_token, "ONE_DAY", symboldata)
#     except (Exception) as error:
#         print("Failed at get_latest_candle_data_daily method error message: ", error)
#     finally:
#         print(f"successfully fetched latest daily tf data for stock_token: {stock_token}")


# this method get past candle data fetches all stocks past data in daily time frame
# this method uses yfinance to fetch data
# this method fetcheds data from past twenty years till today data
# passes this data to add past data method in pg connect module
# symboldata is a pandas data frame

# def get_all_candle_data_from_yfinance(stock_token, start_date, end_date):
#     try:
#         print(start_date, end_date)
#         symbol = tokens[stock_token] + ".NS"

#         # This line is responsible for fetching the data using yfinance in daily time frame
#         symboldata = yf.download(
#             symbol, start=start_date, end=end_date, interval="1d")
#         # if no data is fetched no need for further steps
#         if symboldata.size == 0:
#             return
#         # creating a new column called Date and it has the date of the candle data
#         symboldata['Date'] = symboldata.index
#         print("stock data collection done" + ":" + tokens[stock_token])
#         PgConnection.add_past_data_from_yfinance(stock_token, symboldata)
#     except (Exception) as error:
#         print("Failed at get_all_candle_data_from_yfinance method error message: ", error)
#     finally:
#         print(f"successfully fetched all daily tf data for stock_token: {stock_token}")
        




     

   