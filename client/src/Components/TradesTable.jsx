import React, { useEffect, useState } from "react";
import AxiosAPI from "../API/AxiosAPI";

export default function TradesTable() {
  const [trades, setTrades] = useState([]);
  const getTrades = async () => {
    const response = await AxiosAPI.get("/trades");
    setTrades(response.data.tradesData);
  };
  const handleDelete = async (id) => {
    console.log(id);
    await AxiosAPI.delete(`/trade/${id}`);
    const updatedTrades = trades.filter((trade) => trade.id !== id);
    setTrades(updatedTrades);
  };
  useEffect(() => {
    getTrades();
  }, []);
  return (
    <div className="py-5">
      <table className="table table-hover">
        <thead className="bg-light">
          <tr id={"table-header-row"}>
            <th scope="col" className="p-3">
              Stock
            </th>
            <th scope="col">
              <select className="form-select">
                <option value="">TimeFrame</option>
                <option value="15m">15m</option>
                <option value="30m">30m</option>
                <option value="1hr">1hr</option>
                <option value="2hr">2hr</option>
                <option value="4hr">4hr</option>
                <option value="1D">1D</option>
                <option value="1W">1W</option>
                <option value="1M">1M</option>
              </select>
            </th>
            <th scope="col">
              <select className="form-select">
                <option value="">Status</option>
                <option value="Done">Done</option>
                <option value="Yet to take">Yet to take</option>
              </select>
            </th>
            <th scope="col">
              <select className="form-select">
                <option value="">Direction</option>
                <option value="Long">Long</option>
                <option value="Short">Short</option>
              </select>
            </th>
            <th scope="col">
              <select className="form-select">
                <option value="up-arrow">Quantity</option>
                <option value="up-arrow">Quantity▲</option>
                <option value="down-arrow">Quantity▼</option>
              </select>
            </th>
            <th scope="col" className="p-3">
              Entry Price
            </th>
            <th scope="col" className="p-3">
              Exit Price
            </th>
            <th scope="col" className="p-3">
              Take Profit
            </th>
            <th scope="col" className="p-3">
              Stop Loss
            </th>
            <th scope="col">
              <select className="form-select">
                <option value="">P&L</option>
                <option value="+ve">+ve</option>
                <option value="-ve">-Ve</option>
              </select>
            </th>
          </tr>
        </thead>
        <tbody>
          {trades &&
            trades.map((trade) => {
              return (
                <tr id={trade.id}>
                  <td className="px-3">{trade.stockName}</td>
                  <td className="px-3">{trade.timeFrame}</td>
                  <td className="px-3">{trade.status}</td>
                  <td className="px-3">{trade.direction}</td>
                  <td className="px-3">{trade.quantity}</td>
                  <td className="px-3">{trade.entryPrice}</td>
                  <td className="px-3">{trade.exitPrice}</td>
                  <td className="px-3">{trade.takeProfit}</td>
                  <td className="px-3">{trade.stopLoss}</td>
                  <td className="px-3">{trade["p&l"]}</td>
                  {trade.status === "TODO" && (
                    <td>
                      <button onClick={() => handleDelete(trade.id)}>
                        <i class="fa-solid fa-trash-can"></i>
                      </button>
                    </td>
                  )}
                </tr>
              );
            })}
        </tbody>
      </table>
    </div>
  );
}
