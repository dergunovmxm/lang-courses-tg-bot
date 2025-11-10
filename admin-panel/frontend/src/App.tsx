import { Routes, Route } from "react-router-dom";
import MainLayout from "./layouts/Main";
import { publicRoutes } from "../src/routes";
import "./App.css";

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<MainLayout />}>
          {publicRoutes.map((route) => (
            <Route
              key={route.path}
              path={route.path}
              element={<route.component />}
            />
          ))}
        </Route>
      </Routes>
    </div>
  );
}

export default App;
