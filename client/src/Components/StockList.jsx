import React, { useContext, useState, useEffect } from "react";
import AxiosAPI from "../API/AxiosAPI";
import { Context } from "../Context/AppContextProvider";

export default function StockList() {
  const {
    setStockToken,
    stockList,
    setStockList,
    stockToken,
    setTradeBoxActive,
  } = useContext(Context);
  const [divHeight, setDivHeight] = useState(window.innerHeight - 100);

  useEffect(() => {
    const handleResize = () => {
      setDivHeight(window.innerHeight - 100);
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  const divStyle = {
    height: `${divHeight}px`,
    overflow: "auto",
  };

  const handleOnClickTrade = () => {
    //show trade box
    setTradeBoxActive(true);
  };
  const fetchAllStocksData = async () => {
    const response = await AxiosAPI.get("/stocklist");
    console.log(response);
    setStockList(response.data);
  };

  const handleOnClickStock = (key) => {
    setStockToken(key);
  };

  useEffect(() => {
    fetchAllStocksData();
  }, []);

  return (
    <div className="col" style={divStyle}>
      {Object.keys(stockList).map((key) => {
        return (
          <div
            id={key}
            onClick={() => handleOnClickStock(key)}
            className={
              key === stockToken ? "row px-3 border border-primary" : "row px-3"
            }>
            <div>
              <div className="float-start">
                <span className=" m-1">{stockList[key]}</span>
              </div>
              <div className="float-end p-1 text-white">
                <span
                  className="text-white bg-primary rounded p-1"
                  onClick={() => handleOnClickTrade()}>
                  Trade
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
