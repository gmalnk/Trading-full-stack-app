from sqlalchemy import create_engine, Column, Integer, Float, String, update, Table, MetaData
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.sql import func
from datetime import datetime, timezone
from FastAPI.DBConn.Tables import *
from FastAPI.Constants import *
from FastAPI.config import *
from FastAPI.Modules.Logging import *
from FastAPI.Modules.Utility import Utility, Candle, TrendLine, SimTrendLine
from FastAPI.Modules.PriceAction import PriceAction
import pandas as pd
from scipy.stats import mode, skew, kurtosis
from statsmodels.tsa.stattools import adfuller, kpss

# Create an engine to connect to your PostgreSQL database
engine = create_engine(f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost/{POSTGRES_DATABASE}')

# Create the tables
TableSQL.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)

def sample():
    with Session() as session:
        base_query = (
            session.query(
                func.min(FifteenTFTable.id).label('id'),
                FifteenTFTable.token,
                func.min(FifteenTFTable.time).label('time'),
                func.first(FifteenTFTable.open).label('open'),
                func.max(FifteenTFTable.high).label('high'),
                func.min(FifteenTFTable.low).label('low'),
                func.last(FifteenTFTable.close).label('close'),
                func.sum(FifteenTFTable.volume).label('volume')
            )
            .group_by(
                FifteenTFTable.token,
                func.date_trunc('hour', FifteenTFTable.time)  # truncating time to the hour
            )
            .order_by(func.min(FifteenTFTable.time).desc()))

        # Execute the query
        result = base_query.all()
        print(result)

def bulk_save(data):
    with Session() as session:
        session.bulk_save_objects(data)
        session.commit()
# this method is used for analysis of highs and lows in the highlow_data table and form trendlines and store them 
def initialize_high_low(stock_token:str, time_frame:TimeFrame, consider_all:bool=False)->bool:
    try:
        start_time:datetime = datetime.min

        if not consider_all:
            index = get_latest_highlow_index(stock_token=stock_token, time_frame=time_frame)
            if index == 0:
                start_time = Utility.get_starttime_of_analysis(time_frame=time_frame)
        else:
            index = 0

        candles = fetch_candles(stock_token=stock_token,time_frame=time_frame, index=index-FOUR, start_time=start_time)
        highlow_candles = Utility.find_highs_and_lows(candles)

        if len(highlow_candles) > 0:
            highlow_data_objects = [
                HighLowTable(
                    index=candle.index,
                    token=stock_token,
                    time=candle.time,
                    open=candle.open,
                    high=candle.high,
                    low=candle.low,
                    close=candle.close,
                    volume=candle.volume,
                    high_low=candle.hl,
                    tf=time_frame.value
                )
                for candle in highlow_candles
            ]                
            bulk_save(data=highlow_data_objects)
            return True
        return False

    except Exception as error:
        daily_logger.error("Failed at initialize_high_low method error message: " + str(error))
        
# this method is used for analysis of highs and lows in the highlow_data table and form trendlines and store them 
def get_trendLines(stock_token:str, time_frame:TimeFrame)->None:
    try:
        highs = fetch_highs(stock_token=stock_token, time_frame=time_frame)
        lows = fetch_lows(stock_token=stock_token, time_frame=time_frame)
        index = MAX_NUM
        if not (highs and lows):
            return
        if highs:
            index = min(index, highs[0].index)
        if lows:
            index = min(index, lows[0].index)
        candles = fetch_candles(stock_token = stock_token, time_frame = time_frame, index = index-TEN)
        current_trendlines = fetch_current_trendlines(stock_token=stock_token, time_frame=time_frame)
        [update_uptrendline, update_downtrendline] = update_broken_trendlines(current_trendlines=current_trendlines,latest_candles=candles[-30:])
        price_action = PriceAction(highs, lows, candles, update_uptrendline, update_downtrendline)
        trendlines = price_action.TrendlinesToDraw
        update_trendlines(stock_token=stock_token, time_frame=time_frame, trendlines=trendlines)
    except (Exception) as error:
        daily_logger.error("Failed at get trendlines method  error message : " + str(error))
    finally:
        daily_logger.info("generated trendlines successfully for " + ALL_TOKENS[stock_token] + " stock")

def update_broken_trendlines(current_trendlines:list[TrendLine], latest_candles:list[Candle])->list[bool,bool]:
    try:
        update = ''
        no_trendline = ""

        with Session() as session:
            for trendline in current_trendlines:
                if trendline.slope == 0 and trendline.intercept == -1:
                    no_trendline += trendline.hl
                    continue

                for candle in reversed(latest_candles):
                    if candle.date < trendline.startdate:
                        break

                    trendline_value = trendline.slope * candle.index + trendline.intercept

                    if (trendline.hl == "h" and candle.close > trendline_value) or (trendline.hl == "l" and candle.close < trendline_value):
                        new_trendline = BrokenTrendlines(
                            token=trendline.token,
                            tf=trendline.tf,
                            slope=trendline.slope,
                            intercept=trendline.intercept,
                            startdate=trendline.startdate,
                            enddate=trendline.enddate,
                            hl=trendline.hl,
                            index1=trendline.index1,
                            index2=trendline.index2,
                            index=trendline.index,
                            connects=trendline.connects,
                            totalconnects=trendline.totalconnects
                        )
                        session.add(new_trendline)
                        initialize_trendline(session, trendline.token, trendline.tf, trendline.hl)
                        update += trendline.hl
                        break

            if not update:
                return [no_trendline.__contains__("L"), no_trendline.__contains__("H")]

        return [update.__contains__("L") or no_trendline.__contains__("L"), update.__contains__("H") or no_trendline.__contains__("H")]

    except Exception as error:
        daily_logger.error("Failed to update broken trendlines. Error: " + str(error))
        return [False, False]

def update_trendlines(stock_token:str, time_frame:TimeFrame, trendlines:list[TrendLine])->None:
    try:
        latest_index = get_latest_index(stock_token=stock_token, time_frame=time_frame)

        if len(trendlines) > 0:
            with Session() as session:
                for trendline in trendlines:
                    if trendline.slope is None:
                        continue

                    # Query to update the TrendlineData records
                    session.execute(
                        TrendlineTable.__table__.update().
                        where(
                            (TrendlineTable.token == stock_token) &
                            (TrendlineTable.tf == time_frame.value) &
                            (TrendlineTable.hl == trendline.hl)
                        ).
                        values(
                            slope=trendline.slope,
                            intercept=trendline.intercept,
                            startdate=trendline.candles[0].date,
                            enddate=trendline.candles[-1].date,
                            index1=trendline.candles[0].index,
                            index2=trendline.candles[-1].index,
                            index=latest_index,
                            connects=trendline.connects,
                            totalconnects=trendline.totalconnects
                        )
                    )
                    
    except Exception as error:
        daily_logger.error("Failed at update_trendlines method. Error: " + str(error))
    finally:
        daily_logger.info(f"Updated trendlines successfully for {ALL_TOKENS[stock_token]} stock")

def initialize_trendline(stock_token:str, time_frame:TimeFrame, hl:str)->None:
    try:
        
        with Session() as session:
        # Query to update the TrendlineData records
            session.execute(
                TrendlineTable.__table__.update().
                where(
                    (TrendlineTable.token == stock_token) &
                    (TrendlineTable.tf == time_frame.value) &
                    (TrendlineTable.hl == hl)
                ).
                values(
                    slope=0,
                    intercept=-1,
                    startdate=datetime.now(),
                    enddate=datetime.now(),
                    index1=0,
                    index2=0,
                    index=0,
                    connects=0,
                    totalconnects=0
                )
            )

        # The session is automatically committed when the 'with' block exits successfully
    except Exception as error:
        # Handle exceptions, if needed
        daily_logger.error("Failed at initialize_trendline method. Error: " + str(error))
   
def fetch_current_trendlines(stock_token:str, time_frame:TimeFrame)->list[TrendLine]:
    try:        
        with Session() as session:
        # Query to fetch current trendlines
        # Return the fetched trendlines
            return session.execute(
                TrendlineTable.__table__.select().
                where(
                    (TrendlineTable.token == stock_token) &
                    (TrendlineTable.tf == time_frame.value)
                )
            ).fetchall()

    except Exception as error:
        # Handle exceptions, if needed
        daily_logger.error("Failed at fetch_current_trendlines method. Error: " + str(error))
        return []        

def fetch_all_highlows(stock_token:str, time_frame:TimeFrame, start_time:datetime=datetime.min)->list[Candle]:
    try:
        with Session() as session:
            # Fetch the results
            rows = session.query(HighLowTable).filter(
                (HighLowTable.token == stock_token) &
                (HighLowTable.tf == time_frame.value) &
                (HighLowTable.time > start_time)
            ).order_by(HighLowTable.index.asc()).all()

        # Convert rows to Candle objects
        candles = [
            Candle(index=row.index, time=row.time, open=row.open, high=row.high, low=row.low, close=row.close, volume=row.volume, hl=row.high_low)
            for row in rows
        ]

        return candles

    except Exception as error:
        # Handle exceptions, if needed
        daily_logger.error("Failed at fetch highs. Error: " + str(error))
        return []
    finally:
        daily_logger.info(f"Fetched highs successfully for {ALL_TOKENS[stock_token]} stock")

# this method fetches high candles for given stock, for given time frame
def fetch_highs(stock_token:str, time_frame:TimeFrame, start_time:datetime)->list[Candle]:
    try:
        with Session() as session:
            start_time = Utility.get_starttime_of_analysis(time_frame=time_frame)
            # Fetch the results
            rows = session.query(HighLowTable).filter(
                (HighLowTable.token == stock_token) &
                (HighLowTable.tf == time_frame.value) &
                (HighLowTable.high_low.like('h%')) &
                (HighLowTable.time > start_time)
            ).order_by(HighLowTable.index.asc()).all()

        # Convert rows to Candle objects
        candles = [
            Candle(index=row.index, time=row.time, open=row.open, high=row.high, low=row.low, close=row.close, volume=row.volume, hl=row.high_low)
            for row in rows
        ]

        return candles

    except Exception as error:
        # Handle exceptions, if needed
        daily_logger.error("Failed at fetch highs. Error: " + str(error))
        return []
    finally:
        daily_logger.info(f"Fetched highs successfully for {ALL_TOKENS[stock_token]} stock")
        
# this method fetches low candles for given stock, for given time frame
def fetch_lows(stock_token:str, time_frame:TimeFrame)->list[Candle]:
    try:
        start_time = Utility.get_starttime_of_analysis(time_frame)
        
        with Session() as session:
        # Fetch the results
            rows = session.query(HighLowTable).filter(
                (HighLowTable.token == stock_token) &
                (HighLowTable.tf == time_frame.value) & 
                (HighLowTable.high_low.like('%l')) &
                (HighLowTable.time > start_time)
            ).order_by(HighLowTable.index.asc()).all()

        # Convert rows to Candle objects
        candles = [
            Candle(index=row.index, time=row.time, open=row.open, high=row.high, low=row.low, close=row.close, volume=row.volume, hl=row.high_low)
            for row in rows
        ]

        return candles

    except Exception as error:
        # Handle exceptions, if needed
        daily_logger.error("Failed at fetch lows. Error: " + str(error))
        return []
    finally:
        daily_logger.info(f"Fetched lows successfully for {ALL_TOKENS[stock_token]} stock")
        
# this method fetches all candles for given stock, for given time frame if limit is not specified 
# if limit is provided then latest x no of candles are only returned        
def fetch_candles(stock_token:str, time_frame:TimeFrame, limit:int=0, index:int=0, start_time:datetime=datetime.min)->list[Candle]:
    try:
        with Session() as session:
            table = Utility.get_table(time_frame=time_frame)
            candles = session.query(func.row_number().over(order_by=table.time).label('id'),
                                  table.time,
                                  table.open,
                                  table.high,
                                  table.low,
                                  table.close,
                                  table.volume,
                                  ).filter(table.token == stock_token).order_by(table.time.asc()).all()

            candles = Utility.resample(time_frame=time_frame, candles=candles)

            if limit > 0:
                candles = candles[-limit:]
            
            # Apply additional filters based on index and start_time
            if index > 0:
                candles = candles[index:]

            if start_time != datetime.min:
                candles = [candle for candle in candles if candle.time >= start_time] 

            return candles

    except Exception as error:
        # Handle exceptions, if needed
        daily_logger.error("Failed to fetch candles. Error: " + str(error))
        return []
    finally:
        daily_logger.info(f"Fetched candles successfully for {ALL_TOKENS[stock_token]} stock for {time_frame} timeframe")
      
# this method's functionality is to get latest candle's index for given stock and give time_frame  
def get_latest_index(stock_token:str, time_frame:TimeFrame)->int:
    try:
        with Session() as session:
            table = Utility.get_table(time_frame)
            
            # Fetch the results
            result = session.query(func.max(table.index)).filter(table.token == stock_token).scalar()

        if result is None:
            return 0

        return result

    except Exception as error:
        # Handle exceptions, if needed
        daily_logger.error(f"Failed at get_latest_index method for stock_token: {stock_token} and time_frame: {time_frame}. Error: {str(error)}")
        return 0
        
# this method's functionality is to get latest candle's date for given stock and give time_frame
# used when fetching latest candles data
def get_latest_date(stock_token:str, time_frame:TimeFrame)->datetime:
    try:
        table = Utility.get_table(time_frame)
        with Session() as session:
            # Fetch the results
            result = session.query(func.max(table.time)).filter(table.token == stock_token).scalar()

            if result is None:
                return datetime.min

            return result

    except Exception as error:
        # Handle exceptions, if needed
        daily_logger.error(f"Failed at get_latest_date method for stock_token: {stock_token} and time_frame: {time_frame}. Error: {str(error)}")
        return 0
        
# this method's functionality is to get latest high/low candle's index for given stock and give time_frame
def get_latest_highlow_index(stock_token:str, time_frame:TimeFrame)->int:
    try:
        with Session() as session:
            # Fetch the results
            result = session.query(func.max(HighLowTable.index)).filter(
                (HighLowTable.token == stock_token) &
                (HighLowTable.tf == time_frame.value)
            ).scalar()

        if result is None:
            return 0

        return result

    except Exception as error:
        # Handle exceptions, if needed
        daily_logger.error(f"Failed at get_latest_highlow_index method for stock_token: {stock_token} and time_frame: {time_frame}. Error: {str(error)}")
        return 0
        
def get_latest_low(stock_token:str, time_frame:TimeFrame, time:datetime):
    try:
        with Session() as session:
            row = session.query(HighLowTable).filter(
                HighLowTable.token==stock_token,
                HighLowTable.tf==time_frame.value,
                HighLowTable.high_low.like("%l"),
                HighLowTable.time < time
            ).order_by(HighLowTable.time.desc()).first()
        return Candle(index=row.index, time=row.time, open=row.open, high=row.high, low=row.low, close=row.close, volume=row.volume, hl= row.high_low)
    except Exception as error:
        daily_logger.error(f"failed at get_latest_low for {stock_token}, {time_frame}", error)        
        
# this method's functionality is to create trendline_data table with initial values
def create_trendline_data_table()->None:
    try:
        with Session() as session:
            # Create trendline data with initial values
            for stock_token in ALL_TOKENS:
                for time_frame in TimeFrame:
                    for hl in ["h", "l"]:
                        trendline = get_initial_TrendlineTable_row(stock_token, time_frame, hl)
                        session.add(trendline)
            session.commit()
                        
    except Exception as error:
        # Handle exceptions, if needed
        daily_logger.error("Failed at create_trendline_data_table method. Error: " + str(error))
    finally:
        daily_logger.info("Successfully initialized trendline_data table")
        
def get_initial_TrendlineTable_row(stock_token:str, time_frame:TimeFrame, hl:str)->TableSQL:  
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')      
        return TrendlineTable(
                    token=stock_token,
                    tf=time_frame.value,
                    slope=0,
                    intercept=-1,
                    startdate=date_str,
                    enddate=date_str,
                    hl=hl,
                    index1=0,
                    index2=0,
                    index=0,
                    connects=0,
                    totalconnects=0
                )

def initialize_trendline_data_table()->None:
    try:
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with Session() as session:
            # Update all rows in the trendline_data table
            session.query(TrendlineTable).update({
                'slope': 0,
                'intercept': -1,
                'startdate': date_str,
                'enddate': date_str,
                'index1': 0,
                'index2': 0,
                'index': 0,
                'connects': 0,
                'totalconnects': 0
            })
        
    except Exception as error:
        # Handle exceptions, if needed
        daily_logger.error("Failed at initialize_trendline_data_table method. Error: " + str(error))
    finally:
        daily_logger.info("Successfully initialized trendline_data table")

# this method increments the index of the trendlines for given timeframe
# used repetatively for every new candle formed in any time frame in real time
def increment_index(time_frame:TimeFrame)->None:
    try:
        with Session() as session:
            # Update the index for all rows in the trendline_data table for the specified time_frame
            session.query(TrendlineTable).filter(TrendlineTable.tf == time_frame).update({
                'index': TrendlineTable.index + 1
            })
 
    except (Exception) as error:
        trades_executer_logger.error("Failed at increment_index method error mesage: " + str(error))
    finally:
        daily_logger.info(f"succesfully incremented trendline_data table index for given time_frame {time_frame}")
  
#   this is a one time use method which initializes stock details table
def initialize_stocks_details_table()->None:
    try:
        stock_details = []
        for token in ALL_TOKENS:
            stock_details.append(StockDetails(
                token=token,
                name=ALL_TOKENS[token],
                category=''
                ))
        bulk_save(data=stock_details)
                
    except (Exception) as error:
        print("failed at initialize_stocks_details_table method error mesage: ",error)

def execute_trades_on_candle_close(api, time_frame:TimeFrame, start_time:datetime):
    try:
        trade_ids = []
        trades_entered = []
        end_time = start_time + datetime.timedelta(minutes=Utility.no_of_minutes(time_frame))
        trades = get_trades(time_frame, start_time, end_time)
        execution_time_frame = Utility.get_TimeFrame(time_frame)

        with Session() as session:
            for trade in trades:
                if trade_criteria(trade, execution_time_frame):
                    api.place_order(
                        variety="ROBO",
                        tradingsymbol=f"{ALL_TOKENS[str(trade[0])]}-EQ",
                        symboltoken=trade[0],
                        transactiontype="BUY" if trade[2] == "H" else "SELL",
                        ordertype="LIMIT",
                        producttype="INTRADAY",
                        duration="DAY",
                        price=trade[13],
                        squareoff=abs(trade[4] - trade[13]),
                        stoploss=abs(trade[13] - trade[5]),
                        quantity=trade[6]
                    )

                    # Assuming you have a Trade model
                    session.add(TradesTable(
                        token=trade.token,
                        tf=trade.tf,
                        direction=trade.direction,
                        entry_condition=trade.entry_condition,
                        tp=trade.tp,
                        sl=trade.sl,
                        quantity=trade.quantity,
                        slope=trade.slope,
                        intercept=trade.intercept,
                        index=trade.index,
                        open=trade.open,
                        high=trade.open,
                        low=trade.low,
                        close=trade.close
                    )) 
                    
                    trade_ids.append(trade[0])

        for id in trade_ids:
            trades_executer_logger.info(f"trade executed {id}")

        increment_index(time_frame)
        update_trades(trade_ids)

    except Exception as error:
        trades_executer_logger.error("Failed at execute_trades method error message: " + str(error))

def get_trades(session:sessionmaker, time_frame:TimeFrame, start_time:datetime, end_time:datetime):
    try:
        TradesTableAlias = aliased(TradesTable)
        TrendlineTableAlias = aliased(TrendlineTable)

        subquery = (
            session.query(
                TicksTable.symbol_token,
                func.FIRST_VALUE(TicksTable.ltp).over().partition_by(TicksTable.symbol_token).label('open'),
                func.MAX(TicksTable.ltp).over().partition_by(TicksTable.symbol_token).label('high'),
                func.MIN(TicksTable.ltp).over().partition_by(TicksTable.symbol_token).label('low'),
                func.LAST_VALUE(TicksTable.ltp).over().partition_by(TicksTable.symbol_token).label('close')
            )
            .filter(
                TicksTable.time >= start_time,
                TicksTable.time <= end_time
            )
            .distinct()
            .cte('ohlc_data')
        )

        query = (
            session.query(
                TradesTableAlias.token,
                TradesTableAlias.tf,
                TradesTableAlias.direction,
                TradesTableAlias.entry_condition,
                TradesTableAlias.tp,
                TradesTableAlias.sl,
                TradesTableAlias.quantity,
                TrendlineTableAlias.slope,
                TrendlineTableAlias.intercept,
                TrendlineTableAlias.index,
                subquery.c.open.label('open'),
                subquery.c.high.label('high'),
                subquery.c.low.label('low'),
                subquery.c.close.label('close')
            )
            .join(
                TrendlineTableAlias,
                (TradesTableAlias.token == TrendlineTableAlias.token) &
                (TradesTableAlias.tf == TrendlineTableAlias.tf) &
                (TradesTableAlias.direction == TrendlineTableAlias.hl)
            )
            .join(
                subquery,
                TradesTableAlias.token == subquery.c.symbol_token
            )
            .filter(
                TradesTableAlias.status == 'TODO',
                TradesTableAlias.tf == time_frame.value,
                TradesTableAlias.entry_condition.like('%Close%')
            )
        )

        rows = query.all()
        return rows

    except Exception as error:
        trades_executer_logger.error("Failed at get_trades method error message: " + str(error))

def update_trades(orders_placed:list[int])->None:
    try:
        if orders_placed:
            with Session() as session:
                session.execute(
                    update(TradesTable)
                    .where(TradesTable.token.in_(orders_placed))
                    .values(status='DONE')
                )
    except Exception as error:
        trades_executer_logger.error("Failed at get_trades method error message: " + str(error))

def trade_criteria(trade, execution_time_frame):
    if (breaks_trendline(trade)):
        if (Utility.compare_TimeFrame(execution_time_frame, Utility.get_TimeFrame(trade[1])) == TimeFrameComparer.Equal):
            return True
        elif (Utility.compare_TimeFrame(execution_time_frame, Utility.get_TimeFrame(trade[1])) == TimeFrameComparer.Lower and is_strong_candle(trade)):
            return True
    return False
def breaks_trendline(trade):
    trendline_value = calculate_trendline_value(trade)
    return (trade.close > trendline_value if Utility.get_TradeDirection(trade.direction) == TradeDirection.BUY else trade.close < trendline_value) 

def calculate_trendline_value(trade):
        return trade.slope * trade.index + trade.intercept
    
def is_strong_candle(trade):
    return (Utility.get_TradeDirection(trade.direction) == TradeDirection.BUY and trade.high == trade.close) or (Utility.get_TradeDirection(trade.direction) == TradeDirection.SELL and trade.low == trade.close)

# *********************** FRONTEND API METHODS ***********************
# this method provides stock data, for given stock token, for given time frame, for plotting in UI
def api_get_stock_data(stock_token:str, time_frame:str):
    try:
        data = []
        time_frame = Utility.get_TimeFrame(TF=time_frame)
        candles = fetch_candles(stock_token=stock_token, time_frame=time_frame)
        for candle in candles:
            data.append({
                "time": candle.time.timestamp(),
                "open":candle.open,
                "high":candle.high,
                "low":candle.low,
                "close":candle.close
                })
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
        with Session() as session:
            new_trade = TradesTable(
                token = tradedetails['stockToken'],
                tf = tradedetails['timeFrame'],
                status = 'TODO',
                direction = tradedetails["tradeDirection"],
                entry_condition = entry_condition,
                tp = tradedetails["takeProfit"],
                sl = tradedetails["stopLoss"],
                quantity = tradedetails["numOfShares"],
            )
            session.add(new_trade)
    except (Exception) as error:
        print(f"failed while responding api call in method add_trade_data for stock_token: {tradedetails['stockToken']} and time_frame : {tradedetails['timeFrame']} error mesage: ",error)
    
# this method gets all stock details
def get_stock_details(timeFrame:str, stockListCategory:str, stockListSort:str):
    try:
        tokens = Utility.get_tokens(Utility.get_marketcap(stockListCategory))
        if stockListSort == "cap":
            return {'stocksDict' :ALL_TOKENS, 'tokensList':tokens}
        if stockListSort  == "alphabets":
            tokens.sort(key=lambda x: ALL_TOKENS[x])
        else:
            tokens = get_tokens_ordered_Based_on_connects(timeFrame, stockListSort, tokens)
        return {'stocksDict' :ALL_TOKENS, 'tokensList':tokens}
    except (Exception) as error:
        print(f"failed while responding api call in method get_stock_details for stock_token: time_frame : {timeFrame} error mesage: ",error)
    
def get_tokens_ordered_Based_on_connects(timeFrame, HL, tokens):
    try:
        with Session() as session:
            rows = (session.query(TrendlineTable.token, TrendlineTable.connects)
            .filter(TrendlineTable.tf == timeFrame, TrendlineTable.connects > 2, TrendlineTable.hl == HL)
            .order_by(TrendlineTable.connects.desc(), TrendlineTable.totalconnects.desc())
            .all())
            result = [row[0] for row in rows if str(row[0]) in tokens]
            return result
            
    except (Exception) as error:
        print(f"failed while responding api call in method get_stock_details for stock_token: time_frame : {timeFrame} error mesage: ",error)
    

# this method provides trendline data, for given stock token, for given time frame, for plotting in UI
def api_get_trendline_data(stock_token:str, time_frame:TimeFrame):
    try:
        with Session() as session:
            rows = session.query(TrendlineTable).filter(TrendlineTable.token == stock_token, TrendlineTable.tf == time_frame.value).all()

            data = []
            hl = ""
            for row in rows:
                slope = row.slope
                intercept = row.intercept
                if not (slope == 0 and intercept == -1):
                    data.append(
                        [
                            {
                                "time": int(row.startdate.replace(tzinfo=timezone.utc).timestamp()),
                                "value": slope * row.index1 + intercept,
                            },
                            {
                                "time": int(row.enddate.replace(tzinfo=timezone.utc).timestamp()),
                                "value": slope * row.index2 + intercept,
                            },
                        ]
                    )
                    hl += row.hl

            result_data = {"trendlineData": data, "linesData": hl}
            return result_data
    except (Exception) as error:
        print(f"failed while responding api call in method api_get_trendline_data for stock_token: {stock_token} and time_frame : {time_frame} error mesage: ",error)
        return {"trendlineData" : [], "linesData":""}

# this method gets all the trades data 
def get_all_trades():
    try:
        with Session() as session:
        # Perform the query using SQLAlchemy ORM
            trades_data_rows = (
                session.query(
                    TradesTable.id,
                    StockDetails.name,
                    TradesTable.tf,
                    TradesTable.status,
                    TradesTable.direction,
                    TradesTable.quantity,
                    TradesTable.bp,
                    TradesTable.sp,
                    TradesTable.tp,
                    TradesTable.sl,
                    TradesTable.pl,
                )
                .join(StockDetails, StockDetails.token == TradesTable.token)
                .all()
            )

        trades_data = []
        for row in trades_data_rows:
            trades_data.append(
                {
                    "id": row.id,
                    "stockName": row.name,
                    "timeFrame": row.tf,
                    "status": row.status,
                    "direction": "Long" if row.direction == "h" else "Short",
                    "quantity": row.quantity,
                    "entryPrice": row.bp if row.bp is not None else "---",
                    "exitPrice": row.sp if row.sp is not None else "---",
                    "takeProfit": row.tp,
                    "stopLoss": row.sl,
                    "p&l": row.pl if row.pl is not None else "---",
                }
            )

        return {"tradesData": trades_data}
    except Exception as error:
        print(f"Failed to get all trades data: {error}")
        
# this method deletes a trade based on the given id
def delete_trade(trade_id):
    try:
        with Session() as session:
            trade_to_delete = session.query(TradesTable).filter_by(id=trade_id).first()
            
            if trade_to_delete:
                session.delete(trade_to_delete)
                session.commit()
                print(f"Trade with ID {trade_id} deleted successfully.")
            else:
                print(f"Trade with ID {trade_id} not found.")
                
    except Exception as error:
        print(f"Failed to delete trade: {error}")
    
def authenticate(email, password):
    try:
        with Session() as session:
            user = session.query(UsersTable).filter_by(email=email, password=password).first()
            if user:
                return True
            else:
                return False
            
    except Exception as error:
        print(f"Failed to authenticate: {error}")

def add_user(name, email, password):
    try:
        with Session() as session:
            user = session.query(UsersTable).filter_by(email=email).first()
            if user:
                return False
            else:
                new_user = UsersTable(
                    name=name,
                    email = email,
                    password = password
                )
                session.add(new_user)
                session.commit()
                return True
    except Exception as error:
        print(f"Failed to add user: {error}")
    
class Simulation():
    def __init__(self, time_frame:TimeFrame, token:str):
        self.time_frame = time_frame
        self.token = token
        self.candles = []
        self.highlows = []
        self.current_highs = []
        self.sim_trendlines = []
    
    def is_new_trendline(self, trendline):
        if len(self.sim_trendlines) != 0:
            if trendline.slope == self.sim_trendlines[-1].slope and trendline.intercept == self.sim_trendlines[-1].intercept:
                return False
        return True
    
    def get_stats(self, trendline, start_index, breakout_index):
        i = start_index
        j = breakout_index+1
        data = {
            'index': [candle.index for candle in self.candles[i:j]],            
            'open': [candle.open for candle in self.candles[i:j]],
            'high': [candle.high for candle in self.candles[i:j]],
            'low': [candle.low for candle in self.candles[i:j]],
            'close': [candle.close for candle in self.candles[i:j]],
            'volume': [candle.volume for candle in self.candles[i:j]]
        }
        df = pd.DataFrame(data)
        df['trendline'] = trendline.slope * df['index'] + trendline.intercept

        # Add a new column 'average_price' to calculate the average of open, high, low, close
        df['average_price'] = df[['open', 'high', 'low', 'close']].mean(axis=1)
        
        df['change'] = (df['trendline'] - df['average_price'])

        # Add a new column 'percentage_change' based on the formula (my_price - average_price) / average_price
        df['percentage_change'] = ((df['trendline'] - df['average_price']) / df['average_price'])*100

        # Add a new column 'volume_avg_20' representing the 20-day moving average of 'volume'
        df['volume_avg_20'] = df['volume'].rolling(window=20).mean()
        
        # Calculate statistical measures for the 'percentage_change' column
        trendline.mean = df['percentage_change'].mean()
        trendline.median = df['percentage_change'].median()
        trendline.mode = mode(df['percentage_change'], keepdims=True)[0][0]
        trendline.range = df['percentage_change'].max() - df['percentage_change'].min()
        trendline.std = df['percentage_change'].std()
        trendline.skewness = skew(df['percentage_change'])
        trendline.kurtosis = kurtosis(df['percentage_change'])

        trendline.volume_ratio = df.loc[df['index'] == breakout_index, 'volume'].values[0] / df.loc[df['index'] == breakout_index, 'volume_avg_20'].values[0]

        # ADF Test (Augmented Dickey-Fuller)
        result_adf = adfuller(df['change'])
        trendline.adf_stats = result_adf[0]
        trendline.adf_p = result_adf[1]
        trendline.adf_1 = result_adf[4]["1%"]
        trendline.adf_5 = result_adf[4]["5%"]
        trendline.adf_10 = result_adf[4]["10%"]

        # # KPSS Test (Kwiatkowski-Phillips-Schmidt-Shin)
        # result_kpss = kpss(df['change'], store=True)
        # trendline.kpss_stats = result_kpss[0]
        # trendline.kpss_p = result_kpss[1]
        # trendline.kpss_1 = result_kpss[2]["1%"]
        # trendline.kpss_5 = result_kpss[2]["5%"]
        # trendline.kpss_10 = result_kpss[2]["10%"]
        
        result_kpss = kpss(df['change'])
        trendline.kpss_stats = result_kpss[0]
        trendline.kpss_p = result_kpss[1]
        trendline.kpss_1 = result_kpss[3]["1%"]
        trendline.kpss_5 = result_kpss[3]["5%"]
        trendline.kpss_10 = result_kpss[3]["10%"]
        
        # result_kpss = kpss(df['average_price'], regression='ct')
        # trendline.kpss_stats = result_kpss[0]
        # trendline.kpss_p = result_kpss[1]
        # trendline.kpss_1 = result_kpss[3]["1%"]
        # trendline.kpss_5 = result_kpss[3]["5%"]
        # trendline.kpss_10 = result_kpss[3]["10%"]
        
        return trendline
                
    def get_all_attributes_of_trendline(self, trendline):
        sim_trendline = SimTrendLine(trendline=trendline, token=self.token, time_frame=self.time_frame)
        breakout_index = trendline.candles[-1].index - 1
        breakout_time = datetime.min
        
        while breakout_index+1 <= len(self.candles)-1 and self.candles[breakout_index+1].close <= trendline.slope * (breakout_index+2) + trendline.intercept:
            breakout_index += 1
        breakout_index += 1
        
        if breakout_index > len(self.candles)-1:
            return
        
        breakout_time = self.candles[breakout_index].time
        sim_trendline.close_percentage = ((self.candles[breakout_index].close - (trendline.slope * (breakout_index+1) + trendline.intercept))/(trendline.slope * (breakout_index+1) + trendline.intercept))*100
        entry = self.candles[breakout_index].close
        recentlow = get_latest_low(stock_token=self.token, time_frame=self.time_frame, time=breakout_time)
        stoploss = recentlow.low
        rrr = 0
        tradeexit_candle = breakout_index + 1
        
        while (self.candles[tradeexit_candle].close - entry) < (entry-stoploss)*10 :
            if self.candles[tradeexit_candle].close < stoploss or tradeexit_candle+1 > len(self.candles) -1:
                break
            rrr = max( rrr, int((self.candles[tradeexit_candle].close - entry)/(entry-stoploss)))
            tradeexit_candle += 1
        rrr = max( rrr, int((self.candles[tradeexit_candle].close - entry)/(entry-stoploss)))
        
        if rrr >= 1:
            sim_trendline.rrr1 = 1
        if rrr >= 2:
            sim_trendline.rrr2 = 1
        if rrr >= 3:
            sim_trendline.rrr3 = 1
        if rrr >= 4:
            sim_trendline.rrr4 = 1
        if rrr >= 5:
            sim_trendline.rrr5 = 1
        if rrr >= 6:
            sim_trendline.rrr6 = 1
        if rrr >= 7:
            sim_trendline.rrr7 = 1
        if rrr >= 8:
            sim_trendline.rrr8 = 1
        if rrr >= 9:
            sim_trendline.rrr9 = 1
        if rrr >= 10:
            sim_trendline.rrr10 = 1            
        
        sim_trendline = self.get_stats(sim_trendline, trendline.candles[0].index -1, breakout_index)
        self.sim_trendlines.append(sim_trendline)
        
    def run(self):
        self.candles = fetch_candles(time_frame=self.time_frame, stock_token=self.token)
        self.highlows = fetch_all_highlows(time_frame=self.time_frame, stock_token=self.token)
        
        for high in self.highlows:
            if high.hl == "l":
                continue
            self.current_highs.append(high)
            analysis_time_limit = Utility.get_starttime_of_analysis(time_frame=self.time_frame, time=high.time)
            while self.current_highs[0].time < analysis_time_limit:
                self.current_highs = self.current_highs[1:]
            self.current_highs = Utility.filter_highs(self.current_highs)
            if len(self.current_highs) > 2:
                price_action = PriceAction(self.current_highs, [], self.candles[self.current_highs[0].index-6: self.current_highs[-1].index+4], False, True)
                trendlines = price_action.TrendlinesToDraw 
                if len(trendlines) == 1 and trendlines[0].slope <= 0 and self.is_new_trendline(trendlines[0]):
                    self.get_all_attributes_of_trendline(trendlines[0])

        print("done")

        data = []
        for line in self.sim_trendlines:
            data.append(SimTrendlineTable(
                token = self.token,
                tf = self.time_frame.value,
                slope = line.slope,
                intercept = line.intercept,
                hl = line.hl,
                connects = line.connects,
                totalconnects = line.totalconnects,
                candlescount = line.candlescount,
                mean = line.mean,
                median = line.median,
                mode = line.mode,
                _range = line.range,
                std = line.std,
                skewness = line.skewness,
                kurtosis = line.kurtosis,
                adf_stats = line.adf_stats,
                adf_p = line.adf_p,
                adf_1 = line.adf_1,
                adf_5 = line.adf_5,
                adf_10 = line.adf_10,
                kpss_stats = line.kpss_stats,
                kpss_p = line.kpss_p,
                kpss_1 = line.kpss_1,
                kpss_5 = line.kpss_5,
                kpss_10 = line.kpss_10,
                volume_ratio = line.volume_ratio,
                close_percentage = line.close_percentage,
                rrr1 = line.rrr1,
                rrr2 = line.rrr2,
                rrr3 = line.rrr3,
                rrr4 = line.rrr4,
                rrr5 = line.rrr5,
                rrr6 = line.rrr6,
                rrr7 = line.rrr7,
                rrr8 = line.rrr8,
                rrr9 = line.rrr9,
                rrr10 = line.rrr10,
            ))
        
        
        
        with Session() as session:
            bulk_save(data)

































