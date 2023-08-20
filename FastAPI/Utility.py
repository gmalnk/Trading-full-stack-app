from FastAPI.Candle import Candle
from FastAPI.tradeline_property import *
from FastAPI.Constants import *
from FastAPI.fast_api_lib_if import *
from FastAPI.config import *
from datetime import datetime
from datetime import timedelta
from datetime import date
from FastAPI.Solver import Solver
from FastAPI.Trendline import TrendLine
import pandas as pd
# returns True if the given candle is Local Maximum else False


def IsMax(candles, i):
    if max(candles[i-5].High, candles[i-4].High, candles[i-3].High, candles[i-2].High, candles[i-1].High, candles[i].High, candles[i+1].High, candles[i+2].High, candles[i+3].High, candles[i+4].High, candles[i+5].High) == candles[i].High:
        return True
    else:
        return False

# returns True if the given candle is Local minimum else False


def IsMin(candles, i):
    if min(candles[i-5].Low, candles[i-4].Low, candles[i-3].Low, candles[i-2].Low, candles[i-1].Low, candles[i].Low, candles[i+1].Low, candles[i+2].Low, candles[i+3].Low, candles[i+4].Low, candles[i+5].Low) == candles[i].Low:
        return True
    else:
        return False


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
        if htemp == 0 and IsMax(candles, i):
            htemp = 6
            high_low += "high"
        if ltemp == 0 and IsMin(candles, i):
            ltemp = 6
            high_low += "low"
        candles[i].High_Low = high_low
        if (high_low != ""):
            high_low_candles.append(candles[i])
    daily_logger.info("length of high low cangles : " + str(len(high_low_candles)))
    if len(high_low_candles) <= 1:
        return high_low_candles
    high_low_candles = filter_highs_lows(high_low_candles)
    return high_low_candles


def filter_highs_lows(candles):
    filtered_highs_lows = []
    max_candle = Candle(0, 0, 0, datetime.today(), 0, 0, 0, 0, '')
    min_candle = Candle(0, 0, 0, datetime.today(), float(
        'inf'), float('inf'), float('inf'), float('inf'), '')
    if (len(candles) > 0):
        for candle in candles:
            if (candle.High_Low.find('high') != -1 and candle.High > max_candle.High):
                max_candle = candle
            if (candle.High_Low.find('low') != -1 and candle.Low < min_candle.Low):
                min_candle = candle
    else:
        return []
    daily_logger.info("max candle index : " + str(max_candle.Index))
    daily_logger.info("min candle index : " + str(min_candle.Index))
    for candle in candles:
        if candle.High_Low == 'high' and candle.Index >= max_candle.Index:
            filtered_highs_lows.append(candle)
        if candle.High_Low == 'low' and candle.Index >= min_candle.Index:
            filtered_highs_lows.append(candle)
        if candle.High_Low == "highlow":
            if candle.Index >= max_candle.Index and candle.Index >= min_candle.Index:
                filtered_highs_lows.append(candle)
                continue
            if (candle.Index >= max_candle.Index):
                candle.High_Low = "high"
                filtered_highs_lows.append(candle)
            if (candle.Index >= min_candle.Index):
                candle.High_Low = "low"
                filtered_highs_lows.append(candle)
    return filtered_highs_lows

def filter_highs(candles):
    if (not candles):
        return []
    filtered_highs = []
    max_candle = Candle(0, 0, 0, datetime.today(), 0, 0, 0, 0, '')
    for candle in candles:
        # todo -- second condition high > high is to be replaced with the compare candles 
        if candle.High > max_candle.High and candle.Low > max_candle.High:
            max_candle = candle
    daily_logger.info("max candle index : " + str(max_candle.Index))
    filtered_highs = [x for x in candles if x.Index >= max_candle.Index]
    return filtered_highs

def filter_lows(candles):
    if (not candles):
        return []
    filtered_lows = []
    min_candle = Candle(0, 0, 0, datetime.today(), float(
        'inf'), float('inf'), float('inf'), float('inf'), '')
    for candle in candles:
        # todo -- condition high > high is to be replaced with the compare candles 
        if (candle.Low < min_candle.Low):
            min_candle = candle
    daily_logger.info("min candle index : " + str(min_candle.Index))
    filtered_lows = [x for x in candles if x.Index >= min_candle.Index]
    return filtered_lows


# this method converts ltp  data to pandas ohlc data
def convert_ltp_to_ohlc(time_frame, rows):
    try:
        df = pd.DataFrame(rows, columns=['id', 'token', 'time_stamp', 'ltp'])
        df['Date'] = df['time_stamp']
        df = df.set_index('Date')
        df = df['ltp'].resample(time_frame).ohlc(_method='ohlc')
        return df
    except (Exception) as error:
        daily_logger.error("Failed at convert_data_timeframe method error mesage: " + str(error))


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
    except (Exception) as error:
        daily_logger.error("Failed at convert_data_timeframe method error mesage: " + str(error))


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


# we dont analyse all the data for all time frames, we limit out data for analysis hence 
# this method provides the start time of the analysis based on the time frame
def get_starttime_of_analysis(time_frame):
    match time_frame:
        case 'FIFTEEN_MINUTE':
            return datetime.today()-timedelta(days=31)
        case 'THIRTY_MINUTE':
            return datetime.today()-timedelta(days=61)
        case 'ONE_HOUR':
            return datetime.today()-timedelta(weeks=14)
        case 'TWO_HOUR':
            return datetime.today()-timedelta(weeks=28)
        case 'FOUR_HOUR':
            return datetime(date.today().year-1, date.today().month, date.today().day)
        case 'ONE_DAY':
            return datetime(date.today().year-2, date.today().month, date.today().day)
        case 'ONE_WEEK':
            return datetime(date.today().year-20, date.today().month, date.today().day)
        case 'ONE_MONTH':
            return datetime(date.today().year-20, date.today().month, date.today().day)
        case default:
            return datetime.today()

def get_tokens(stockListCategory):
    match stockListCategory:
        case "all":
            return list(ALL_TOKENS.keys())
        case "n50":
            return list(TOKENS_50.keys())
        case "n100":
            return list(TOKENS_100.keys())
        case "n200":
            return list(TOKENS_200.keys())
        case "n500":
            return list(TOKENS_500.keys())
        case "n1000":
            return list(TOKENS_1000.keys())
        case default:
            return list(ALL_TOKENS.keys())

#  Boss for Price Data and Trendlines
class PriceData:

    # Constructor
    def __init__(self, highs, lows, candles):

        # initialization
        self.Candles = candles
        self.HighsForDownTrendLines = []
        self.LowsForUpTrendLines = []
        self.Trendlines = []
        self.TrendlinesToDraw = []
        self.AllTrendlineCombinationList = []
        self.ThirdOrderTrendlineCombinationsSet=set()
        
        # filtering Highs and Lows 
        self.Highs = filter_highs(highs)
        self.Lows = filter_lows(lows)
        
        # getting List of Highs for down trendlines
        if (self.Highs):
            self.FindHighsForDownTrendLines()
        daily_logger.info("len of highs for downtrend lines : " + str(len(self.HighsForDownTrendLines)))
        
        # getting List of Lows for Up trendlines
        if (self.Lows):
            self.FindLowsForUpTrendLines()
        daily_logger.info("len of lows for uptrend lines : " + str(len(self.LowsForUpTrendLines)))
        
        # Gets all trend lines
        self.GetTrendLines()


    # this method finds the Highs For Downward Trend Lines
    def FindHighsForDownTrendLines(self):
        self.HighsForDownTrendLines.append(self.Highs[-1])
        for high in reversed(self.Highs[:-1]):
            if self.CompareCandles(high, self.HighsForDownTrendLines[-1],"H") != CandleComparer.Lower:
                self.HighsForDownTrendLines.append(high)
        self.HighsForDownTrendLines.reverse()

    # this method finds the Lows For Upward Trend Lines
    def FindLowsForUpTrendLines(self):
        self.LowsForUpTrendLines.append(self.Lows[-1])
        for low in reversed(self.Lows[:-1]):
            if (self.CompareCandles(low, self.LowsForUpTrendLines[-1], "L") != CandleComparer.Higher):
                self.LowsForUpTrendLines.append(low)
        self.LowsForUpTrendLines.reverse()

    # This method Compares two candles
    # if candle1 is on equal level to candle2 then, returns Equal
    # if candle1 is above candle2 then, returns Higher
    # if candle1 is below candle2 then, returns Lower
    def CompareCandles(self, candle1, candle2, H_L):
        if (H_L == "H"):
            if (max(candle1.Open, candle1.Close) > candle2.High):
                return CandleComparer.Higher
            elif (max(candle2.Open, candle2.Close) > candle1.High):
                return CandleComparer.Lower
            else:
                return CandleComparer.Equal
        else:
            if (min(candle1.Open, candle1.Close) < candle2.Low):
                return CandleComparer.Lower
            elif (min(candle2.Open, candle2.Close) < candle1.Low):
                return CandleComparer.Higher
            else:
                return CandleComparer.Equal

    # this method finds if a trendline is possible for given three candles
    def IsTrendLinePossible(self, candles, H_L):
        candle3 = candles[-1]
        if (H_L == "H"):
            slopeRange = Solver.SlopeRange(candles[0], candles[1], "H")
            if (max(candle3.Open, candle3.Close) > slopeRange[0]*(candle3.Index - candles[0].Index) + max(candles[0].Open, candles[0].Close)):
                return False
            if (candle3.High < slopeRange[1]*(candle3.Index - candles[0].Index) + candles[0].High):
                return False
        elif (H_L == "L"):
            slopeRange = Solver.SlopeRange(candles[0], candles[1], "L")
            if (candle3.Low > slopeRange[0]*(candle3.Index - candles[0].Index) + candles[0].Low):
                return False
            if (min(candle3.Open, candle3.Close) < slopeRange[1]*(candle3.Index - candles[0].Index) + min(candles[0].Open, candles[0].Close)):
                return False
        return True

    # This method is responsible for getting the trendlines
    def GetTrendLines(self):
        for i in range(len(self.HighsForDownTrendLines)):
            for j in range(i+1, len(self.HighsForDownTrendLines)):
                for k in range(j+1, len(self.HighsForDownTrendLines)):
                    if (self.IsTrendLinePossible([self.HighsForDownTrendLines[i], self.HighsForDownTrendLines[j], self.HighsForDownTrendLines[k]], "H")):
                        self.ThirdOrderTrendlineCombinationsSet.add((i,j,k))
                        self.AllTrendlineCombinationList.append([i,j,k])
        daily_logger.info("getting higher order trendlines for highs")
        self.GetSuperTrendLinesFromComboAlgo("H")
        
        for i in range(len(self.LowsForUpTrendLines)):
            for j in range(i+1, len(self.LowsForUpTrendLines)):
                for k in range(j+1, len(self.LowsForUpTrendLines)):
                    if (self.IsTrendLinePossible([self.LowsForUpTrendLines[i], self.LowsForUpTrendLines[j], self.LowsForUpTrendLines[k]], "L")):
                        self.ThirdOrderTrendlineCombinationsSet.add((i,j,k))
                        self.AllTrendlineCombinationList.append([i,j,k])
        daily_logger.info("getting higher order trendlines for lows")
        self.GetSuperTrendLinesFromComboAlgo("L")
        

    # this method returns pricerange if the candles form a trendline with zero slop then pricerange[0] is greater than pricerange[1]

    def EqualCandles(self, candles, H_L):
        priceRange = [MAX_NUM, MIN_NUM]
        if (H_L == "H"):
            for candle in candles:
                priceRange[0] = min(priceRange[0], candle.High)
                priceRange[1] = max(priceRange[1], max(
                    candle.Open, candle.Close))
                if priceRange[0] < priceRange[1]:
                    return priceRange
        else:
            for candle in candles:
                priceRange[0] = min(priceRange[0], min(
                    candle.Open, candle.Close))
                priceRange[1] = max(priceRange[1], candle.Low)
                if priceRange[0] < priceRange[1]:
                    return priceRange
        return priceRange
    
    # returns the value of the trendline at the given index (y= m * x + c)
    def GetTrendlineValue(self, trendline:TrendLine, index:int)->float:
        return trendline.Slope*index+ trendline.Intercept

    # This method Validates a trendline
    def IsTrendlineValid(self, trendline:TrendLine):
        if (trendline.HL == 'H'):
            for candle in trendline.Candles:
                value = self.GetTrendlineValue(trendline, candle.Index)
                if candle.High < value:
                    return False
            for candle in reversed(self.Highs):
                value = self.GetTrendlineValue(trendline, candle.Index)
                if (max(candle.Open, candle.Close) >= value):
                    return False
                if (candle.Date == trendline.Candles[0].Date):
                    return True
        else:
            for candle in trendline.Candles:
                value = self.GetTrendlineValue(trendline, candle.Index)
                if candle.Low > value:
                    return False
            for candle in reversed(self.Lows):
                value = self.GetTrendlineValue(trendline, candle.Index)
                if (max(candle.Open, candle.Close) <= value):
                    return False
                if (candle.Date == trendline.Candles[0].Date):
                    return True

    def GetSuperTrendLinesFromComboAlgo(self, H_L):
        
        # logic to get the highre order trendlines or the super trendlines    
        prev_map=self.ThirdOrderTrendlineCombinationsSet
        self.ThirdOrderTrendlineCombinationsSet = set()
        present_map=set()
        candles = self.HighsForDownTrendLines if H_L == "H" else self.LowsForUpTrendLines
        n=len(candles)
        indexes_list=range(n)
        for r in range(4,n+1):
            is_forming=False
            combo_list=generate_combinations(indexes_list,r)
            for combo in combo_list:
                combo=tuple(combo)
                prev_candles=combo[:-1]
                curr_candle=combo[-1]
                if (prev_candles not in prev_map):
                    continue
                list_nC2_prevCandles_combinations=generate_combinations(prev_candles,2)
                current_highercombo_forms_trendline=True
                for nC2_combo in list_nC2_prevCandles_combinations:
                    nC2_combo=tuple(nC2_combo)
                    if (nC2_combo[0],nC2_combo[1],curr_candle) not in self.ThirdOrderTrendlineCombinationsSet:
                        current_highercombo_forms_trendline=False
                        break
                if current_highercombo_forms_trendline:
                    present_map.add(combo)
                    self.AllTrendlineCombinationList.append(list(combo))
                    is_forming=True
            if is_forming==False:
                break
            prev_map=present_map.copy()
            present_map=set()
            
            
        # getting the best trendline using the optimiser from the combinations computed above 
        foundTrendline = False
        for combo in reversed(self.AllTrendlineCombinationList):
                comboCandles = [candles[i] for i in combo]
                pricerange = self.EqualCandles(comboCandles, H_L)
                if pricerange[0] > pricerange[1] and self.IsTrendlineValid([comboCandles, 0, pricerange[1]], H_L):
                        self.TrendlinesToDraw.append(TrendLine(comboCandles, 0, pricerange[1], H_L))
                        foundTrendline = True
                        break
                else:
                    better_trendline = Solver.RunHH(comboCandles, self.Candles) if H_L == "H" else Solver.RunLL(comboCandles, self.Candles)
                    if better_trendline.Slope != None and self.IsTrendlineValid(TrendLine(comboCandles, better_trendline.Slope, better_trendline.Intercept, H_L)):
                        self.TrendlinesToDraw.append(TrendLine(comboCandles, better_trendline.Slope, better_trendline.Intercept, H_L))
                        foundTrendline = True
                        break
        if not foundTrendline:
            daily_logger.error("not found any combination" + str(self.AllTrendlineCombinationList))
        self.AllTrendlineCombinationList = []