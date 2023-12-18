import React from "react";
import { TimeFrame } from "./TimeFrame";
import { TIME_FRAMES } from "../Constants/constants";
export default function TimeFrames() {
  return (
    <>
      {Object.keys(TIME_FRAMES).map((key) => {
        return (
          <TimeFrame timeFrame={key} displayTimeFrame={TIME_FRAMES[key]} />
        );
      })}
    </>
  );
}
