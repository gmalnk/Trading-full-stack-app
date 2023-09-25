import React, { useRef, useState } from "react";
import TradeForm from "./TradeForm";

const TradeBox = () => {
  const [position, setPosition] = useState({ x: 200, y: 100 });
  const childRef = useRef(null);

  // Handle mouse down event to start dragging
  const handleMouseDown = (event) => {
    // Save the initial position of the mouse
    const initialX = event.clientX;
    const initialY = event.clientY;

    // Calculate the initial position of the component
    const initialPosition = { x: position.x, y: position.y };

    // Handle mouse move event to update component position
    const handleMouseMove = (event) => {
      // Calculate the distance moved by the mouse
      const deltaX = event.clientX - initialX;
      const deltaY = event.clientY - initialY;

      // Update the component's position
      setPosition({
        x: initialPosition.x + deltaX,
        y: initialPosition.y + deltaY,
      });
    };

    // Attach mouse move event listener
    document.addEventListener("mousemove", handleMouseMove);

    // Handle mouse up event to stop dragging
    const handleMouseUp = () => {
      // Remove mouse move event listener
      document.removeEventListener("mousemove", handleMouseMove);
    };

    // Attach mouse up event listener
    document.addEventListener("mouseup", handleMouseUp);
  };
  const handleOnClickDeleteTradeBox = () => {
    childRef.current.removeTradeBox(true);
  };
  return (
    <div
      className="trade-box-active border border-primary rounded bg-white"
      style={{
        position: "absolute",
        left: position.x,
        top: position.y,
        cursor: "move",
      }}
    >
      <div className="container p-3 rounded">
        <div>
          <span>
            <h2 onMouseDown={handleMouseDown}>Trade Parameters</h2>
          </span>
          <span>
            <i
              class="fa-solid fa-xmark"
              onClick={() => handleOnClickDeleteTradeBox()}
            ></i>
          </span>
        </div>
        <TradeForm ref={childRef} />
      </div>
    </div>
  );
};

export default TradeBox;
