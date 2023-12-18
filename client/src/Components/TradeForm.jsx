import React, {
  forwardRef,
  useContext,
  useEffect,
  useImperativeHandle,
  useState,
} from "react";
import { Context } from "../Context/AppContextProvider";
import AxiosAPI from "../API/AxiosAPI";
import { stocksDict } from "../Constants/constants";

const TradeForm = forwardRef(({ removeTradeBox }, ref) => {
  const [tradeDirection, setTradeDirection] = useState("");
  const [numOfShares, setNumOfShares] = useState(0);
  const [takeProfit, setTakeProfit] = useState(0);
  const [stopLoss, setStopLoss] = useState(0);
  const [tradeOnCandleClose, setTradeOnCandleClose] = useState(false);
  const [tradeOnCandleOpen, setTradeOnCandleOpen] = useState(false);
  const { timeFrame, stockToken, setTradeBoxActive, linesData } =
    useContext(Context);

  useImperativeHandle(ref, () => ({
    removeTradeBox() {
      initializeAllStatesOfTradeFormComponent(true);
    },
  }));

  const regex = /^[0-9]*\.?[0-9]*$/;

  const handleNumOfSharesChange = (e) => {
    if (regex.test(e.target.value)) {
      setNumOfShares(e.target.value);
    }
  };

  const handleTakeProfitChange = (e) => {
    if (regex.test(e.target.value)) {
      setTakeProfit(e.target.value);
    }
  };

  const handleStopLossChange = (e) => {
    if (regex.test(e.target.value)) {
      setStopLoss(e.target.value);
    }
  };

  const handleTradeOnCandleCloseChange = (e) => {
    setTradeOnCandleClose(e.target.checked);
  };

  const handletradeOnCandleOpenChange = (e) => {
    setTradeOnCandleOpen(e.target.checked);
  };

  const handleOptionChange = (e) => {
    setTradeDirection(e.target.value);
  };

  const initializeAllStatesOfTradeFormComponent = (makeTradeBoxInActive) => {
    setNumOfShares(0);
    setTakeProfit(0);
    setStopLoss(0);
    setTradeOnCandleClose(false);
    setTradeOnCandleOpen(false);
    setTradeDirection("");
    if (makeTradeBoxInActive === true) {
      setTradeBoxActive(false);
    }
  };

  const handleOnClickSubmit = () => {
    if (
      !(
        tradeDirection === "" ||
        numOfShares === 0 ||
        takeProfit === 0 ||
        stopLoss === 0 ||
        !(tradeOnCandleClose || tradeOnCandleOpen)
      )
    ) {
      //api call
      console.log("api call");
      AxiosAPI.post("/tradedetails", {
        params: {
          stockToken,
          timeFrame,
          tradeDirection,
          numOfShares,
          takeProfit,
          stopLoss,
          tradeOnCandleClose,
          tradeOnCandleOpen,
        },
      });
    }
    initializeAllStatesOfTradeFormComponent(true);
  };

  useEffect(() => {
    initializeAllStatesOfTradeFormComponent(false);
  }, [timeFrame, stockToken]);

  return (
    <div>
      <div className="row px-3 py-2">
        <div className="col">{stocksDict[stockToken]}</div>
        <div className="col">{timeFrame}</div>
      </div>
      <form>
        <select className="form-select" onChange={handleOptionChange}>
          <option selected disabled>
            Choose TrendLine To Trade
          </option>
          {linesData.includes("H") && (
            <option value="H">Trade Resistance Line</option>
          )}
          {linesData.includes("L") && (
            <option value="L">Trade Support Line</option>
          )}
        </select>
        <div className="form-group">
          <label htmlFor="numOfShares">No of Shares:</label>
          <input
            type="text"
            pattern="[0-9]*\.?[0-9]*"
            className="form-control"
            value={numOfShares}
            onChange={handleNumOfSharesChange}
            id="numOfShares"
          />
        </div>
        <div className="form-group">
          <label htmlFor="takeProfit">Take Profit:</label>
          <input
            type="text"
            pattern="[0-9]*\.?[0-9]*"
            className="form-control"
            value={takeProfit}
            onChange={handleTakeProfitChange}
            id="takeProfit"
          />
        </div>
        <div className="form-group">
          <label htmlFor="stopLoss">Stop Loss:</label>
          <input
            type="text"
            pattern="[0-9]*\.?[0-9]*"
            className="form-control"
            value={stopLoss}
            onChange={handleStopLossChange}
            id="stopLoss"
          />
        </div>
        <div className="form-check">
          <input
            className="form-check-input"
            type="checkbox"
            checked={tradeOnCandleClose}
            onChange={handleTradeOnCandleCloseChange}
            id="tradeOnCandleClose"
          />
          <label className="form-check-label" htmlFor="tradeOnCandleClose">
            Trade on Candle Close
          </label>
        </div>
        <div className="form-check">
          <input
            className="form-check-input"
            type="checkbox"
            checked={tradeOnCandleOpen}
            onChange={handletradeOnCandleOpenChange}
            id="tradeOnCandleOpen"
          />
          <label className="form-check-label" htmlFor="tradeOnCandleOpen">
            Trade on Candle Open
          </label>
        </div>
        <button
          type="submit"
          className="btn btn-primary"
          onClick={handleOnClickSubmit}
        >
          Submit
        </button>
      </form>
    </div>
  );
});

export default TradeForm;
