import React, { createContext, useState } from 'react'


export const Context = createContext()


export default function AppContextProvider(props) {
  const [searchActive, setSearchActive] = useState(false);
  const [showTrendline, setShowTrendline] = useState(true);
  const [timeFrame, setTimeFrame] = useState("ONE_HOUR");
  const [stockToken, setStockToken] = useState(474);
  const [stockList, setStockList] = useState({});

  return (<Context.Provider
  value={{
    showTrendline,
    setShowTrendline,
    timeFrame,
    setTimeFrame,
    stockToken,
    setStockToken,
    stockList,
    setStockList,
    searchActive,
    setSearchActive,
    }}>
    {props.children}
  </Context.Provider>)
}

