import React from "react";

const Testimonial = () => {
  return (
    <div className="testimonial-section">
      <div className="testimonialContainer">
        <div className="leftArrow">
          <img
            loading="lazy"
            src="https://cdn.builder.io/api/v1/image/assets/TEMP/503a81e2-0742-4d11-b271-20b51ca50c7f?apiKey=05a03f3237de41d99e4f93550adfb278&"
            className="leftArrowImg"
          />
        </div>
        <div className="testimonialContent">
          <img
            loading="lazy"
            srcset="
          https://cdn.builder.io/api/v1/image/assets/TEMP/0828ef15-6959-48d1-8230-866fbc00028a?apiKey=05a03f3237de41d99e4f93550adfb278&width=100   100w,
          https://cdn.builder.io/api/v1/image/assets/TEMP/0828ef15-6959-48d1-8230-866fbc00028a?apiKey=05a03f3237de41d99e4f93550adfb278&width=200   200w,
          https://cdn.builder.io/api/v1/image/assets/TEMP/0828ef15-6959-48d1-8230-866fbc00028a?apiKey=05a03f3237de41d99e4f93550adfb278&width=400   400w,
          https://cdn.builder.io/api/v1/image/assets/TEMP/0828ef15-6959-48d1-8230-866fbc00028a?apiKey=05a03f3237de41d99e4f93550adfb278&width=800   800w,
          https://cdn.builder.io/api/v1/image/assets/TEMP/0828ef15-6959-48d1-8230-866fbc00028a?apiKey=05a03f3237de41d99e4f93550adfb278&width=1200 1200w,
          https://cdn.builder.io/api/v1/image/assets/TEMP/0828ef15-6959-48d1-8230-866fbc00028a?apiKey=05a03f3237de41d99e4f93550adfb278&width=1600 1600w,
          https://cdn.builder.io/api/v1/image/assets/TEMP/0828ef15-6959-48d1-8230-866fbc00028a?apiKey=05a03f3237de41d99e4f93550adfb278&width=2000 2000w,
          https://cdn.builder.io/api/v1/image/assets/TEMP/0828ef15-6959-48d1-8230-866fbc00028a?apiKey=05a03f3237de41d99e4f93550adfb278&
        "
            className="testimonialImg"
          />
          <div className="testimonialText">
            A staple in my trading toolkit, this platform delivers exceptional
            trendlines and seamlessly executes pre-defined trades. It has
            significantly improved the way I approach and execute trades.
          </div>
          <div className="testimonialName">ChatGPT</div>
          <div className="testimonialDetails">CEO, Company XYZ</div>
        </div>
        <div className="rightArrow">
          <img
            loading="lazy"
            src="https://cdn.builder.io/api/v1/image/assets/TEMP/cb180c55-e53b-4569-b4ce-c76e4ed11d4d?apiKey=05a03f3237de41d99e4f93550adfb278&"
            className="rightArrowImg"
          />
        </div>
      </div>
    </div>
  );
};

export default Testimonial;
