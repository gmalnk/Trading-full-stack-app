import React from "react";
import ButtonDark from "./ButtonDark";
import ButtonLight from "./ButtonLight";
import { useNavigate } from "react-router-dom";

const CallToAction = () => {
  const navigate = useNavigate();
  return (
    <div className="CTA-Section">
      <div className="CTA-container">
        <div className="CTA-flexBox">
          <div className="CTA-column">
            <div className="CTA-columnContainer">
              <div className="CTA-heading">Unlock the Future of Trading</div>
              <div className="CTA-subHeading">
                Sign up or sign in to unlock your Systematic Algo-trading
                Journey.
              </div>
              <div className="CTA-buttons">
                <div onClick={() => navigate("/signup")}>
                  <ButtonDark text="Sign up" />
                </div>
                <div onClick={() => navigate("/login")}>
                  <ButtonLight text="Sign in" />
                </div>
              </div>
            </div>
          </div>
          <div className="CTA-imgColumn">
            <img loading="lazy" src="./Images/7.jpg" className="CTA-img" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default CallToAction;
