import { publicApi as axios, readTokens, clearTokens, logoutSession } from "../api";
import { jwtDecode } from "jwt-decode";
import { createContext, useRef, useState } from "react";

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
  const logoutPending = useRef(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  function showAuthError(error, fallback) {
    const retryAfter = Number(error.response?.headers?.["retry-after"]);
    const detail = error.response?.data?.detail;
    setMessage(error.response?.status === 429
      ? `Too many attempts. ${retryAfter > 0 ? `Try again in ${retryAfter} seconds.` : "Please wait before trying again."}`
      : typeof detail === "string" ? detail : fallback);
    setShowMessage(true);
  }

  const registerUser = async (e) => {
    e.preventDefault();
    setShowMessage(false);

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
          const firstError = Object.values(err.response.data)[0];
          setMessage(Array.isArray(firstError) ? firstError[0] : String(firstError));
          setShowMessage(true);
        } else {
          showAuthError(err, "Could not register. Please try again.");
        }
      });
  };

  const loginUser = async (e) => {
    e.preventDefault();
    setShowMessage(false);

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
        showAuthError(err, "Could not sign in. Check your credentials and try again.");
      });
  };

  const logoutUser = async (event) => {
    event?.preventDefault();
    if (logoutPending.current) return;
    logoutPending.current = true;
    setIsLoggingOut(true);
    let confirmed = true;
    try {
      await logoutSession();
    } catch {
      confirmed = false;
    } finally {
      setAuthTokens(null);
      setUser(null);
      navigate(confirmed ? "/" : "/login/?logout=unconfirmed");
    }
  };

  const contextData = {
    user: user,
    authTokens: authTokens,
    isLoggingOut,
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
