from FastAPI.Constants import *
from FastAPI.Modules.Logging import *
from FastAPI.config import *
from FastAPI.DBConn.Tables import DailyTFTable, FifteenTFTable, HighLowTable
from datetime import datetime, timedelta, date
from itertools import combinations
from sqlalchemy import Table
import pandas as pd
import pytz

class Utility():
    # returns True if the given candle is Local Maximum else False
    @staticmethod
    def IsMax(candles, i):
        if max(candles[i-5].high, candles[i-4].high, candles[i-3].high, candles[i-2].high, candles[i-1].high, candles[i].high, candles[i+1].high, candles[i+2].high, candles[i+3].high, candles[i+4].high, candles[i+5].high) == candles[i].high:
            return True
        else:
            return False

    @staticmethod
    def generate_combinations(numbers, r):
        return list(combinations(numbers, r))

    # returns True if the given candle is Local minimum else False
    @staticmethod
    def IsMin(candles, i):
        if min(candles[i-5].low, candles[i-4].low, candles[i-3].low, candles[i-2].low, candles[i-1].low, candles[i].low, candles[i+1].low, candles[i+2].low, candles[i+3].low, candles[i+4].low, candles[i+5].low) == candles[i].low:
            return True
        else:
            return False

    @staticmethod
    def find_highs_and_lows(candles):
        # local variables
        high_low_candles = []
        htemp = 0
        ltemp = 0
        if len(candles) == 0:
            return []
        for i in range(5, len(candles)-5):
            high_low = ""
            if htemp > 0:
                htemp -= 1
            if ltemp > 0:
                ltemp -= 1
            if htemp == 0 and Utility.IsMax(candles, i):
                htemp = 6
                high_low += "h"
            if ltemp == 0 and Utility.IsMin(candles, i):
                ltemp = 6
                high_low += "l"
            if (high_low != ""):
                candles[i].hl = high_low
                high_low_candles.append(candles[i])
        daily_logger.info("length of high low cangles : " + str(len(high_low_candles)))
        if len(high_low_candles) <= 1:
            return high_low_candles
        # high_low_candles = Utility.filter_highs_lows(high_low_candles)
        return high_low_candles

    @staticmethod
    def filter_highs_lows(candles):
        filtered_highs_lows = []
        max_candle = Candle(index=0, volume=0, time=datetime.today(), open=0, high=0, low=0, close=0, hl='')
        min_candle = Candle(index=0, volume=0, time=datetime.today(), open=float(
            'inf'), high=float('inf'), low=float('inf'), close=float('inf'), hl='')
        if (len(candles) > 0):
            for candle in candles:
                if (candle.High_Low.find('h') != -1 and candle.high > max_candle.high):
                    max_candle = candle
                if (candle.High_Low.find('l') != -1 and candle.low < min_candle.low):
                    min_candle = candle
        else:
            return []
        daily_logger.info("max candle index : " + str(max_candle.index))
        daily_logger.info("min candle index : " + str(min_candle.index))
        for candle in candles:
            if candle.High_Low == 'h' and candle.index >= max_candle.index:
                filtered_highs_lows.append(candle)
            if candle.High_Low == 'h' and candle.index >= min_candle.index:
                filtered_highs_lows.append(candle)
            if candle.High_Low == "hl":
                if candle.index >= max_candle.index and candle.index >= min_candle.index:
                    filtered_highs_lows.append(candle)
                    continue
                if (candle.index >= max_candle.index):
                    candle.High_Low = "h"
                    filtered_highs_lows.append(candle)
                if (candle.index >= min_candle.index):
                    candle.High_Low = "l"
                    filtered_highs_lows.append(candle)
        return filtered_highs_lows

    @staticmethod
    def filter_highs(candles):
        if (not candles):
            return []
        filtered_highs = []
        max_candle = Candle(index=0, volume=0, time=datetime.today(), open=0, high=0, low=0, close=0, hl='')
        for candle in candles:
            # todo -- second condition high > high is to be replaced with the compare candles 
            if candle.high > max_candle.high and candle.low > max_candle.high:
                max_candle = candle
        daily_logger.info("max candle index : " + str(max_candle.index))
        filtered_highs = [x for x in candles if x.index >= max_candle.index]
        return filtered_highs

    @staticmethod
    def filter_lows(candles):
        if (not candles):
            return []
        filtered_lows = []
        min_candle = Candle(index=0, volume=0, time=datetime.today(), open=float(
            'inf'), high=float('inf'), low=float('inf'), close=float('inf'), hl='')
        for candle in candles:
            # todo -- condition high > high is to be replaced with the compare candles 
            if (candle.low < min_candle.low):
                min_candle = candle
        daily_logger.info("min candle index : " + str(min_candle.index))
        filtered_lows = [x for x in candles if x.index >= min_candle.index]
        return filtered_lows

    # this method converts ltp  data to pandas ohlc data
    @staticmethod
    def convert_ltp_to_ohlc(time_frame, rows):
        try:
            df = pd.DataFrame(rows, columns=['id', 'token', 'time', 'ltp'])
            df['Date'] = df['time']
            df = df.set_index('Date')
            df = df['ltp'].resample(time_frame).ohlc(_method='ohlc')
            return df
        except (Exception) as error:
            daily_logger.error("Failed at convert_ltp_to_ohlc method error mesage: " + str(error))

    # this method returns no of minutes in a time frame
    @staticmethod
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

    # method provides offset based on time frame 
    # off set of 9 hours 15 minutes is provided for time frames below one day
    # off set of 0 hours 0 minutes is provided for time frames above four hours
    @staticmethod
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
    @staticmethod
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

    # after fetching data from data base we convert it into required time frame using this method
    # it uses pandas resample function with offset and dropna function to remove NAN values
    @staticmethod
    def convert_data_timeframe(time_frame, rows):
        try:
            off_set = Utility.get_offset(time_frame)
            df = pd.DataFrame(rows, columns=['id', 'index', 'token', 'time',
                            'open', 'high', 'low', 'close'])
            df['Date'] = df['time']
            df = df.set_index('Date')
            if time_frame == "ONE_DAY" or time_frame == "FIFTEEN_MINUTE":
                return df
            df = df.resample(Utility.convert_timeframe(time_frame), offset=off_set).apply(OHLC)
            return df.dropna()
        except (Exception) as error:
            daily_logger.error("Failed at convert_data_timeframe method error mesage: " + str(error))

        # we dont analyse all the data for all time frames, we limit out data for analysis hence 
    # this method provides the start time of the analysis based on the time frame
    @staticmethod
    def get_starttime_of_analysis(time_frame:TimeFrame, time:datetime=datetime.today()) -> datetime:
        match time_frame:
            case TimeFrame.FIFTEEN_MINUTE:
                return time-timedelta(days=31)
            case TimeFrame.THIRTY_MINUTE:
                return time-timedelta(days=61)
            case TimeFrame.ONE_HOUR:
                return time-timedelta(weeks=14)
            case TimeFrame.TWO_HOUR:
                return time-timedelta(weeks=28)
            case TimeFrame.FOUR_HOUR:
                return datetime(time.year-1, time.month, time.day)
            case TimeFrame.ONE_DAY:
                return datetime(time.year-2, time.month, time.day)
            case TimeFrame.ONE_WEEK:
                return datetime(time.year-20, time.month, time.day)
            case TimeFrame.ONE_MONTH:
                return datetime(time.year-20, time.month, time.day)
            case default:
                return time

    @staticmethod
    def get_tokens(stockListCategory):
        match stockListCategory:
            case MarketCap.ALL:
                return list(ALL_TOKENS.keys())
            case MarketCap.N50:
                return list(TOKENS_50.keys())
            case MarketCap.N100:
                return list(TOKENS_100.keys())
            case MarketCap.N200:
                return list(TOKENS_200.keys())
            case MarketCap.N500:
                return list(TOKENS_500.keys())
            case MarketCap.N1000:
                return list(TOKENS_1000.keys())
            case default:
                return list(ALL_TOKENS.keys())

    @staticmethod
    def get_marketcap(stockListCategory: str):
        match stockListCategory:
            case "all":
                return MarketCap.ALL
            case "n50":
                return MarketCap.N50
            case "n100":
                return MarketCap.N100
            case "n200":
                return MarketCap.N200
            case "n500":
                return MarketCap.N500
            case "n1000":
                return MarketCap.N1000
            case default:
                return MarketCap.N50
        
    @staticmethod
    def get_TimeFrame(TF: str)-> TimeFrame:
        match TF:
            case "5m":
                return TimeFrame.FIVE_MINUTE
            case "15m":
                return TimeFrame.FIFTEEN_MINUTE
            case "30m":
                return TimeFrame.THIRTY_MINUTE
            case "1h":
                return TimeFrame.ONE_HOUR
            case "2h":
                return TimeFrame.TWO_HOUR
            case "4h":
                return TimeFrame.FOUR_HOUR
            case "1D":
                return TimeFrame.ONE_DAY
            case "1W":
                return TimeFrame.ONE_WEEK
            case "1M":
                return TimeFrame.ONE_MONTH
            case default:
                return TimeFrame.ONE_DAY
            
    @staticmethod
    def compare_TimeFrame(TF1:TimeFrame, TF2:TimeFrame)-> TimeFrameComparer:
        if (TF1.value < TF2.value):
            return TimeFrameComparer.Lower
        elif (TF1.value == TF2.value):
            return TimeFrameComparer.Equal    
        return TimeFrameComparer.Higher

    @staticmethod
    def get_TradeDirection(Direction:str)->TradeDirection:
        match Direction :
            case 'BUY':
                return TradeDirection.BUY
            case 'SELL':
                return TradeDirection.SELL
            case default:
                return TradeDirection.BUY
          
    @staticmethod  
    def get_nb_bars(time_frame:TimeFrame, from_date:datetime, to_date:datetime)->int:
        nb_days = Utility.get_nb_days_between(from_date, to_date)
        return nb_days*Utility.nb_candles_in_day(time_frame)
    
    @staticmethod
    def get_nb_days_between(from_date:datetime, to_date:datetime)->int:
        return (to_date-from_date).days
    
    @staticmethod
    def nb_candles_in_day(time_frame:TimeFrame)->int:
        match time_frame:
            # case TimeFrame.ONE_MINUTE:
            #     return 375
            # case TimeFrame.FIVE_MINUTE:
            #     return 75
            case TimeFrame.FIFTEEN_MINUTE:
                return 25
            case TimeFrame.THIRTY_MINUTE:
                return 13
            case TimeFrame.ONE_HOUR:
                return 7
            case TimeFrame.TWO_HOUR:
                return 4
            case TimeFrame.FOUR_HOUR:
                return 2
            case TimeFrame.ONE_DAY:
                return 1
            case default:
                return 1
    
    @staticmethod
    def epoch_to_datetime(epoch:float)->datetime:
        return datetime.fromtimestamp(epoch)
    
    @staticmethod
    def datetime_to_str(input:str)->datetime:
        return datetime.strftime(input, '%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def str_to_datetime(input:str)->datetime:
        return datetime.strptime(input, '%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def datetime_to_epoch(input:datetime)->float:
        return input.timestamp()
    
    # we have stored fifteen minute data in fifteentf_data table in historicdata data base
    # we have stored daily data in dailytf_data table in historicdata data base
    # all the data up to four hour is created using the fifteentf_data table 
    # all the data above one day is created using the dailytf_data table 
    # this method provides which data table to use based on time frame
    @staticmethod
    def get_table(time_frame:TimeFrame):
        if time_frame not in [TimeFrame.ONE_DAY, TimeFrame.ONE_WEEK, TimeFrame.ONE_MONTH]:
            return FifteenTFTable
        else:
            return DailyTFTable
     
    @staticmethod
    def resample(time_frame:TimeFrame=TimeFrame.ONE_DAY, candles:list[Table]=[]):
        try:            
            resampled_candles = []
            index = 1
            if time_frame in [TimeFrame.FIFTEEN_MINUTE, TimeFrame.ONE_DAY]:
                for candle in candles:
                    resampled_candles.append(Candle(index=index,time=candle.time,open=candle.open,high=candle.high,low=candle.low,close=candle.close,volume=candle.volume)) 
                    index += 1
                return resampled_candles
            if not candles:
                return candles
            time = Utility.get_initial_time_resample(current_time=candles[0].time,time_frame=time_frame) 
            low = MAX_NUM
            open,high,close,volume = candles[0].open, 0, 0, 0
            next_time = Utility.get_next_time_resample(current_time=time,time_frame=time_frame)
            for candle in candles:
                if candle.time >= time and candle.time < next_time:
                    close = candle.close
                    low = min(low,candle.low)
                    high = max(high,candle.high)
                    volume += candle.volume
                else:
                    if open != 0:
                        resampled_candles.append(Candle(index=index,time=time,open=open,high=high,low=low,close=close,volume=volume))
                    index +=1
                    time = candle.time
                    next_time = Utility.get_next_time_resample(time,time_frame=time_frame)
                    open,high,low,close,volume = candle.open, candle.high, candle.low, candle.close, candle.volume
            if open != 0:
                resampled_candles.append(Candle(index=index,time=time,open=open,high=high,low=low,close=close,volume=volume))  
            return resampled_candles
        except Exception as error:
            print(error) 
     
    @staticmethod
    def get_next_time_resample(current_time:datetime, time_frame:TimeFrame=TimeFrame.ONE_DAY):
        match time_frame:
            case TimeFrame.FIFTEEN_MINUTE:
                return current_time + timedelta(minutes=15)
            case TimeFrame.THIRTY_MINUTE:
                return current_time + timedelta(minutes=30)
            case TimeFrame.ONE_HOUR:
                return current_time + timedelta(hours=1)
            case TimeFrame.TWO_HOUR:
                return current_time + timedelta(hours=2)
            case TimeFrame.FOUR_HOUR:
                return current_time + timedelta(hours=4)
            case TimeFrame.ONE_DAY:
                return current_time + timedelta(days=1)
            case TimeFrame.ONE_WEEK:
                return current_time + timedelta(weeks=1)
            case TimeFrame.ONE_MONTH:
                if current_time.month == 12:
                    return datetime(current_time.year+1, 1,1)
                else:
                    return datetime(current_time.year, current_time.month+1,1)
            case defualt:
                return current_time + timedelta(days=1)
        
    @staticmethod
    def get_initial_time_resample(current_time:datetime, time_frame:TimeFrame=TimeFrame.ONE_DAY):
        minutes = (current_time-datetime(current_time.year,current_time.month,current_time.day,9,15)).total_seconds()/60
        match time_frame:
            case TimeFrame.FIFTEEN_MINUTE:
                return current_time 
            case TimeFrame.THIRTY_MINUTE:
                return current_time - timedelta(minutes=minutes%30)
            case TimeFrame.ONE_HOUR:
                return current_time - timedelta(minutes=minutes%60)
            case TimeFrame.TWO_HOUR:
                return current_time - timedelta(minutes=minutes%120)
            case TimeFrame.FOUR_HOUR:
                return current_time - timedelta(minutes=minutes%240)
            case TimeFrame.ONE_DAY:
                return current_time
            case TimeFrame.ONE_WEEK:
                return current_time - timedelta(days=current_time.weekday())                 
            case TimeFrame.ONE_MONTH:
                return datetime(current_time.year, current_time.month,1)
            case defualt:
                return current_time + timedelta(days=1)
        
class Candle():

    # Constructor
    def __init__(self, index: int = 0, time: datetime = datetime.min, open: float = -1, high: float = -1, low: float = -1, close: float = -1, volume:int = -1, hl: str =""):

        # Validating the Input Data
        assert open >= 0, f"open price: {open} is less than or equal to  zero"
        assert high >= 0, f"Open price: {high} is less than or equal to  zero"
        assert low >= 0, f"Open price: {low} is less than or equal to  zero"
        assert close >= 0, f"Open price: {close} is less than or equal to  zero"
        assert index >= 0, f"Candle index: {index} is less than or equal to  zero"

        # Assignment
        self.index = index
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.hl = hl    
     
class TrendLine():
    # Constructor for the Class TrendLines
    def __init__(self, candles:list[Candle], slope: float, intercept: float, hl: str, connects: int):
        self.candles = candles
        self.slope = slope
        self.intercept = intercept
        self.hl = hl
        self.connects = connects
        self.totalconnects = len(candles)
        
class SimTrendLine():
    # Constructor for the Class TrendLines
    def __init__(self,trendline:TrendLine,token:str, time_frame:TimeFrame):
        self.slope = trendline.slope
        self.intercept = trendline.intercept
        self.hl = trendline.hl
        self.connects = trendline.connects
        self.totalconnects = trendline.totalconnects
        self.token = token
        self.time_frame = time_frame
        # self.time = (trendline.candles[-1]-trendline.candles[0].time).total_seconds()/900
        self.candlescount = (trendline.candles[-1].index-trendline.candles[0].index) + 1
        self.mean = 0
        self.median = 0
        self.mode = 0
        self.range = 0
        self.std = 0
        self.skewness = 0
        self.kurtosis = 0
        self.adf_stats = 0
        self.adf_p = 0
        self.adf_5 = 0
        self.adf_1 = 0
        self.adf_10 = 0
        self.kpss_stats = 0
        self.kpss_p = 0
        self.kpss_5 = 0
        self.kpss_1 = 0
        self.kpss_10 = 0
        self.volume_ratio = 0
        self.close_percentage = 0
        self.rrr1 = 0
        self.rrr2 = 0
        self.rrr3 = 0
        self.rrr4 = 0
        self.rrr5 = 0
        self.rrr6 = 0
        self.rrr7 = 0
        self.rrr8 = 0
        self.rrr9 = 0
        self.rrr10 = 0
        
        
     
     
     
     
     
     
     
     
     
     
     
     
     
     
