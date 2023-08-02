from FastAPI.Candle import Candle
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

class PriceData:

    # Constructor
    def __init__(self, highs, lows, candles):

        # initialization
        self.Highs = filter_highs(highs)
        self.Lows = filter_lows(lows)
        self.Candles = candles
        self.HighsForDownTrendLines = []
        self.LowsForUpTrendLines = []
        self.Trendlines = []
        self.TrendlinesToDraw = []
        # List of Highs for down trendlines
        if (self.Highs):
            self.FindHighsForDownTrendLines()
        # List of Lows for Up trendlines
        if (self.Lows):
            self.FindLowsForUpTrendLines()

        daily_logger.info("len of highs for downtrend lines : " + str(len(self.HighsForDownTrendLines)))
        daily_logger.info("len of lows for downtrend lines : " + str(len(self.LowsForUpTrendLines)))
        # Gets all trend lines
        self.GetTrendLines()

    def FindHighsForDownTrendLines(self):
        highs = self.Highs
        self.HighsForDownTrendLines.append(highs[0])
        for i in range(1, len(highs)):
            if (self.CompareCandles(self.HighsForDownTrendLines[-1], highs[i], "H") != -1):
                self.HighsForDownTrendLines.append(highs[i])
            else:
                self.UpdateHighsForDownTrendLines(highs[i])

    # this method Updates the Highs For DownTrend Lines
    def UpdateHighsForDownTrendLines(self, high):
        for i in range(1, len(self.HighsForDownTrendLines)+1):
            if (self.CompareCandles(self.HighsForDownTrendLines[-i], high, "H") != -1):
                temp = i
                break
        for i in range((temp-1)):
            self.HighsForDownTrendLines.pop()
        self.HighsForDownTrendLines.append(high)

    # this method finds the Lows For Upward Trend Lines
    def FindLowsForUpTrendLines(self):
        lows = self.Lows
        self.LowsForUpTrendLines.append(lows[0])
        for i in range(1, len(lows)):
            if (self.CompareCandles(self.LowsForUpTrendLines[-1], lows[i], "L") != 1):
                self.LowsForUpTrendLines.append(lows[i])
            else:
                self.UpdateLowsForUpTrendLines(lows[i])

    # this method Updates the Lows For Upward Trend Lines

    def UpdateLowsForUpTrendLines(self, low):
        for i in range(1, len(self.LowsForUpTrendLines)+1):
            if (self.CompareCandles(self.LowsForUpTrendLines[-i], low, "L") != 1):
                temp = i
                break
        for i in range((temp-1)):
            self.LowsForUpTrendLines.pop()
        self.LowsForUpTrendLines.append(low)

    # This method Compares two candles
    # if candle1 is on equal level to candle2 then, returns 0
    # if candle1 is above candle2 then, returns 1
    # if candle1 is below candle2 then, returns -1
    def CompareCandles(self, candle1, candle2, H_L):
        if (H_L == "H"):
            if (max(candle1.Open, candle1.Close) > candle2.High):
                return 1
            elif (max(candle2.Open, candle2.Close) > candle1.High):
                return -1
            else:
                return 0
        else:
            if (min(candle1.Open, candle1.Close) < candle2.Low):
                return -1
            elif (min(candle2.Open, candle2.Close) < candle1.Low):
                return 1
            else:
                return 0

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
                    candles = [self.HighsForDownTrendLines[i],
                               self.HighsForDownTrendLines[j], self.HighsForDownTrendLines[k]]
                    if (self.IsTrendLinePossible(candles, "H")):
                        self.Trendlines.append(TrendLine(candles,0,0,"H"))
        daily_logger.info("getting higher order trendlines for highs")
        self.GetHigherOrderTrendLines("H")

        for i in range(len(self.LowsForUpTrendLines)):
            for j in range(i+1, len(self.LowsForUpTrendLines)):
                for k in range(j+1, len(self.LowsForUpTrendLines)):
                    candles = [self.LowsForUpTrendLines[i],
                               self.LowsForUpTrendLines[j], self.LowsForUpTrendLines[k]]
                    if (self.IsTrendLinePossible(candles, "L")):
                        self.Trendlines.append(TrendLine(candles,0,0,"L"))
        daily_logger.info("getting higher order trendlines for lows")
        self.GetHigherOrderTrendLines("L")

    # this method returns pricerange if the candles form a trendline with zero slop then pricerange[0] is greater than pricerange[1]

    def EqualCandles(self, candles, H_L):
        priceRange = [float('inf'), float('-inf')]
        if (H_L == "H"):
            for candle in candles:
                priceRange[0] = min(priceRange[0], candle.High)
                priceRange[1] = max(priceRange[1], max(
                    candle.Open, candle.Close))
            return priceRange
        else:
            for candle in candles:
                priceRange[0] = min(priceRange[0], min(
                    candle.Open, candle.Close))
                priceRange[1] = max(priceRange[1], candle.Low)
            return priceRange

    # This method Validates a trendline
    def IsTrendlineValid(self, trendline, H_L):
        if (H_L == 'H'):
            for candle in reversed(self.Highs):
                value = trendline[1]*candle.Index + trendline[2]
                if (max(candle.Open, candle.Close) >= value):
                    return False
                if (candle.Date == trendline[0][0].Date):
                    return True
        else:
            for candle in reversed(self.Lows):
                value = trendline[1]*candle.Index + trendline[2]
                if (max(candle.Open, candle.Close) <= value):
                    return False
                if (candle.Date == trendline[0][0].Date):
                    return True

    def GetHigherOrderTrendLines(self, H_L):
        higherOrderTrendlines = []
        trendlinesToRemove = []
        counter = 1
        skipper = 0
        if H_L == "H":
            # Using this for loop we get possible higher order trendlines of highs which are valid
            for i in range(len(self.Trendlines)-1):
                if self.Trendlines[i].Candles[0].Date == self.Trendlines[i+1].Candles[0].Date and i >= skipper:
                    counter += 1
                else:
                    if counter == 3 and len(self.Trendlines) >= (i+2):
                        if self.Trendlines[i-2].Candles[1].Date == self.Trendlines[i+1].Candles[0].Date:
                            candles = [self.Trendlines[i].Candles[0], self.Trendlines[i+1].Candles[0], self.Trendlines[i].Candles[1], self.Trendlines[i].Candles[2]]
                            pricerange = self.EqualCandles(candles, "H")
                            if (pricerange[0] > pricerange[-1]):
                                higherOrderTrendlines.append(TrendLine(candles, 0, pricerange[0], "H"))
                            else:
                                [Intercept, Slope] = Solver.RunH(candles)
                                if Slope != None and self.IsTrendlineValid([candles, Slope, Intercept], "H"):
                                    higherOrderTrendlines.append(TrendLine(candles, Slope, Intercept, "H"))
                                    for j in range(counter+1):
                                        trendlinesToRemove.append(self.Trendlines[i-j+1])
                        counter = 1
                        skipper = i+2
                    elif counter == 6 and len(self.Trendlines) >= (i+5):
                        if self.Trendlines[i-5].Candles[1].Date == self.Trendlines[i+1].Candles[0].Date and self.Trendlines[i-5].Candles[2].Date == self.Trendlines[i+4].Candles[0].Date:
                            candles = [self.Trendlines[i].Candles[0], self.Trendlines[i+1].Candles[0],
                                       self.Trendlines[i+1].Candles[1], self.Trendlines[i].Candles[1], self.Trendlines[i].Candles[2]]
                            pricerange = self.EqualCandles(candles, "H")
                            if (pricerange[0] > pricerange[-1]):
                                higherOrderTrendlines.append(TrendLine(candles, 0, pricerange[0], "H"))
                            else:
                                [Intercept, Slope] = Solver.RunH(candles)
                                if Slope != None and self.IsTrendlineValid([candles, Slope, Intercept], "H"):
                                    higherOrderTrendlines.append(TrendLine(candles, Slope, Intercept, "H"))
                                    for j in range(counter+4):
                                        trendlinesToRemove.append(self.Trendlines[i-j+4])
                        counter = 1
                        skipper = i+5
                    elif counter == 10 and len(self.Trendlines) >= (i+11):
                        if self.Trendlines[i-9].Candles[1].Date == self.Trendlines[i+1].Candles[0].Date and self.Trendlines[i-9].Candles[2].Date == self.Trendlines[i+7].Candles[0].Date and self.Trendlines[i+1].Candles[2].Date == self.Trendlines[i+10].Candles[0].Date:
                            candles = [self.Trendlines[i].Candles[0], self.Trendlines[i+1].Candles[0], self.Trendlines[i+1].Candles
                                       [1], self.Trendlines[i+1].Candles[2], self.Trendlines[i].Candles[1], self.Trendlines[i].Candles[2]]
                            pricerange = self.EqualCandles(candles, "H")
                            if (pricerange[0] > pricerange[-1]):
                                higherOrderTrendlines.append(TrendLine(candles, 0, pricerange[0], "H"))
                            else:
                                [Intercept, Slope] = Solver.RunH(candles)
                                if Slope != None and self.IsTrendlineValid([candles, Slope, Intercept], "H"):
                                    higherOrderTrendlines.append(TrendLine(candles, Slope, Intercept, "H"))
                                for j in range(counter+10):
                                    trendlinesToRemove.append(self.Trendlines[i-j+10])
                        counter = 1
                        skipper = i + 11
            for trendline in trendlinesToRemove:
                self.Trendlines.remove(trendline)
            if (higherOrderTrendlines):
                better_trendline = Solver.RunHH(higherOrderTrendlines[-1].Candles, self.Candles)
                # initial_guess = [better_trendline.Slope, better_trendline.Intercept]
                # better_trendline = Solver.Generate_Optimal_TrendLine_SLSQP(higherOrderTrendlines[-1].Candles, self.Candles, initial_guess)
                
                
                if better_trendline.Slope != None:
                    self.TrendlinesToDraw.append(better_trendline)
                else:
                    self.TrendlinesToDraw.append(higherOrderTrendlines[-1])
            else:
                for trendline in reversed(self.Trendlines):
                    candles = trendline.Candles
                    pricerange = self.EqualCandles(candles, H_L)
                    if (pricerange[0] > pricerange[1]) and self.IsTrendlineValid([candles, 0, pricerange[0]], H_L):
                        self.TrendlinesToDraw.append(TrendLine(candles, 0, pricerange[0], "H"))
                        break
                    else: 
                        trendline = Solver.RunHH(candles, self.Candles)
                        if trendline.Slope != None and self.IsTrendlineValid([trendline.Candles, trendline.Slope, trendline.Intercept], H_L):
                            self.TrendlinesToDraw.append(trendline)
                            break

        if H_L == "L":
            # Using this for loop we get possible higher order trendlines of lows which are valid
            for i in range(len(self.Trendlines)-1):
                if self.Trendlines[i].Candles[0].Date == self.Trendlines[i+1].Candles[0].Date and i >= skipper:
                    counter += 1
                else:
                    if counter == 3 and len(self.Trendlines) >= (i+2):
                        if self.Trendlines[i-2].Candles[1].Date == self.Trendlines[i+1].Candles[0].Date:
                            candles = [self.Trendlines[i].Candles[0], self.Trendlines[i+1].Candles[0], self.Trendlines[i].Candles[1], self.Trendlines[i].Candles[2]]
                            pricerange = self.EqualCandles(candles, "L")
                            if (pricerange[0] > pricerange[-1]):
                                higherOrderTrendlines.append(TrendLine(candles, 0, pricerange[1], "L"))
                            else:
                                [Intercept, Slope] = Solver.RunL(candles)
                                if Slope != None and self.IsTrendlineValid([candles, Slope, Intercept], "L"):
                                    higherOrderTrendlines.append(TrendLine(candles, Slope, Intercept, "L"))
                                    for j in range(counter+1):
                                        trendlinesToRemove.append(
                                            self.Trendlines[i-j+1])
                        counter = 1
                        skipper = i + 2
                    elif counter == 6 and len(self.Trendlines) >= (i+5):
                        if self.Trendlines[i-5].Candles[1].Date == self.Trendlines[i+1].Candles[0].Date and self.Trendlines[i-5].Candles[2].Date == self.Trendlines[i+4].Candles[0].Date:
                            candles = [self.Trendlines[i].Candles[0], self.Trendlines[i+1].Candles[0],
                                       self.Trendlines[i+1].Candles[1], self.Trendlines[i].Candles[1], self.Trendlines[i].Candles[2]]
                            pricerange = self.EqualCandles(candles, "L")
                            if (pricerange[0] > pricerange[-1]):
                                higherOrderTrendlines.append(TrendLine(candles, 0, pricerange[1], "L"))
                            else:
                                [Intercept, Slope] = Solver.RunL(candles)
                                if Slope != None and self.IsTrendlineValid([candles, Slope, Intercept], "L"):
                                    higherOrderTrendlines.append(TrendLine(candles, Slope, Intercept, "L"))
                                    for j in range(counter+4):
                                        trendlinesToRemove.append(
                                            self.Trendlines[i-j+4])
                        counter = 1
                        skipper = i + 5
                    elif counter == 10 and len(self.Trendlines) >= (i+11):
                        if self.Trendlines[i-9].Candles[1].Date == self.Trendlines[i+1].Candles[0].Date and self.Trendlines[i-9].Candles[2].Date == self.Trendlines[i+7].Candles[0].Date and self.Trendlines[i+1].Candles[2].Date == self.Trendlines[i+10].Candles[0].Date:
                            candles = [self.Trendlines[i].Candles[0], self.Trendlines[i+1].Candles[0], self.Trendlines[i+1].Candles
                                       [1], self.Trendlines[i+1].Candles[2], self.Trendlines[i].Candles[1], self.Trendlines[i].Candles[2]]
                            pricerange = self.EqualCandles(candles, "L")
                            if (pricerange[0] > pricerange[-1]):
                                higherOrderTrendlines.append(TrendLine(candles, 0, pricerange[1], "L"))
                            else:
                                [Intercept, Slope] = Solver.RunL(candles)
                                if Slope != None and self.IsTrendlineValid([candles, Slope, Intercept], "L"):
                                    higherOrderTrendlines.append(TrendLine(candles, Slope, Intercept, "L"))
                                    for j in range(counter+10):
                                        trendlinesToRemove.append(
                                            self.Trendlines[i-j+10])
                        counter = 1
                        skipper = i + 11
            for trendline in trendlinesToRemove:
                self.Trendlines.remove(trendline)
            if (higherOrderTrendlines):
                self.TrendlinesToDraw.append(higherOrderTrendlines[-1])
            else:
                for trendline in reversed(self.Trendlines):
                    candles = trendline.Candles
                    pricerange = self.EqualCandles(candles, H_L)
                    if (pricerange[0] > pricerange[1]) and self.IsTrendlineValid([candles, 0, pricerange[1]], H_L):
                            self.TrendlinesToDraw.append(TrendLine(candles, 0, pricerange[1], "L"))
                            break
                    else:
                        [Intercept, Slope] = Solver.RunL(candles)
                        if Slope != None and self.IsTrendlineValid([candles, Slope, Intercept], H_L):
                            self.TrendlinesToDraw.append(TrendLine(candles, Slope, Intercept, "L"))
                            break

