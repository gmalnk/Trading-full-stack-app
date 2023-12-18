import { Routes, Route, useNavigate } from "react-router-dom";
import Home from "./Routes/Home";
import Trades from "./Routes/Trades";
import PNL from "./Routes/PNL";
import Login from "./Routes/Login";
import About from "./Routes/About";
import Stocks from "./Routes/Stocks";
import SignUp from "./Routes/SignUp";
import SignIn from "./Components/exp";
import { useContext, useEffect } from "react";
import { Context } from "./Context/AppContextProvider";
import Pricing from "./Routes/Pricing";
import NavbarNew from "./Components/NavbarNew";

const Routing = () => {
  const { logedIn } = useContext(Context);
  return (
    <>
      <NavbarNew />
      <Routes>
        <Route exact path="/" Component={Home} />
        <Route
          exact
          path="/trades"
          Component={logedIn ? Trades : PromtToLogin}
        />
        <Route exact path="/p&l" Component={logedIn ? PNL : PromtToLogin} />
        <Route exact path="/login" Component={Login} />
        <Route exact path="/signup" Component={SignUp} />
        <Route exact path="/about" Component={About} />
        <Route
          exact
          path="/stocks"
          Component={logedIn ? Stocks : PromtToLogin}
        />
        <Route exact path="/pricing" Component={Pricing} />
        <Route exact path="/exp" Component={SignIn} />
      </Routes>
    </>
  );
};

const PromtToLogin = () => {
  const navigate = useNavigate();
  useEffect(() => {
    navigate("/login");
  }, []);
  return <></>;
};

export default Routing;
