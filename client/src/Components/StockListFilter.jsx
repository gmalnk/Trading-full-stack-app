import React from "react";
import { useContext } from "react";
import { Context } from "../Context/AppContextProvider";

export default function StockListFilter() {
  const { setStockListCategory, setStockListSort } = useContext(Context);
  return (
    <div>
      <table className="table table-hover">
        <thead className="bg-light">
          <tr id={"table-header-row"}>
            <th scope="col">
              <select
                className="form-select"
                onChange={(e) => setStockListCategory(e.target.value)}
              >
                <option value="all">All</option>
                <option value="n50">NIFTY-50</option>
                <option value="n100">NIFTY-100</option>
                <option value="n200">NIFTY-200</option>
                <option value="n500">NIFTY-500</option>
                <option value="n1000">NIFTY-1000</option>
              </select>
            </th>
            <th scope="col">
              <select
                className="form-select"
                onChange={(e) => setStockListSort(e.target.value)}
              >
                <option value="alphabets">Alphabetically</option>
                <option value="cap">Market Cap</option>
                <option value="H">down-trendline</option>
                <option value="L">up-trendline</option>
              </select>
            </th>
          </tr>
        </thead>
      </table>
    </div>
  );
}
