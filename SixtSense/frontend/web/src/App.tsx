import "./App.css";
import HomePage from "./app/home/page";
import LoginPage from "./app/LoginPage";
import RemoteControlPage from "./app/RemoteControlPage"
import { Routes, Route } from "react-router-dom";

function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/home" element={<HomePage />} />
      <Route path="/remote" element={<RemoteControlPage />} />
    </Routes>
  );
}

export default App;
