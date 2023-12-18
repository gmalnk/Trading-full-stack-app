import React, { createContext, useState } from "react";

export const Context = createContext();

export default function AppContextProvider(props) {
  const [searchActive, setSearchActive] = useState(false);
  const [showTrendline, setShowTrendline] = useState(true);
  const [timeFrame, setTimeFrame] = useState("ONE_HOUR");
  const [stockToken, setStockToken] = useState(474);
  const [tradeBoxActive, setTradeBoxActive] = useState(false);
  const [linesData, setLinesData] = useState("");
  const [stockListCategory, setStockListCategory] = useState("all");
  const [stockListSort, setStockListSort] = useState("alphabets");
  const [logedIn, setLogedIn] = useState(false);

  return (
    <Context.Provider
      value={{
        showTrendline,
        setShowTrendline,
        timeFrame,
        setTimeFrame,
        stockToken,
        setStockToken,
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
        logedIn,
        setLogedIn,
      }}
    >
      {props.children}
    </Context.Provider>
  );
}
