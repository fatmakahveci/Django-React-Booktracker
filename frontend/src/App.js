import { useState } from "react";
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
  const path = window.location.pathname.replace(/\/$/, "") || "/";

  let page = <PageNotFound />;
  if (path === "/") page = <HomePage />;
  if (!isLoggedIn && path === "/register") page = <Register />;
  if (!isLoggedIn && path === "/login") page = <Login />;
  if (isLoggedIn && path === "/books") page = <Book />;

  return (
    <div className="container">
      <AuthProvider>
        <Header setIsLoggedIn={setIsLoggedIn} />
        {page}
        <Footer title="Footer" />
      </AuthProvider>
    </div>
  );
}

export default App;
