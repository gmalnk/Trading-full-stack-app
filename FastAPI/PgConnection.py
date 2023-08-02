import psycopg2
import math
from FastAPI.fast_api_lib_if import *
from FastAPI.Constants import *
from FastAPI.config import *
from FastAPI.Candle import Candle
from FastAPI.Utility import *
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
        query = f"INSERT INTO ticks_data (symbol_token, time_stamp, ltp) values({token}, '{datetime.fromtimestamp(data['exchange_timestamp']/1000.0).strftime('%Y-%m-%d %H:%M:%S')}',{data['last_traded_price']/100.0})"
        cur.execute(
            """INSERT INTO ticks_data (symbol_token, time_stamp, ltp) values(%s, %s, %s)""", [token, datetime.fromtimestamp(data['exchange_timestamp']/1000.0).strftime('%Y-%m-%d %H:%M:%S'), data['last_traded_price']/100.0])
        conn.commit()
    except (Exception) as error:
        real_time_logger.error("Failed to insert record into ticks_data table error message:" + str(error))

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
    except (Exception) as error:
        trades_executer_logger.error("Failed at get candles from ticks_data table error message:" + str(error))

# this method is responsible for storing each day data, of all stocks, everyday
# data is a array of array having elements as follows symbol_token, time_stamp, open_price, high_price, low_price, close_price, high_low

def add_market_data_daily(data):
    try:
        cur = conn.cursor()
        for row in data:
            cur.execute("""INSERT INTO daily_data (symbol_token, time_stamp, open_price, high_price, low_price, close_price, high_low) values (%s,%s,%s,%s,%s,%s,'')""", [
                        row[0], row[1], row[2], row[3], row[4], row[5]])
            conn.commit()
    except (Exception) as error:
        daily_logger.error("Failed at add_market_data_daily method (error message):" + str(error))

# this method is responsible for inserting all the past data of a stock
# parameter data is a pandas dataframe it has columns Date, Open, High, Low, Close respectively from smart_api and yfianance

def add_past_data_from_yfinance(stock_token, data):
    try:
        table = get_table("ONE_DAY")
        counter = get_latest_index(stock_token, 'ONE_DAY')+1
        query = f"INSERT INTO {table} (token, time_stamp, open_price, high_price, low_price, close_price, index) values "
        for i in data.index:
            date = data['Date'][i].strftime("%Y-%m-%d %H:%M:%S")
            query += f"({stock_token},'{date}',{data['Open'][i]},{data['High'][i]},{data['Low'][i]},{data['Close'][i]},{counter}),"
            counter = counter + 1
        execute_query(query[:-1])
        conn.commit()
    except (Exception) as error:
        daily_logger.error("Failed at add_past_data_from_yfinance method (error message):" + str(error))

def add_past_data_from_yfinance_once(data):
    try:
        for token in tokens:
            query = f"INSERT INTO {dailytf_table} (token, time_stamp, open_price, high_price, low_price, close_price, index) values "
            counter = 1
            symbol = tokens[token]+".NS"
            for i in data.index:
                date = i.strftime("%Y-%m-%d %H:%M:%S")
                if math.isnan(data[(symbol, 'Open')][i]) or math.isnan(data[(symbol, 'High')][i]) or math.isnan(data[(symbol, 'Low')][i]) or math.isnan(data[(symbol, 'Close')][i]):
                    continue
                query += f"({token},'{date}',{data[(symbol, 'Open')][i]},{data[(symbol, 'High')][i]},{data[(symbol, 'Low')][i]},{data[(symbol, 'Close')][i]},{counter}),"
                counter = counter + 1
            daily_logger.info(f"symbol: {symbol} counter: {counter}")
            daily_logger.info("started adding data to database...")
            execute_query(query[:-1])
            conn.commit()   
    except (Exception) as error:
        daily_logger.error("Failed at add_past_data_from_yfinance method (error message):" + str(error))
    finally:
        daily_logger.info("succesfully fetched all the data of stocks in daily time frame at once from y finance")

def add_latest_data_from_yfinance_once(data):
    try:
        if data.empty:
            daily_logger.info("data provided to add_latest_data_from_yfinance_once is empty")
            return
        query = f"INSERT INTO {dailytf_table} (token, time_stamp, open_price, high_price, low_price, close_price, index) values "
        for token in tokens:
            counter = get_latest_index(token, "ONE_DAY") + 1
            symbol = tokens[token]+".NS"
            for i in data.index:
                date = i.strftime("%Y-%m-%d %H:%M:%S")
                if math.isnan(data[(symbol, 'Open')][i]) or math.isnan(data[(symbol, 'High')][i]) or math.isnan(data[(symbol, 'Low')][i]) or math.isnan(data[(symbol, 'Close')][i]):
                    continue
                query += f"({token},'{date}',{data[(symbol, 'Open')][i]},{data[(symbol, 'High')][i]},{data[(symbol, 'Low')][i]},{data[(symbol, 'Close')][i]},{counter}),"
                counter = counter + 1
        execute_query(query[:-1])
        conn.commit()   
    except (Exception) as error:
        daily_logger.error("Failed at add_latest_data_from_yfinance_once method (error message):" + str(error))
    finally:
        daily_logger.info("succesfully fetched all latest data of stocks in daily time frame at once from y finance")

def add_past_data_from_smart_api(stock_token, time_frame, data):
    try:
        if data == None:
            return
        data.sort()
        table = get_table(time_frame)
        counter = get_latest_index(stock_token, time_frame)+1
        query = f"INSERT INTO {table} (token, time_stamp, open_price, high_price, low_price, close_price, index) values "
        for row in data:
            row[0] = row[0].replace("T", " ")
            query += f"({stock_token}, '{row[0]}', {row[1]}, {row[2]}, {row[3]}, {row[4]}, {counter}),"
            counter = counter + 1
        execute_query(query[:-1])
        conn.commit()
    except (Exception) as error:
        daily_logger.error(f"failed at add_past_data_from_smart_api method failed for stock_token : {stock_token} error message: " + str(error))
    finally:
        daily_logger.info(f"successfully added data for stock : {stock_token} for time frame : {time_frame}")

# this method is used for initializing highs and lows in the highlow_data table
def initialize_high_low(stock_token, time_frame):
    try:
        index = get_latest_highlow_index(stock_token, time_frame)
        start_time = datetime.min
        if index == 0:
            start_time = get_starttime_of_analysis(time_frame)
        candles = fetch_candles(stock_token, time_frame, index = index-Numbers.FOUR, start_time=start_time)
        highlow_candles = find_highs_and_lows(candles)
        if len(highlow_candles) > 0 :
            query = "insert into highlow_data (index, token, time_stamp, open_price, high_price, low_price, close_price, high_low, tf) values"
            for candle in highlow_candles:
                query += f" ({candle.Index}, {stock_token}, '{candle.Date}', {candle.Open}, {candle.High}, {candle.Low}, {candle.Close}, '{candle.High_Low}', '{time_frame}'),"
            execute_query(query[:-1])
            conn.commit()
            daily_logger.info("inserted highs and lows ***********************************")
            return 1
        daily_logger.info("highlow_candles length is zero")
        return 0
    except (Exception) as error:
        daily_logger.error("Failed at initialize_high_low method error message: " + str(error))

# this method is used for analysis of highs and lows in the highlow_data table and form trendlines and store them 
def get_trendLines(stock_token, time_frame):
    try:
        highs = fetch_highs(stock_token, time_frame)
        lows = fetch_lows(stock_token, time_frame)
        index = Numbers.MIN
        if not (highs and lows):
            return
        if highs:
            index = min(index, highs[0].Index)
        if lows:
            index = min(index, lows[0].Index)
        candles = fetch_candles(stock_token = stock_token, time_frame = time_frame, index = index-Numbers.TEN)
        priceData = PriceData(highs, lows, candles)
        trendlines = priceData.TrendlinesToDraw
        update_trendlines(stock_token, time_frame, trendlines)
    except (Exception) as error:
        daily_logger.error("Failed at get trendlines method  error message : " + str(error))
    finally:
        daily_logger.info("generated trendlines successfully for " + tokens[stock_token] + " stock")
        
# this method updates trendlines in the database       
def update_trendlines(stock_token, time_frame, trendlines):
    try:
        latest_index = get_latest_index(stock_token, time_frame)        
        query = ''
        if len(trendlines) > 0:
            for trendline in trendlines:
                if (trendline.Slope == None):
                    continue
                query += f"""UPDATE trendline_data 
                            SET 
                                slope = {trendline.Slope},
                                intercept = {trendline.Intercept},
                                startdate = '{trendline.Candles[0].Date}',
                                enddate = '{trendline.Candles[-1].Date}',
                                index1 = '{trendline.Candles[0].Index}',
                                index2 = '{trendline.Candles[-1].Index}',
                                index = {latest_index},
                                connects = {trendline.NoOfPoints}
                            WHERE token = {stock_token} AND
                                tf = '{time_frame}' AND
                                hl = '{trendline.HL}';"""
            execute_query(query)
            conn.commit()
    except (Exception) as error:
        daily_logger.error("Failed at update_trendlines method  error message : " + str(error))
    finally:
        daily_logger.info("updated trendlines successfully for " + tokens[stock_token] + " stock")
        


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
                Candle(0, row[1], row[2], row[3], row[4], row[5], row[6], row[7],row[8]))
        return candles
    except (Exception) as error:
        daily_logger.error("Failed at fetch highs error mesage: " + str(error))
    finally:
        daily_logger.info("fetched highs successfully for " + tokens[stock_token] + " stock")

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
                Candle(0, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return candles
    except (Exception) as error:
        daily_logger.error("Failed at fetch highs error message: " + str(error))
    finally:
        daily_logger.info("fetched lows successfully for " + tokens[stock_token] + " stock")

# this method fetches all candles for given stock, for given time frame if limit is not specified 
# if limit is provided then latest x no of candles are only returned
def fetch_candles(stock_token, time_frame, limit=0, index = 0, start_time = datetime.min):
    try:
        table = get_table(time_frame)
        query = f"select * from {table} where token = {stock_token} order by index desc "
        if limit > 0:
            query += f"limit {limit}"
        cur.execute(query)
        rows = cur.fetchall()
        rows.reverse()
        rows = convert_data_timeframe(time_frame, rows)
        if rows.empty:
            return None
        candles = []
        candle_index = 1
        for i in rows.index:
            candles.append(
                Candle(rows['id'][i], candle_index, rows['token'][i], rows['time_stamp'][i], rows['open_price'][i], rows['high_price'][i], rows['low_price'][i], rows['close_price'][i], ""))
            candle_index += 1
        if index > 0:
            candles = [x for x in candles if x.Index >= index]
        if start_time != datetime.min:
            candles = [x for x in candles if datetime.strptime(x.Date,'%Y-%m-%d %H:%M') >= start_time]
        return candles
    except (Exception) as error:
        daily_logger.error("Failed to fetch candles error message: " + str(error))
    finally:
        daily_logger.info("fetched candles successfully for " + tokens[stock_token] + " stock for " + time_frame + " timeframe")

# this method's functionality is to get latest candle's index for given stock and give time_frame
def get_latest_index(stock_token, time_frame):
    try:
        table = get_table(time_frame)
        query = f"select max(index) from {table} where token = {stock_token}"
        execute_query(query)
        rows = cur.fetchall()
        if rows[0][0] == None:
             return 0
        return rows[0][0]
    except (Exception) as error:
        daily_logger.error(f"failed at get_latest_index method for stock_token: {stock_token} and time_frame : {time_frame} error mesage: " + str(error))

# this method's functionality is to get latest candle's date for given stock and give time_frame
# used when fetching latest candles data
def get_latest_date(stock_token, time_frame):
    try:
        table = get_table(time_frame)
        query = f"select max(time_stamp) from {table} where token = {stock_token}"
        execute_query(query)
        rows = cur.fetchall()
        if rows[0][0] == None:
             return 0
        return rows[0][0]
    except (Exception) as error:
        daily_logger.error(f"failed at get_latest_date method for stock_token: {stock_token} and time_frame : {time_frame} error mesage: " + str(error))

# this method's functionality is to get latest high/low candle's index for given stock and give time_frame
def get_latest_highlow_index(stock_token, time_frame):
    try:
        query = f"select max(index) from highlow_data where token = {stock_token} and tf = '{time_frame}'"
        execute_query(query)
        rows = cur.fetchall()
        if rows[0][0] == None:
             return 0
        return rows[0][0]
    except (Exception) as error:
        daily_logger.error(f"failed at get_latest_index method for stock_token: {stock_token} and time_frame : {time_frame} error mesage: " + str(error))

# this method's functionality is to initialize trendline_data table with initial values
def initialize_trendline_data_table():
    try:
        # query = 'DROP TABLE if exists trendlinecandels_data; DROP TABLE if exists trendline_data;'
        # query +='''CREATE TABLE if not exists trendline_data(
        #             id BIGSERIAL PRIMARY KEY,
        #             token INT NOT NULL,
        #             tf varchar(14),
        #             slope REAL NOT NULL,
        #             intercept REAL NOT NULL,
        #             startdate timestamptz NOT NULL,
        #             enddate timestamptz NOT NULL,
        #             hl varchar(2) NOT NULL,
        #             index1 INT NOT NULL,
        #             index2 INT NOT NULL,
        #             index Int Not Null
        #         );'''
        # execute_query(query)
        query = 'INSERT INTO trendline_data (token, tf, slope, intercept, startdate, enddate, hl, index1, index2, index) values '
        date_str = date.today().strftime('%Y-%m-%d %H:%M')
        for stock_token in tokens:
            for time_frame in time_frames:
                query += f"""({stock_token}, '{time_frame}',{0},{-1},'{date_str}', '{date_str}', 'H', {0},{0},{0}), 
                             ({stock_token}, '{time_frame}',{0},{-1},'{date_str}', '{date_str}', 'L', {0},{0},{0}),"""
        execute_query(query[:-1])
        conn.commit()
    except (Exception) as error:
        print(f"failed at initialize_trendline_data_table method error mesage: " + str(error))
    finally:
        print("succesfully initialized trendline_data table")

# this method increments the index of the trendlines for given timeframe
# used repetatively for every new candle formed in any time frame in real time
def increment_index(time_frame):
    try:
        query = f"""UPDATE trendline_data
                    SET index = index +1
                    WHERE tf= '{time_frame}'"""
        execute_query(query)
        conn.commit()
    except (Exception) as error:
        trades_executer_logger.error("Failed at increment_index method error mesage: " + str(error))
    finally:
        daily_logger.info(f"succesfully incremented trendline_data table index for given time_frame {time_frame}")
  
#   this is a one time use method which initializes stock details table
def initialize_stocks_details_table():
    try:
        query = """INSERT INTO stock_details
        (token, name, category) values
        """
        for token in tokens:
            query += f"({token}, '{tokens[token]}', ''),"
        execute_query(query[:-1])
        conn.commit()
    except (Exception) as error:
        print("failed at initialize_stocks_details_table method error mesage: ",error)


def execute_trades_on_candle_close(api, time_frame, start_time):
    try:
        trades_executed = []
        end_time = start_time + timedelta(minutes=no_of_minutes(time_frame))
        trades = get_trades(time_frame, start_time, end_time)
        for trade in trades:
            if ( trade[13] > trade[7] * trade[9] + trade[8] ):
                api.place_order(
                    variety="ROBO",
                    tradingsymbol=tokens[str(trade[0])]+"-EQ",
                    symboltoken=trade[0],
                    transactiontype= "BUY" if trade[2] == "H" else "SELL",
                    ordertype="LIMIT",
                    producttype="INTRADAY",
                    duration="DAY",
                    price=trade[13],
                    squareoff=abs(trade[4]-trade[13]),
                    stoploss=abs(trade[13]-trade[5]),
                    quantity= trade[6]
                )
                trades_executed.append(trade[0])
        for trade in trades_executed:
            trades_executer_logger.info(f"trade executed {trade}")
        increment_index(time_frame)
        update_trades(trades_executed)
    except (Exception) as error:
        trades_executer_logger.error("Failed at execute_trades method error mesage: " + str(error))

def update_trades(orders_placed):
    try:
        if orders_placed:
            query ="""
                    UPDATE  trades_data 
                    set status = 'DONE'
                    Where token in ("""
            for token in orders_placed:
                query += f" {token},"
            query = query[:-1]+");"
            execute_query(query)
            conn.commit()
    except (Exception) as error:
        trades_executer_logger.error("Failed at get_trades method error mesage: " + str(error))

def get_trades(time_frame, start_time, end_time):
    try:
        query = f"""
        SELECT trades_data.token, trades_data.tf, trades_data.direction, trades_data.entry_condition, trades_data.tp, trades_data.sl, trades_data.quantity, trendline_data.slope, trendline_data.intercept, trendline_data.index, ohlc_data.open, ohlc_data.high, ohlc_data.low, ohlc_data.close
        FROM trades_data
        INNER JOIN trendline_data
        ON trades_data.token = trendline_data.token and trades_data.tf = trendline_data.tf and trades_data.direction = trendline_data.hl
        INNER JOIN
            (
               SELECT DISTINCT
                    symbol_token,
                    FIRST_VALUE(ltp) OVER w AS open,
                    MAX(ltp) OVER w AS high,
                    MIN(ltp) OVER w AS low,
                    LAST_VALUE(ltp) OVER w AS close
                FROM
                    ticks_data
                WHERE
                    time_stamp >= '{start_time.strftime('%Y-%m-%d %H:%M:%S')}'
                    AND time_stamp <= '{end_time.strftime('%Y-%m-%d %H:%M:%S')}'
                WINDOW w AS (PARTITION BY symbol_token ORDER BY time_stamp ROWS BETWEEN UNBOUNDED preceding AND UNBOUNDED FOLLOWING)
            ) as ohlc_data
        ON trades_data.token = ohlc_data.symbol_token
        where trades_data.status = 'TODO' and trades_data.tf = '{time_frame}' and trades_data.entry_condition like '%Close%';
        """
        execute_query(query)
        rows = cur.fetchall()
        return rows
    except (Exception) as error:
        trades_executer_logger.error("Failed at get_trades method error mesage: " + str(error))






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
        # if rows.empty :
        #     return {"stockData" : data}
        for i in rows.index:
            data.append({
                "time": int(rows['time_stamp'][i].replace(tzinfo=timezone.utc).timestamp()),
                "open":rows['open_price'][i],
                "high":rows['high_price'][i],
                "low":rows['low_price'][i],
                "close":rows['close_price'][i]
                })
        data  = {"stockData" : data}
        return data
    except (Exception) as error:
        print(f"failed while responding api call in method api_get_stock_data for stock_token: {stock_token} and time_frame : {time_frame} error mesage: ",error)

# this method adds a new trade data
def add_trade_data(tradedetails): 
    try:
        entry_condition = ""
        if tradedetails["tradeOnCandleClose"] :
            entry_condition += "Close"
        if tradedetails["tradeOnCandleOpen"] :
            entry_condition += "Open"
        query = f"""INSERT INTO trades_data
        (token, tf, status, direction, entry_condition, tp, sl, quantity)
        values
        (
            {tradedetails['stockToken']},
            '{tradedetails['timeFrame']}',
            'TODO',
            '{tradedetails["tradeDirection"]}',
            '{entry_condition}',
            {tradedetails["takeProfit"]},
            {tradedetails["stopLoss"]},
            {tradedetails["numOfShares"]}        
        )
        """
        execute_query(query)
        conn.commit()
    except (Exception) as error:
        print(f"failed while responding api call in method add_trade_data for stock_token: {tradedetails['stockToken']} and time_frame : {tradedetails['timeFrame']} error mesage: ",error)
    
# this method gets all stock details
def get_stock_details():
    query = "select * from stock_details;"
    execute_query(query)
    rows = cur.fetchall()
    stock_details = []
    for row in rows:
        stock_details.append({
        "token": row[1],
        "name":row[2],
        "category": row[3]})
    # print(stock_details)
    # print(stock_details[474]["name"])
    return stock_details

# this method provides trendline data, for given stock token, for given time frame, for plotting in UI
def api_get_trendline_data(stock_token, time_frame):
    try:
        data = []
        query = f"select * from trendline_data where token = {stock_token} and tf = '{time_frame}'"
        execute_query(query)
        rows = cur.fetchall()
        data = []
        hl = ""
        for row in rows:
            slope = row[3]
            intercept = row[4]
            if not(row[3] == 0 and row[4] == -1):
                data.append([{
                    "time": int(row[5].replace(tzinfo=timezone.utc).timestamp()),
                    "value" :slope*row[8]+intercept
                    },
                    {
                    "time": int(row[6].replace(tzinfo=timezone.utc).timestamp()),
                    "value" :slope*row[9]+intercept
                    }])
                hl += row[7]
        data  = {"trendlineData" : data, "linesData":hl}
        return data
    except (Exception) as error:
        print(f"failed while responding api call in method api_get_trendline_data for stock_token: {stock_token} and time_frame : {time_frame} error mesage: ",error)

# this method gets all the trades data 
def get_all_trades():
    query = """SELECT trades_data.id, stock_details.name, trades_data.tf, trades_data.status, trades_data.direction, trades_data.quantity, trades_data.bp, trades_data.sp, trades_data.tp, trades_data.sl,trades_data.pl 
                FROM stock_details 
                INNER JOIN trades_data  
                ON stock_details.token = trades_data.token"""
    execute_query(query)
    rows = cur.fetchall()
    tradesData = []
    for row in rows:
        tradesData.append(
            {
                "id":row[0],
                "stockName":row[1],
                "timeFrame":row[2],
                "status":row[3],
                "direction":"Long" if row[4] =="H" else "Short",
                "quantity": row[5],
                "entryPrice":row[6] if row[6] != None else "---",
                "exitPrice":row[7] if row[7] != None else "---",
                "takeProfit":row[8],
                "stopLoss":row[9],
                "p&l":row[10] if row[10] != None else "---"
            }
        )
    return {"tradesData":tradesData}

# this method deletes a trade based on the given id
def delete_trade(id):
    query = f"delete from trades_data where id = {id}"
    execute_query(query)
    conn.commit()