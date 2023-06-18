import AppContextProvider from "./Context/AppContextProvider";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./Routes/Home";
import Trades from "./Routes/Trades";
import PNL from "./Routes/PNL";
import Login from "./Routes/Login";
import About from "./Routes/About";
import Stocks from "./Routes/Stocks";
import Navbar from "./Components/Navbar";
import Exp from "./Components/exp";

function App() {
  return (
    <AppContextProvider>
      <div className="container-fluid">
        <Navbar />
        <Router>
          <Routes>
            <Route exact path="/" Component={Home} />
            <Route exact path="/trades" Component={Trades} />
            <Route exact path="/p&l" Component={PNL} />
            <Route exact path="/login" Component={Login} />
            <Route exact path="/about" Component={About} />
            <Route exact path="/stocks" Component={Stocks} />
            <Route exact path="/exp" Component={Exp} />
          </Routes>
        </Router>
      </div>
    </AppContextProvider>
  );
}

export default App;
