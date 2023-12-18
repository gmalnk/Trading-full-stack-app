import React from "react";
import { useContext } from "react";
import { Context } from "../Context/AppContextProvider";
import {
  STOCK_LIST_CATEGORY_OPTIONS,
  STOCK_SORT_OPTIONS,
} from "../Constants/constants";

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
                {Object.keys(STOCK_LIST_CATEGORY_OPTIONS).map((key) => {
                  return (
                    <option value={key}>
                      {STOCK_LIST_CATEGORY_OPTIONS[key]}
                    </option>
                  );
                })}
              </select>
            </th>
            <th scope="col">
              <select
                className="form-select"
                onChange={(e) => setStockListSort(e.target.value)}
              >
                {Object.keys(STOCK_SORT_OPTIONS).map((key) => {
                  return <option value={key}>{STOCK_SORT_OPTIONS[key]}</option>;
                })}
              </select>
            </th>
          </tr>
        </thead>
      </table>
    </div>
  );
}
