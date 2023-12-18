import AppContextProvider from "./Context/AppContextProvider";
import Navbar from "./Components/Navbar";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useNavigate,
} from "react-router-dom";
import Routing from "./Routing";

function App() {
  return (
    <AppContextProvider>
      <div className="container-fluid">
        <Router>
          <Routing />
        </Router>
      </div>
    </AppContextProvider>
  );
}

export default App;
