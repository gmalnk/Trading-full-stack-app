from FastAPI.Constants import *
from FastAPI.Solver.Solver import Solver
from FastAPI.Modules.Logging import daily_logger
from FastAPI.Modules.Utility import Utility, Candle, TrendLine
#  Boss for Price Data and Trendlines
class PriceAction:

    # Constructor
    def __init__(self, highs, lows, candles, update_uptrendline, update_downtrendline):

        # initialization
        self.Candles = candles
        self.Highs = []
        self.Lows = []
        self.HighsForDownTrendLines = []
        self.LowsForUpTrendLines = []
        self.Trendlines = []
        self.TrendlinesToDraw = []
        self.AllTrendlineCombinationList = []
        self.ThirdOrderTrendlineCombinationsSet=set()
        
        # filtering Highs and Lows 
        if update_downtrendline:
            self.Highs = Utility.filter_highs(highs)
        if update_uptrendline:
            self.Lows = Utility.filter_lows(lows)
        
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
            if self.CompareCandles(high, self.HighsForDownTrendLines[-1],"h") != CandleComparer.Lower:
                self.HighsForDownTrendLines.append(high)
        self.HighsForDownTrendLines.reverse()

    # this method finds the Lows For Upward Trend Lines
    def FindLowsForUpTrendLines(self):
        self.LowsForUpTrendLines.append(self.Lows[-1])
        for low in reversed(self.Lows[:-1]):
            if (self.CompareCandles(low, self.LowsForUpTrendLines[-1], "l") != CandleComparer.Higher):
                self.LowsForUpTrendLines.append(low)
        self.LowsForUpTrendLines.reverse()

    # This method Compares two candles
    # if candle1 is on equal level to candle2 then, returns Equal
    # if candle1 is above candle2 then, returns Higher
    # if candle1 is below candle2 then, returns Lower
    def CompareCandles(self, candle1, candle2, H_L):
        if (H_L == "h"):
            if (max(candle1.open, candle1.close) > candle2.high):
                return CandleComparer.Higher
            elif (max(candle2.open, candle2.close) > candle1.high):
                return CandleComparer.Lower
            else:
                return CandleComparer.Equal
        else:
            if (min(candle1.open, candle1.close) < candle2.low):
                return CandleComparer.Lower
            elif (min(candle2.open, candle2.close) < candle1.low):
                return CandleComparer.Higher
            else:
                return CandleComparer.Equal

    # this method finds if a trendline is possible for given three candles
    def IsTrendLinePossible(self, candles, H_L):
        candle3 = candles[-1]
        if (H_L == "h"):
            slopeRange = Solver.SlopeRange(candles[0], candles[1], "h")
            if (max(candle3.open, candle3.close) > slopeRange[0]*(candle3.index - candles[0].index) + max(candles[0].open, candles[0].close)):
                return False
            if (candle3.high < slopeRange[1]*(candle3.index - candles[0].index) + candles[0].high):
                return False
        elif (H_L == "l"):
            slopeRange = Solver.SlopeRange(candles[0], candles[1], "l")
            if (candle3.low > slopeRange[0]*(candle3.index - candles[0].index) + candles[0].low):
                return False
            if (min(candle3.open, candle3.close) < slopeRange[1]*(candle3.index - candles[0].index) + min(candles[0].open, candles[0].close)):
                return False
        return True

    # This method is responsible for getting the trendlines
    def GetTrendLines(self):
        for i in range(len(self.HighsForDownTrendLines)):
            for j in range(i+1, len(self.HighsForDownTrendLines)):
                for k in range(j+1, len(self.HighsForDownTrendLines)):
                    if (self.IsTrendLinePossible([self.HighsForDownTrendLines[i], self.HighsForDownTrendLines[j], self.HighsForDownTrendLines[k]], "h")):
                        self.ThirdOrderTrendlineCombinationsSet.add((i,j,k))
                        self.AllTrendlineCombinationList.append([i,j,k])
        daily_logger.info("getting higher order trendlines for highs")
        self.GetSuperTrendLinesFromComboAlgo("h")
        
        # for i in range(len(self.LowsForUpTrendLines)):
        #     for j in range(i+1, len(self.LowsForUpTrendLines)):
        #         for k in range(j+1, len(self.LowsForUpTrendLines)):
        #             if (self.IsTrendLinePossible([self.LowsForUpTrendLines[i], self.LowsForUpTrendLines[j], self.LowsForUpTrendLines[k]], "l")):
        #                 self.ThirdOrderTrendlineCombinationsSet.add((i,j,k))
        #                 self.AllTrendlineCombinationList.append([i,j,k])
        # daily_logger.info("getting higher order trendlines for lows")
        # self.GetSuperTrendLinesFromComboAlgo("l")
        

    # this method returns pricerange if the candles form a trendline with zero slop then pricerange[0] is greater than pricerange[1]

    def EqualCandles(self, candles, H_L):
        priceRange = [MAX_NUM, MIN_NUM]
        if (H_L == "h"):
            for candle in candles:
                priceRange[0] = min(priceRange[0], candle.high)
                priceRange[1] = max(priceRange[1], max(
                    candle.open, candle.close))
                if priceRange[0] < priceRange[1]:
                    return priceRange
        else:
            for candle in candles:
                priceRange[0] = min(priceRange[0], min(
                    candle.open, candle.close))
                priceRange[1] = max(priceRange[1], candle.low)
                if priceRange[0] < priceRange[1]:
                    return priceRange
        return priceRange
    
    # returns the value of the trendline at the given index (y= m * x + c)
    def GetTrendlineValue(self, trendline:TrendLine, index:int)->float:
        return trendline.slope*index + trendline.intercept

    # This method Validates a trendline
    def IsTrendlineValid(self, trendline:TrendLine):
        if (trendline.hl == 'h'):             
            for candle in trendline.candles:
                value = self.GetTrendlineValue(trendline, candle.index)
                if TOLERANCE < value - candle.high:
                    return False
            for candle in reversed(self.Highs + self.Candles[-5:]):
                value = self.GetTrendlineValue(trendline, candle.index)
                if (max(candle.open, candle.close) - value > TOLERANCE):
                    return False
                if (candle.time == trendline.candles[0].time):
                    return True
        else:
            for candle in trendline.candles:
                value = self.GetTrendlineValue(trendline, candle.index)
                if candle.low - value > TOLERANCE:
                    return False
            for candle in reversed(self.Lows + self.Candles[-5:]):
                value = self.GetTrendlineValue(trendline, candle.index)
                if ( TOLERANCE < value - min(candle.open, candle.close)):
                    return False
                if (candle.time == trendline.candles[0].time):
                    return True

    def GetSuperTrendLinesFromComboAlgo(self, H_L):
        
        # logic to get the highre order trendlines or the super trendlines    
        prev_map=self.ThirdOrderTrendlineCombinationsSet
        present_map=set()
        candles = self.HighsForDownTrendLines if H_L == "h" else self.LowsForUpTrendLines
        n=len(candles)
        indexes_list=range(n)
        for r in range(4,n+1):
            is_forming=False
            combo_list=Utility.generate_combinations(indexes_list,r)
            for combo in combo_list:
                combo=tuple(combo)
                prev_candles=combo[:-1]
                curr_candle=combo[-1]
                if (prev_candles not in prev_map):
                    continue
                list_nC2_prevCandles_combinations=Utility.generate_combinations(prev_candles,2)
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
                if pricerange[0] > pricerange[1] and self.IsTrendlineValid(TrendLine(comboCandles, 0, pricerange[1], H_L, len(comboCandles))):
                        self.TrendlinesToDraw.append(TrendLine(comboCandles, 0, pricerange[1], H_L,len(comboCandles)))
                        foundTrendline = True
                        break
                else:
                    better_trendline = Solver.RunHH(comboCandles, self.Candles) if H_L == "h" else Solver.RunLL(comboCandles, self.Candles)
                    if better_trendline.slope != None and self.IsTrendlineValid(better_trendline):
                        self.TrendlinesToDraw.append(better_trendline)
                        foundTrendline = True
                        break
        if not foundTrendline:
            daily_logger.warning("not found any combination" + str(self.AllTrendlineCombinationList))
        self.AllTrendlineCombinationList = []
        self.ThirdOrderTrendlineCombinationsSet = set()
   
   
   
   
   
   
   
   
   
   
   
   