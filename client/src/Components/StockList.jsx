import React, { useContext, useState, useEffect } from "react";
import AxiosAPI from "../API/AxiosAPI";
import { Context } from "../Context/AppContextProvider";
import StockListFilter from "./StockListFilter";

export default function StockList() {
  const {
    setStockToken,
    stockDict,
    setStockDict,
    stockList,
    setStockList,
    stockToken,
    timeFrame,
    stockListCategory,
    stockListSort,
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

  const fetchStockList = async () => {
    await AxiosAPI.get(
      `/stocklist/${timeFrame}/${stockListCategory}/${stockListSort}`
    ).then((res) => {
      console.log(res.data);
      setStockList(res.data.tokensList);
      setStockDict(res.data.stocksDict);
    });
  };

  const handleOnClickStock = (key) => {
    setStockToken(key);
  };

  useEffect(() => {
    fetchStockList();
  }, [timeFrame, stockListCategory, stockListSort]);

  return (
    <div>
      <StockListFilter />

      <div className="col" style={divStyle}>
        {stockList &&
          stockList.map((key) => {
            return (
              <div
                id={key}
                onClick={() => handleOnClickStock(key)}
                className={
                  key === stockToken
                    ? "row px-3 border border-primary"
                    : "row px-3"
                }
              >
                <div>
                  <div className="float-start">
                    <span className=" m-1">{stockDict[key]}</span>
                  </div>
                </div>
              </div>
            );
          })}
      </div>
    </div>
  );
}
