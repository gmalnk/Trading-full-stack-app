import { createChart } from "lightweight-charts";
import React, { useEffect, useRef, useState } from "react";
import { useContext } from "react";
import { Context } from "../Context/AppContextProvider";
import AxiosAPI from "../API/AxiosAPI";
import {
  candleoptions,
  chartoptions,
  lineoptions,
  timeScaleOptions,
} from "../Constants/constants";

function useStockData(timeFrame, stockToken, setStockData, setLinesData) {
  const fetchStockData = async () => {
    // console.log(stockToken + timeFrame);
    const response = await AxiosAPI.get(`/${stockToken}/${timeFrame}`);
    console.log(response);
    response.data &&
      response.data.stockData &&
      response.data.trendlineData &&
      setStockData({
        candleData: response.data.stockData,
        trendlineData: response.data.trendlineData,
      });
    response.data.linesData && setLinesData(response.data.linesData);
  };

  useEffect(() => {
    fetchStockData();
  }, [stockToken, timeFrame]);
}

export default function ChartComponent() {
  const { showTrendline, timeFrame, stockToken, setLinesData } =
    useContext(Context);
  const [stockData, setStockData] = useState({
    candleData: [],
    trendlineData: [],
  });
  useStockData(timeFrame, stockToken, setStockData, setLinesData);

  const chartContainerRef = useRef();

  useEffect(() => {
    const handleResize = () => {
      chart.applyOptions({
        width: chartContainerRef.current.clientWidth,
        height: window.innerHeight - 100,
      });
    };

    const chart = createChart(chartContainerRef.current, {
      ...chartoptions,
      width: chartContainerRef.current.clientWidth,
      height: window.innerHeight - 100,
    });

    chart.timeScale().applyOptions(timeScaleOptions);

    if (showTrendline && stockData.trendlineData) {
      stockData.trendlineData.forEach((line) => {
        chart.addLineSeries(lineoptions).setData(line);
      });
    }
    const candleSeries = chart.addCandlestickSeries(candleoptions);
    // console.log(stockData)
    candleSeries.setData(stockData.candleData && stockData.candleData);

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);

      chart.remove();
    };
  }, [stockData]);

  return <div id="chart-container" ref={chartContainerRef} />;
}
