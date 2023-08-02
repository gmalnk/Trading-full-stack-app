import React, { useContext, useState, useEffect } from "react";
import AxiosAPI from "../API/AxiosAPI";
import { Context } from "../Context/AppContextProvider";

export default function StockList() {
  const { setStockToken, stockList, setStockList, stockToken } =
    useContext(Context);
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

  const fetchAllStocksData = async () => {
    await AxiosAPI.get("/stocklist").then((res) => {
      // console.log(res);
      // console.log(typeof res.data); // Output should be "object" for an array
      // console.log(Array.isArray(res.data)); // Output should be true if stockList is an array
      setStockList(res.data);
    });
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
            }
          >
            <div>
              <div className="float-start">
                <span className=" m-1">{stockList[key]}</span>
              </div>
            </div>
          </div>
        );
      })}
      {/* {stockList &&
        stockList.map((item) => {
          return (
            <div
              id={item.stockToken}
              onClick={() => handleOnClickStock(item.token)}
              className={
                item.token === stockToken
                  ? "row px-3 border border-primary"
                  : "row px-3"
              }
            >
              <div>
                <div className="float-start">
                  <span className=" m-1">{stockList[item.token]}</span>
                </div>
              </div>
            </div>
          );
        })} */}
    </div>
  );
}
