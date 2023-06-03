import psycopg2
import datetime
from tokens import tokens
from tokens import time_frames
from config import *
from Candle import Candle
import Utility
import time
from time import time
from datetime import timedelta
from datetime import datetime
from datetime import timezone
from datetime import date
import pandas as pd
import numpy
from psycopg2.extensions import register_adapter, AsIs

def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)

def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)

register_adapter(numpy.float64, addapt_numpy_float64)
register_adapter(numpy.int64, addapt_numpy_int64)

# this method uses environmnet variables and psycopg2 package to connect to postgres data base
def connect_to_database():
    return psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD
    )

# this method closes the connection at the end of the day
def close_connection():
    conn.close()

# this method executes the query 
def execute_query(query):
    cur.execute(query)
    
#  global variables used frequently for quering data from data base
conn = connect_to_database()
cur = conn.cursor()

# this method inserts ticks data into ticks_data table in historicdata data base
# this method gets triggered when the on_data method gets a message

def add_ticks_data(token, data):
    try:
        query = f"INSERT INTO ticks_data (token, time_stamp, ltp) values({token}, '{datetime.fromtimestamp(data['exchange_timestamp']/1000.0).strftime('%Y-%m-%d %H:%M')}',{data['last_traded_price']/100.0})"
        cur.execute(
            """INSERT INTO ticks_data (token, time_stamp, ltp) values(%s, %s, %s)""", [token, datetime.fromtimestamp(data['exchange_timestamp']/1000.0).strftime('%Y-%m-%d %H:%M'), data['last_traded_price']/100.0])
        conn.commit()
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into ticks_data table error message:", error)

# this method takes is run on a periodic basis when we want to get the candle data in real time
# this method parameters are stocken tocken, time_frame, start time , end time 
# token is a unique number for a stock
# time frame is the candle time frame
# this method returns a candle of specified time frame with specified start time, if  endtime is not give then only one candle is returned
# if end time is specified than u get all the candles of specified time frame forming between start time and end time
# all the candles returned are formed using the real time ticks data

def get_ticks_candles(token, time_frame, start_time, end_time=None):
    try:
        time_frame = convert_timeframe(time_frame)
        if end_time == None:
            end_time = start_time
            start_time = end_time - timedelta(minutes=no_of_minutes(time_frame))
        cur = conn.cursor()
        cur.execute(
            f"select * from ticks_data where token = {token} and time_stamp >= '{start_time} and time_stamp <= '{end_time}'")
        rows = cur.fetchall()
        rows = convert_ltp_to_ohlc(time_frame, rows)
        candles = []
        for i in rows.index:
            candles.append(Candle(
                0, 0, token, i, rows['open'][i], rows['high'][i], rows['low'][i], rows['close'][i], ""))
        return candles
    except (Exception, psycopg2.Error) as error:
        print("Failed at get candles from ticks_data table error message:", error)

# this method is responsible for storing each day data, of all stocks, everyday
# data is a array of array having elements as follows symbol_token, time_stamp, open_price, high_price, low_price, close_price, high_low

def add_market_data_daily(data):
    try:
        cur = conn.cursor()
        for row in data:
            cur.execute("""INSERT INTO daily_data (symbol_token, time_stamp, open_price, high_price, low_price, close_price, high_low) values (%s,%s,%s,%s,%s,%s,'')""", [
                        row[0], row[1], row[2], row[3], row[4], row[5]])
            conn.commit()
    except (Exception, psycopg2.Error) as error:
        print("Failed at add_market_data_daily method (error message):", error)

# this method is responsible for inserting all the past data of a stock
# parameter data is a pandas dataframe it has columns Date, Open, High, Low, Close respectively from smart_api and yfianance

def add_past_data_from_yfinance(stock_token, data):
    try:
        cur = conn.cursor()
        counter = 0
        for i in data.index:
            date = data['Date'][i].strftime("%Y-%m-%d %H:%M:%S")
            query = f"INSERT INTO dailytf_data (token, time_stamp, open_price, high_price, low_price, close_price, index) values ({stock_token},'{date}',{data['Open'][i]},{data['High'][i]},{data['Low'][i]},{data['Close'][i]},{counter})"
            cur.execute(query)
            counter = counter + 1
            conn.commit()
    except (Exception, psycopg2.Error) as error:
        print("Failed at add_past_data_from_yfinance method (error message):", error)

def add_past_data_from_smart_api(stock_token, time_frame, data):
    try:
        table = get_table(time_frame)
        cur = conn.cursor()
        counter = 0
        for row in data:
            row[0] = row[0].replace("T", " ")
            cur.execute(
                f"INSERT INTO {table} (token, time_stamp, open_price, high_price, low_price, close_price, index) values ({stock_token}, '{row[0]}', {row[1]}, {row[2]}, {row[3]}, {row[4]}, {counter})")
            counter = counter + 1
            conn.commit()
    except (Exception, psycopg2.Error) as error:
        print(f"failed at add_past_data_from_smart_api method failed for stock_token : {stock_token} error message: ", error)

# this method is used for initializing highs and lows in the highlow_data table
def initialize_high_low(stock_token, time_frame):
    try:
        cur = conn.cursor()
        candles = fetch_candles(stock_token, time_frame)
        candles = Utility.find_highs_and_lows(candles)
        for candle in candles:
            cur.execute(
                """insert into highlow_data (index, token, time_stamp, open_price, high_price, low_price, close_price, high_low, tf) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)""", [candle.Index, stock_token, candle.Date, candle.Open, candle.High, candle.Low, candle.Close, candle.High_Low, time_frame])
            conn.commit()
        print("inserted ***********************************")
    except (Exception, psycopg2.Error) as error:
        print("Failed at initialize_high_low method error message: ", error)

# this method is used for analysis of highs and lows in the highlow_data table and form trendlines and store them 
def get_trendLines(stock_token, time_frame):
    try:
        highs = fetch_highs(stock_token, time_frame)
        lows = fetch_lows(stock_token, time_frame)
        priceData = Utility.PriceData(highs, lows)
        trendlines = priceData.TrendlinesToDraw
        for trendline in trendlines:
            query = f"insert into trendline_data (token, tf, slope, intercept, startdate, enddate, hl, index1, index2, index) values ({stock_token}, '{time_frame}', {trendline[0][1]}, {trendline[0][2]},'{trendline[0][0][0].Date}','{trendline[0][0][-1].Date}','{trendline[1]}' ,{trendline[0][0][0].Index},{trendline[0][0][-1].Index},500)"
            cur.execute(query)
            conn.commit()
    except (Exception, psycopg2.Error) as error:
        print("Failed at get trendlines method  error message : ", error)
    finally:
        print("generated trendlines successfully for ",
              tokens[stock_token], " stock")

# this method fetches high candles for given stock, for given time frame
def fetch_highs(stock_token, time_frame):
    try:
        start_time = get_starttime_of_analysis(time_frame)
        query = f"select * from highlow_data where token = {stock_token} and tf = '{time_frame}' and high_low like 'high%' and time_stamp > '{start_time.strftime('%Y-%m-%d %H:%M')}' order by index asc"
        cur.execute(query)
        rows = cur.fetchall()
        candles = []
        for row in rows:
            candles.append(
                Candle(0, row[1], row[2], row[3], row[4], row[5], row[6], row[7], ""))
        return candles
    except (Exception, psycopg2.Error) as error:
        print("Failed at fetch highs error mesage: ", error)
    finally:
        print("fetched highs successfully for ", tokens[stock_token], " stock")

# this method fetches low candles for given stock, for given time frame
def fetch_lows(stock_token, time_frame):
    try:
        start_time = get_starttime_of_analysis(time_frame)
        query = f"select * from highlow_data where token = {stock_token} and tf = '{time_frame}' and high_low like '%low' and time_stamp > '{start_time.strftime('%Y-%m-%d %H:%M')}' order by index asc"
        cur.execute(query)
        rows = cur.fetchall()
        candles = []
        for row in rows:
            candles.append(
                Candle(0, row[1], row[2], row[3], row[4], row[5], row[6], row[7], ""))
        return candles
    except (Exception, psycopg2.Error) as error:
        print("Failed at fetch highs error message: ", error)
    finally:
        print("fetched lows successfully for ", tokens[stock_token], " stock")

# this method fetches all candles for given stock, for given time frame if limit is not specified 
# if limit is provided then latest x no of candles are only returned
def fetch_candles(stock_token, time_frame, limit=0):
    try:
        table = get_table(time_frame)
        start_time = get_starttime_of_analysis(time_frame)
        query = f"select * from {table} where token = {stock_token} and time_stamp >= '{start_time.strftime('%Y-%m-%d %H:%M')}' order by index desc"
        if limit > 0:
            query += f" limit {limit}"
        cur.execute(query)
        rows = cur.fetchall()
        rows.reverse()
        rows = convert_data_timeframe(time_frame, rows)
        if rows.empty:
            return None
        candles = []
        counter = 0
        for i in rows.index:
            candles.append(
                Candle(rows['id'][i], counter, rows['token'][i], rows['time_stamp'][i], rows['open_price'][i], rows['high_price'][i], rows['low_price'][i], rows['close_price'][i], ""))
            counter += 1
        return candles
    except (Exception, psycopg2.Error) as error:
        print("Failed to fetch candles error message: ", error)
    finally:
        print("fetched candles successfully for ",
              tokens[stock_token], " stock for ", time_frame, " timeframe")

# we dont analyse all the data for all time frames, we limit out data for analysis hence 
# this method provides the start time of the analysis based on the time frame
def get_starttime_of_analysis(time_frame):
    match time_frame:
        case 'FIFTEEN_MINUTE':
            return date.today()-timedelta(days=30)
        case 'THIRTY_MINUTE':
            return date.today()-timedelta(days=60)
        case 'ONE_HOUR':
            return date.today()-timedelta(weeks=14)
        case 'TWO_HOUR':
            return date.today()-timedelta(weeks=28)
        case 'FOUR_HOUR':
            return date(date.today().year-1, date.today().month, date.today().day)
        case 'ONE_DAY':
            return date(date.today().year-2, date.today().month, date.today().day)
        case 'ONE_WEEK':
            return date(date.today().year-20, date.today().month, date.today().day)
        case 'ONE_MONTH':
            return date(date.today().year-20, date.today().month, date.today().day)
        case default:
            return date.today()

# we have stored fifteen minute data in fifteentf_data table in historicdata data base
# we have stored daily data in dailytf_data table in historicdata data base
# all the data up to four hour is created using the fifteentf_data table 
# all the data above one day is created using the dailytf_data table 
# this method provides which data table to use based on time frame
def get_table(time_frame):
    match time_frame:
        case 'FIFTEEN_MINUTE':
            return "fifteentf_data"
        case 'THIRTY_MINUTE':
            return "fifteentf_data"
        case 'ONE_HOUR':
            return "fifteentf_data"
        case 'TWO_HOUR':
            return "fifteentf_data"
        case 'FOUR_HOUR':
            return "fifteentf_data"
        case 'ONE_DAY':
            return "dailytf_data"
        case 'ONE_WEEK':
            return "dailytf_data"
        case 'ONE_MONTH':
            return "dailytf_data"
        case default:
            return "dailytf_data"

# after fetching data from data base we convert it into required time frame using this method
# it uses pandas resample function with offset and dropna function to remove NAN values
def convert_data_timeframe(time_frame, rows):
    try:
        off_set = get_offset(time_frame)
        df = pd.DataFrame(rows, columns=['id', 'index', 'token', 'time_stamp',
                        'open_price', 'high_price', 'low_price', 'close_price'])
        df['Date'] = df['time_stamp']
        df = df.set_index('Date')
        if time_frame == "ONE_DAY" or time_frame == "FIFTEEN_MINUTE":
            return df
        df = df.resample(convert_timeframe(time_frame), offset=off_set).apply(OHLC)
        return df.dropna()
    except (Exception, psycopg2.Error) as error:
        print("failed at convert_data_timeframe method error mesage: ",error)

# method provides offset based on time frame 
# off set of 9 hours 15 minutes is provided for time frames below one day
# off set of 0 hours 0 minutes is provided for time frames above four hours
def get_offset(time_frame):
    match time_frame:
        case 'FIFTEEN_MINUTE':
            return '9h15min'
        case 'THIRTY_MINUTE':
            return '9h15min'
        case 'ONE_HOUR':
            return '9h15min'
        case 'TWO_HOUR':
            return '9h15min'
        case 'FOUR_HOUR':
            return '9h15min'
        case 'ONE_DAY':
            return '0h0min'
        case 'ONE_WEEK':
            return '0h0min'
        case 'ONE_MONTH':
            return '0h0min'
        case default:
            return '0h0min'

# This method takes api timeframe example : "ONE_DAY", "FIFTEEN_MINUTE"
# returns pandas timeframe example : "15T", "1H", "D", "W", "M"
def convert_timeframe(time_frame):
    match time_frame:
        case 'FIFTEEN_MINUTE':
            return "15T"
        case 'THIRTY_MINUTE':
            return "30T"
        case 'ONE_HOUR':
            return "1H"
        case 'TWO_HOUR':
            return "2H"
        case 'FOUR_HOUR':
            return "4H"
        case 'ONE_DAY':
            return "D"
        case 'ONE_WEEK':
            return "W"
        case 'ONE_MONTH':
            return "M"
        case default:
            return "D"

# this method returns no of minutes in a time frame
def no_of_minutes(time_frame):
    match time_frame:
        case 'FIFTEEN_MINUTE':
            return 15
        case 'THIRTY_MINUTE':
            return 30
        case 'ONE_HOUR':
            return 60
        case 'TWO_HOUR':
            return 120
        case 'FOUR_HOUR':
            return 240
        case default:
            return 0

# this method converts ltp  data to pandas ohlc data
def convert_ltp_to_ohlc(time_frame, rows):
    try:
        df = pd.DataFrame(rows, columns=['id', 'token', 'time_stamp', 'ltp'])
        df['Date'] = df['time_stamp']
        df = df.set_index('Date')
        df = df['ltp'].resample(time_frame).ohlc(_method='ohlc')
        return df
    except (Exception, psycopg2.Error) as error:
        print("failed at convert_data_timeframe method error mesage: ",error)

# this method is run repitatively, its functionality is to add candles to data base tables in real time using real time ticks data
def data_handler(time_frame, start_time):
    try:
        stock_token = '18944'
        candles = fetch_candles(stock_token, time_frame, 10)
        candles.append(get_ticks_candles(stock_token, time_frame, start_time))
        candles = Utility.find_highs_and_lows(candles)
        for candle in candles:
            cur.execute(
                """insert into highlow_data (index, token, time_stamp, open_price, high_price, low_price, close_price, high_low, tf) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)""", [candle.Index, stock_token, candle.Date, candle.Open, candle.High, candle.Low, candle.Close, candle.High_Low, time_frame])
            conn.commit()
        print("inserted ***********************************")
    except (Exception, psycopg2.Error) as error:
        print("failed at data_handler error mesage: ",error)
    

def run_trendline_generator():
    try:
        for stock_token in tokens:
            for time_frame in time_frames:
                initialize_high_low(stock_token, time_frame)
                get_trendLines(stock_token,time_frame)
    except (Exception, psycopg2.Error) as error:
        print("failed at run_trendline_generator method error mesage: ",error)


# FRONTEND API METHODS
# this method provides stock data, for given stock token, for given time frame, for plotting in UI
def api_get_stock_data(stock_token, time_frame):
    try:
        data = []
        table = get_table(time_frame)
        query = f"select * from {table} where token = {stock_token} order by index asc"
        cur.execute(query)
        rows = cur.fetchall()
        rows = convert_data_timeframe(time_frame, rows)
        for i in rows.index:
            data.append({
                "time": int(rows['time_stamp'][i].replace(tzinfo=timezone.utc).timestamp()),
                "open":rows['open_price'][i],
                "high":rows['high_price'][i],
                "low":rows['low_price'][i],
                "close":rows['close_price'][i]
                })
        data  = {"stockdata" : data}
        return data
    except (Exception, psycopg2.Error) as error:
        print(f"failed while responding api call in method api_get_stock_data for stock_token: {stock_token} and time_frame : {time_frame} error mesage: ",error)

def api_get_trendline_data(stock_token, time_frame):
    try:
        data = []
        query = f"select * from trendline_data where token = {stock_token} and tf = '{time_frame}'"
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            data.append([{
                "time": int(row[5].replace(tzinfo=timezone.utc).timestamp()),
                "value" :row[3]*row[8]+row[4]
                },
                   {
                "time": int(row[6].replace(tzinfo=timezone.utc).timestamp()),
                "value" :row[3]*row[9]+row[4]
                }])
        data  = {"trendlinedata" : data}
        return data
    except (Exception, psycopg2.Error) as error:
        print(f"failed while responding api call in method api_get_trendline_data for stock_token: {stock_token} and time_frame : {time_frame} error mesage: ",error)


