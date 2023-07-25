import { useContext, useEffect } from "react";
import "../assets/css/App.css";
import AuthContext from "../context/AuthContext";

const Header = ({ setIsLoggedIn }) => {
  let { user, logoutUser } = useContext(AuthContext);

  useEffect(() => {
    if (user) {
      setIsLoggedIn(true);
    } else {
      setIsLoggedIn(false);
    }
  }, [user]);

  if (user) {
    return (
      <nav className="navbar navbar-expand-lg navbar-light navbar-laravel">
        <div className="container">
          <div className="collapse navbar-collapse" id="navbarSupportedContent">
            <ul className="navbar-nav ml-auto">
              <li className="nav-item">
                <a className="nav-link" onClick={logoutUser} href="/">
                  Logout
                </a>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    );
  } else {
    return (
      <nav className="navbar navbar-expand-lg navbar-light navbar-laravel">
        <div className="container">
          <div className="collapse navbar-collapse" id="navbarSupportedContent">
            <ul className="navbar-nav ml-auto">
              <li className="nav-item">
                <a className="nav-link" href="/login">
                  Login
                </a>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    );
  }
};

export default Header;
