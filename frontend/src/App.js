import { useState } from "react";
import { Route, Routes } from "react-router-dom";
import "./assets/css/App.css";
import Footer from "./components/Footer";
import Header from "./components/Header";
import { AuthProvider } from "./context/AuthContext";
import Book from "./pages/Book";
import HomePage from "./pages/HomePage";
import Login from "./pages/Login";
import Register from "./pages/Register";
import PageNotFound from "./utils/PageNotFound";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  return (
    <div className="container">
      <AuthProvider>
        <Header setIsLoggedIn={setIsLoggedIn} />
        <Routes>
          <Route exact path="/" element={<HomePage />} />
          {!isLoggedIn && (
            <Route exact path="register" element={<Register />} />
          )}
          {!isLoggedIn && <Route exact path="login" element={<Login />} />}
          {isLoggedIn && <Route exact path="books" element={<Book />} />}
          <Route exact path="*" element={<PageNotFound />} />
        </Routes>
        <Footer title="Footer" />
      </AuthProvider>
    </div>
  );
}

export default App;
