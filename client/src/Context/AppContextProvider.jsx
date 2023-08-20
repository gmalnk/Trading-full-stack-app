import React, { createContext, useState } from "react";

export const Context = createContext();

export default function AppContextProvider(props) {
  const [searchActive, setSearchActive] = useState(false);
  const [showTrendline, setShowTrendline] = useState(true);
  const [timeFrame, setTimeFrame] = useState("ONE_HOUR");
  const [stockToken, setStockToken] = useState(474);
  const [stockDict, setStockDict] = useState({});
  const [stockList, setStockList] = useState([]);
  const [tradeBoxActive, setTradeBoxActive] = useState(false);
  const [linesData, setLinesData] = useState("");
  const [stockListCategory, setStockListCategory] = useState("all");
  const [stockListSort, setStockListSort] = useState("alphabets");

  return (
    <Context.Provider
      value={{
        showTrendline,
        setShowTrendline,
        timeFrame,
        setTimeFrame,
        stockToken,
        setStockToken,
        stockDict,
        setStockDict,
        stockList,
        setStockList,
        searchActive,
        setSearchActive,
        tradeBoxActive,
        setTradeBoxActive,
        linesData,
        setLinesData,
        stockListCategory,
        setStockListCategory,
        stockListSort,
        setStockListSort,
      }}
    >
      {props.children}
    </Context.Provider>
  );
}
