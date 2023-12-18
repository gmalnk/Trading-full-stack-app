import React, { useContext } from "react";
import TextLogo from "./TextLogo";
import ButtonLight from "./ButtonLight";
import ButtonDark from "./ButtonDark";
import { useNavigate } from "react-router-dom";
import { Context } from "../Context/AppContextProvider";

const NavbarNew = () => {
  const navigate = useNavigate();
  const { logedIn, setLogedIn } = useContext(Context);
  const handleOnClickLogOut = () => {
    setLogedIn(false);
    localStorage.removeItem("token");
    navigate("/");
  };
  return (
    <div className="navbar-container">
      <div className="navbar-autolayout">
        <TextLogo />
        <div className="navbar-linksSection">
          <div className="navbar-linksContainer">
            <div className="navbarLinks" onClick={() => navigate("/about")}>
              About Us
            </div>
            <div className="navbarLinks" onClick={() => navigate("/pricing")}>
              Pricing
            </div>
            <div className="navbarLinks" onClick={() => navigate("/stocks")}>
              Stocks
            </div>
            <div className="navbarMoreSection">
              <div className="navbarMore" onClick={() => navigate("/trades")}>
                Products
              </div>
              <img
                loading="lazy"
                src="https://cdn.builder.io/api/v1/image/assets/TEMP/b760eb9b-1de3-432f-af9b-ae878e610ca9?apiKey=05a03f3237de41d99e4f93550adfb278&"
                className="navbarMoreImg"
              />
            </div>
          </div>
          <div className="navbarButtons">
            {!logedIn ? (
              <>
                <div onClick={() => navigate("/signup")}>
                  <ButtonLight text="Sign Up" />
                </div>
                <div onClick={() => navigate("/login")}>
                  <ButtonDark text="Log In" />
                </div>
              </>
            ) : (
              <div onClick={handleOnClickLogOut}>
                <ButtonDark text="Log Out" />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NavbarNew;
