import React, { useContext, useState, useEffect } from "react";
import AxiosAPI from "../API/AxiosAPI";
import { Context } from "../Context/AppContextProvider";
import StockListFilter from "./StockListFilter";
import { stocksDict } from "./Constants/constants";

export default function StockList() {
  const {
    setStockToken,
    stockToken,
    timeFrame,
    stockListCategory,
    stockListSort,
  } = useContext(Context);
  const [divHeight, setDivHeight] = useState(window.innerHeight - 200);

  const [stockList, setStockList] = useState([]);
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

  const handleStockClick = (event) => {
    if (event.target.hasAttribute("data-stocktoken")) {
      setStockToken(event.target.getAttribute("data-stocktoken"));
      return;
    }
    setStockToken(
      event.target
        .querySelector("span[data-stocktoken]")
        .getAttribute("data-stocktoken")
    );
  };

  const fetchStockList = async () => {
    console.log(timeFrame, stockListCategory, stockListSort);
    await AxiosAPI.get(
      `/stocklist/${timeFrame}/${stockListCategory}/${stockListSort}`
    ).then((res) => {
      console.log(res.data);
      setStockList(res.data.tokensList);
    });
  };

  useEffect(() => {
    fetchStockList();
  }, [timeFrame, stockListCategory, stockListSort]);

  return (
    <div>
      <StockListFilter />

      <div
        className="col"
        style={divStyle}
        onClick={(event) => {
          handleStockClick(event);
        }}
      >
        {stockList &&
          stockList.map((key) => {
            return (
              <div
                id={key}
                className={
                  key === stockToken
                    ? "row px-3 border border-primary"
                    : "row px-3"
                }
              >
                <div>
                  <div className="float-start">
                    <span className=" m-1" data-stocktoken={key}>
                      {stocksDict[key]}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
      </div>
    </div>
  );
}
