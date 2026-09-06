import { publicApi as axios, readTokens, clearTokens } from "../api";
import { jwtDecode } from "jwt-decode";
import { createContext, useState } from "react";

const AuthContext = createContext();

axios.defaults.headers.post["Content-Type"] = "application/json";
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

export const AuthProvider = ({ children }) => {
  const [authTokens, setAuthTokens] = useState(readTokens);

  const [user, setUser] = useState(() => {
    try { return authTokens ? jwtDecode(authTokens.access) : null; }
    catch { clearTokens(); return null; }
  });

  const navigate = (path) => window.location.assign(path);

  const [message, setMessage] = useState("");
  const [showMessage, setShowMessage] = useState(false);

  const registerUser = async (e) => {
    e.preventDefault();

    await axios
      .post("/register/", {
        user_name: e.target.user_name.value,
        email: e.target.email.value,
        password: e.target.password.value,
      })
      .then((response) => {
        if (response.status >= 200 && response.status < 300) {
          setMessage("The user is successfully registered.");
          setShowMessage(false);
          navigate("/login/");
        }
      })
      .catch((err) => {
        if (err?.response?.status === 400) {
          setMessage(Object.values(err.response.data)[0][0]);
          setShowMessage(true);
        }
      });
  };

  const loginUser = async (e) => {
    e.preventDefault();

    await axios
      .post("token/", {
        email: e.target.email.value,
        password: e.target.password.value,
      })
      .then((response) => {
        setAuthTokens(response.data);
        setUser(jwtDecode(response.data.access));
        localStorage.setItem("authTokens", JSON.stringify(response.data));
        navigate("/books/");
      })
      .catch((err) => {
        console.log(err);
      });
  };

  const logoutUser = (event) => {
    event?.preventDefault();
    setAuthTokens(null);
    setUser(null);
    clearTokens();
    navigate("/");
  };

  const contextData = {
    user: user,
    authTokens: authTokens,
    loginUser: loginUser,
    registerUser: registerUser,
    logoutUser: logoutUser,
    message: message,
    showMessage: showMessage,
  };

  return (
    <AuthContext.Provider value={contextData}>{children}</AuthContext.Provider>
  );
};

export default AuthContext;
