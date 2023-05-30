import { createChart } from "lightweight-charts";
import React, { useEffect, useRef, useState } from "react";
import { useContext } from "react";
import {Context} from "../Context/AppContextProvider";
import AxiosAPI from "../API/AxiosAPI";

export default function ChartComponent() {
  
  const candleoptions = {
    upColor: "#26a69a",
    downColor: "#ef5350",
    borderVisible: false,
    wickUpColor: "#26a69a",
    wickDownColor: "#ef5350",
  }
  const {showTrendline, timeFrame, stockToken} = useContext(Context);
  const [stockData, setStockData] = useState({"candleData":[], "trendlineData":[]})

  const fetchStockData = async () => {
    console.log(stockData+timeFrame)
    const response1 = await AxiosAPI.get(`/trendlines/${stockToken}/${timeFrame}`);
    const response = await AxiosAPI.get(`/${stockToken}/${timeFrame}`);
    setStockData({"candleData" : response.data.stockdata, "trendlineData": response1.data.trendlinedata})
  }

  useEffect( ()=>{
    fetchStockData()
  },[stockToken, timeFrame])

  const chartContainerRef = useRef();
  
  useEffect(() => {
    // console.log("iam in second useEffect")
    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current.clientWidth,
         height: window.innerHeight-100});
    };

    const chartoptions = {
      width: chartContainerRef.current.clientWidth,
      height: window.innerHeight-100,
      layout: {
        textColor: "black",
        background: { type: "black", color: "white" },
      },
      grid: {
        vertLines: {
          color: 'rgba(197, 203, 206, 0)',
        },
        horzLines: {
          color: 'rgba(197, 203, 206, 0)',
        },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: true,
      },
    }

    const chart = createChart(chartContainerRef.current, chartoptions);
    
    chart.timeScale().applyOptions({
      barSpacing: 9,
  });;

    if (showTrendline && stockData.trendlineData) {
      stockData.trendlineData.forEach((line) => {
        chart
          .addLineSeries({
            color: "rgba(45, 85, 255, 1)",
            lineWidth: 0.7,
          })
          .setData(line);
      });
    }
    const candleSeries = chart.addCandlestickSeries(candleoptions);
    // console.log(stockData)
    candleSeries.setData(stockData.candleData);

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);

      chart.remove();
    };
  }, [stockData]);

  return <div id="chart-container" ref={chartContainerRef} />;
}
