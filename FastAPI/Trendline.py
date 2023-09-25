from FastAPI.Candle import * 
class TrendLine:
    # Constructor for the Class TrendLines
    def __init__(self, candles:list[Candle], slope: float, intercept: float, hl: str, connects: int):
        self.Candles = candles
        self.Slope = slope
        self.Intercept = intercept
        self.HL = hl
        self.Connects = connects
        self.TotalConnects = len(candles)