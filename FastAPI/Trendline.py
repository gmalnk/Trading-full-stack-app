class TrendLine:
    # Constructor for the Class TrendLines
    def __init__(self, candles, slope, intercept, hl):
        self.Candles = candles
        self.Slope = slope
        self.Intercept = intercept
        self.HL = hl
        self.NoOfPoints = len(candles)