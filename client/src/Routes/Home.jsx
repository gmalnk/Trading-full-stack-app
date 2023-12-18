import React from "react";
import "../App.css";
import NavbarNew from "../Components/NavbarNew";
import ButtonDark from "../Components/ButtonDark";
import ButtonLight from "../Components/ButtonLight";
import Footer from "../Components/Footer";
import HeroHeader from "../Components/HeroHeader";
import CallToAction from "../Components/CallToAction";
import StockNews from "../Components/StockNews";
import Testimonial from "../Components/Testimonial";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();
  return (
    <div class="main">
      <HeroHeader />
      <div class="div-23">
        <div class="div-24">
          <div class="div-25">
            <div class="column">
              <img loading="lazy" src="./Images/4.jpg" class="img-8" />
            </div>
            <div class="column-2">
              <div class="div-26">
                <div class="div-27">Revolutionize Your Trading Experience</div>
                <div class="div-28">
                  Empower Your Trading Journey with our Real-Time Stock
                  Insights, Customizable Charts, Intelligent Trendlines, Chart
                  Patterns, Candlestick patterns, Systematic Algo Trading and
                  many more exciting features
                  <br />– Your Gateway to Informed Decision-Making.
                </div>
                <div class="div-29">
                  <div onClick={() => navigate("/learnmore")}>
                    <ButtonLight text="Learn More" />
                  </div>
                  <div onClick={() => navigate("/signup")}>
                    <ButtonDark text="Sign Up" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="div-32">
        <div class="div-33">
          <div class="div-34">
            <div class="column">
              <div class="div-35">
                <div class="div-37">Systematic Trading Redefined</div>
                <div class="div-38">
                  Superior Trendlines using Operations Research Excellence.
                  Embrace Systematic Breakout Trading Strategies with a
                  Pre-Defined Trade Executor. Revolutionizing Trader Psychology
                  and Empowering Traders with Confidence and Control.
                </div>
                <div class="div-39">
                  <div class="div-40">
                    <div class="column">
                      <div class="div-41">
                        <div class="div-42">Algo Trendlines</div>
                        <div class="div-43">
                          Better your trading journey with our system generated
                          Super-Trendlines.
                        </div>
                      </div>
                    </div>
                    <div class="column-3">
                      <div class="div-44">
                        <div class="div-45">Predefined Trades</div>
                        <div class="div-46">
                          Elevating trading psychology, our unique one-of-a-kind
                          predefined trade executor sets a new industry
                          standard.
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="div-47">
                  <div onClick={() => navigate("/learnmore")}>
                    <ButtonLight text="Learn More" />
                  </div>
                  <div onClick={() => navigate("/signup")}>
                    <ButtonDark text="Sign Up" />
                  </div>
                </div>
              </div>
            </div>
            <div class="column-4">
              <img loading="lazy" src="./Images/5.jpg" class="img-9" />
            </div>
          </div>
        </div>
      </div>
      <CallToAction />
      <Testimonial />
      <StockNews />
      <Footer />
    </div>
  );
}
