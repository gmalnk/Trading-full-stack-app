import React from "react";
import { useNavigate } from "react-router-dom";

const TextLogo = () => {
  const navigate = useNavigate();
  const handleOnCLickTextLogo = () => {
    navigate("/");
  };
  return (
    <div className="textLogo-container">
      <img
        loading="lazy"
        srcset="
  https://cdn.builder.io/api/v1/image/assets/TEMP/5b06395a-1316-42d0-b551-460de5540f91?apiKey=05a03f3237de41d99e4f93550adfb278&width=100   100w,
  https://cdn.builder.io/api/v1/image/assets/TEMP/5b06395a-1316-42d0-b551-460de5540f91?apiKey=05a03f3237de41d99e4f93550adfb278&width=200   200w,
  https://cdn.builder.io/api/v1/image/assets/TEMP/5b06395a-1316-42d0-b551-460de5540f91?apiKey=05a03f3237de41d99e4f93550adfb278&width=400   400w,
  https://cdn.builder.io/api/v1/image/assets/TEMP/5b06395a-1316-42d0-b551-460de5540f91?apiKey=05a03f3237de41d99e4f93550adfb278&width=800   800w,
  https://cdn.builder.io/api/v1/image/assets/TEMP/5b06395a-1316-42d0-b551-460de5540f91?apiKey=05a03f3237de41d99e4f93550adfb278&width=1200 1200w,
  https://cdn.builder.io/api/v1/image/assets/TEMP/5b06395a-1316-42d0-b551-460de5540f91?apiKey=05a03f3237de41d99e4f93550adfb278&width=1600 1600w,
  https://cdn.builder.io/api/v1/image/assets/TEMP/5b06395a-1316-42d0-b551-460de5540f91?apiKey=05a03f3237de41d99e4f93550adfb278&width=2000 2000w,
  https://cdn.builder.io/api/v1/image/assets/TEMP/5b06395a-1316-42d0-b551-460de5540f91?apiKey=05a03f3237de41d99e4f93550adfb278&
"
        className="textLogoImg"
        onClick={handleOnCLickTextLogo}
      />
      <div className="logoText">Algo Traders</div>
    </div>
  );
};

export default TextLogo;
