import React, { useContext } from "react";
import { Context } from "../Context/AppContextProvider";
import TimeFrames from "./TimeFrames";

export default function StockBar() {
  const { stockToken, setSearchActive, setTradeBoxActive, stockDict } =
    useContext(Context);

  const handleOnClickName = () => {
    setSearchActive(true);
  };

  const handleOnClickTrade = () => {
    //show trade box
    setTradeBoxActive(true);
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-white bg-white">
      <div className="container-fluid">
        <div className="collapse navbar-collapse" id="navbarSupportedContent">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            <li className="nav-item px-3">
              <p className="p-1" onClick={() => handleOnClickName()}>
                {stockDict[stockToken]}
              </p>
            </li>
            <TimeFrames />
          </ul>
          <div className="float-end p-1 text-white">
            <span
              className="text-white bg-primary rounded p-1"
              onClick={() => handleOnClickTrade()}
            >
              Add Trade
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
}
