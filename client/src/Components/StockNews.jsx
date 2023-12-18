import React from "react";
import ButtonDark from "./ButtonDark";

const StockNews = () => {
  return (
    <div className="stockNewsContainer">
      <div className="stockNewsHeading">Stay Updated with Stock News</div>
      <div className="stockNewsSubHeading">
        Get the Latest Stock Updates and News
      </div>
      <div className="stockNewsForm">
        <input className="stockNewsInput" placeholder="yourmail@gmail.com" />
        <ButtonDark text="Get Stock Updates" />
      </div>
      <div className="stockNewsTANDC">
        By signing up, you confirm that you agree with our Terms and Conditions.
      </div>
    </div>
  );
};

export default StockNews;
