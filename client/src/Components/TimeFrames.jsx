import React from "react";
import { useContext } from "react";
import { Context } from "../Context/AppContextProvider";

export default function TimeFrames() {
  const { setTimeFrame, timeFrame } = useContext(Context);

  const handleOnCLickTimeFrame = (timeFrame) => {
    setTimeFrame(timeFrame);
  };

  return (
    <>
      <li
        className="nav-item px-1"
        onClick={() => handleOnCLickTimeFrame("FIFTEEN_MINUTE")}>
        <p
          className={
            timeFrame === "FIFTEEN_MINUTE" ? "bg-primary rounded p-1" : "p-1"
          }>
          15m
        </p>
      </li>
      <li
        className="nav-item px-1"
        onClick={() => handleOnCLickTimeFrame("THIRTY_MINUTE")}>
        <p
          className={
            timeFrame === "THIRTY_MINUTE" ? "bg-primary rounded p-1" : "p-1"
          }>
          30m
        </p>
      </li>
      <li
        className="nav-item px-1"
        onClick={() => handleOnCLickTimeFrame("ONE_HOUR")}>
        <p
          className={
            timeFrame === "ONE_HOUR" ? "bg-primary rounded p-1" : "p-1"
          }>
          1h
        </p>
      </li>
      <li
        className="nav-item px-1"
        onClick={() => handleOnCLickTimeFrame("TWO_HOUR")}>
        <p
          className={
            timeFrame === "TWO_HOUR" ? "bg-primary rounded p-1" : "p-1"
          }>
          2h
        </p>
      </li>
      <li
        className="nav-item px-1"
        onClick={() => handleOnCLickTimeFrame("FOUR_HOUR")}>
        <p
          className={
            timeFrame === "FOUR_HOUR" ? "bg-primary rounded p-1" : "p-1"
          }>
          4h
        </p>
      </li>
      <li
        className="nav-item px-1"
        onClick={() => handleOnCLickTimeFrame("ONE_DAY")}>
        <p
          className={
            timeFrame === "ONE_DAY" ? "bg-primary rounded p-1" : "p-1"
          }>
          D
        </p>
      </li>
      <li
        className="nav-item px-1"
        onClick={() => handleOnCLickTimeFrame("ONE_WEEK")}>
        <p
          className={
            timeFrame === "ONE_WEEK" ? "bg-primary rounded p-1" : "p-1"
          }>
          W
        </p>
      </li>
      <li
        className="nav-item px-1"
        onClick={() => handleOnCLickTimeFrame("ONE_MONTH")}>
        <p
          className={
            timeFrame === "ONE_MONTH" ? "bg-primary rounded p-1" : "p-1"
          }>
          M
        </p>
      </li>
    </>
  );
}
