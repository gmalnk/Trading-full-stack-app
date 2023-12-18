import React from "react";
import ButtonDark from "./ButtonDark";
import ButtonLight from "./ButtonLight";
import { useNavigate } from "react-router-dom";

const HeroHeader = () => {
  const navigate = useNavigate();
  return (
    <div className="heroHeaderContainer">
      <div className="heroHeaderHeading">
        Welcome to our Exciting World of Trading
      </div>
      <div className="heroHeaderSubHeading">
        Discover endless possibilities and maximize your investment potential.
      </div>
      <div className="heroHeaderButtons">
        <div onClick={() => navigate("/signup")}>
          <ButtonDark text="Get Started" />
        </div>
        <div onClick={() => navigate("/learnmore")}>
          <ButtonLight text="Learn More" />
        </div>
      </div>
      <div className="heroHeaderImgContainer">
        <img
          loading="lazy"
          srcset="
        https://cdn.builder.io/api/v1/image/assets/TEMP/fd41a869-b46f-4e2a-a737-dbcab0a877c7?apiKey=05a03f3237de41d99e4f93550adfb278&width=100   100w,
        https://cdn.builder.io/api/v1/image/assets/TEMP/fd41a869-b46f-4e2a-a737-dbcab0a877c7?apiKey=05a03f3237de41d99e4f93550adfb278&width=200   200w,
        https://cdn.builder.io/api/v1/image/assets/TEMP/fd41a869-b46f-4e2a-a737-dbcab0a877c7?apiKey=05a03f3237de41d99e4f93550adfb278&width=400   400w,
        https://cdn.builder.io/api/v1/image/assets/TEMP/fd41a869-b46f-4e2a-a737-dbcab0a877c7?apiKey=05a03f3237de41d99e4f93550adfb278&width=800   800w,
        https://cdn.builder.io/api/v1/image/assets/TEMP/fd41a869-b46f-4e2a-a737-dbcab0a877c7?apiKey=05a03f3237de41d99e4f93550adfb278&width=1200 1200w,
        https://cdn.builder.io/api/v1/image/assets/TEMP/fd41a869-b46f-4e2a-a737-dbcab0a877c7?apiKey=05a03f3237de41d99e4f93550adfb278&width=1600 1600w,
        https://cdn.builder.io/api/v1/image/assets/TEMP/fd41a869-b46f-4e2a-a737-dbcab0a877c7?apiKey=05a03f3237de41d99e4f93550adfb278&width=2000 2000w,
        https://cdn.builder.io/api/v1/image/assets/TEMP/fd41a869-b46f-4e2a-a737-dbcab0a877c7?apiKey=05a03f3237de41d99e4f93550adfb278&
      "
          className="heroHeaderImgStart"
        />
        <img
          loading="lazy"
          src="./Images/11.jpg"
          alt="Hero Header Image"
          className="heroHeaderImg"
        />
        <img
          loading="lazy"
          src="./Images/12.jpg"
          className="heroHeaderImg"
          alt="Hero Header Image"
        />
        <img
          loading="lazy"
          src="./Images/13.jpg"
          className="heroHeaderImg"
          alt="Hero Header Image"
        />
        <img
          loading="lazy"
          srcset="
        https://cdn.builder.io/api/v1/image/assets/TEMP/4b91b573-a9d5-4307-b677-d14c5820cb52?apiKey=05a03f3237de41d99e4f93550adfb278&width=100   100w,
        https://cdn.builder.io/api/v1/image/assets/TEMP/4b91b573-a9d5-4307-b677-d14c5820cb52?apiKey=05a03f3237de41d99e4f93550adfb278&width=200   200w,
        https://cdn.builder.io/api/v1/image/assets/TEMP/4b91b573-a9d5-4307-b677-d14c5820cb52?apiKey=05a03f3237de41d99e4f93550adfb278&width=400   400w,
        https://cdn.builder.io/api/v1/image/assets/TEMP/4b91b573-a9d5-4307-b677-d14c5820cb52?apiKey=05a03f3237de41d99e4f93550adfb278&width=800   800w,
        https://cdn.builder.io/api/v1/image/assets/TEMP/4b91b573-a9d5-4307-b677-d14c5820cb52?apiKey=05a03f3237de41d99e4f93550adfb278&width=1200 1200w,
        https://cdn.builder.io/api/v1/image/assets/TEMP/4b91b573-a9d5-4307-b677-d14c5820cb52?apiKey=05a03f3237de41d99e4f93550adfb278&width=1600 1600w,
        https://cdn.builder.io/api/v1/image/assets/TEMP/4b91b573-a9d5-4307-b677-d14c5820cb52?apiKey=05a03f3237de41d99e4f93550adfb278&width=2000 2000w,
        https://cdn.builder.io/api/v1/image/assets/TEMP/4b91b573-a9d5-4307-b677-d14c5820cb52?apiKey=05a03f3237de41d99e4f93550adfb278&
      "
          className="heroHeaderImgEnd"
        />
      </div>
    </div>
  );
};

export default HeroHeader;
