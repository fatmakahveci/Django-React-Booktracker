import {
  faCheck,
  faInfoCircle,
  faTimes,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useContext, useEffect, useState } from "react";
import AuthContext from "../context/AuthContext";
import { NavLink } from "react-router-dom";

const EMAIL_REGEX = /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(.\w{2,3})+$/;
const PWD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%.]).{8,24}$/;

const Login = () => {
  const { loginUser } = useContext(AuthContext);

  const [email, setEmail] = useState("");
  const [validEmail, setValidEmail] = useState(false);
  const [emailFocus, setEmailFocus] = useState(false);
  const emailInstruction = `E-mail is invalid.`;

  useEffect(() => {
    setValidEmail(EMAIL_REGEX.test(email));
  }, [email]);

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
  };

  const [pwd, setPwd] = useState("");
  const [validPwd, setValidPwd] = useState(false);
  const [pwdFocus, setPwdFocus] = useState(false);
  const pwdInstruction = `
    8 to 24 characters.
    It must include uppercase and lowercase letters,
    a number and a special character (!@#$%).`;

  useEffect(() => {
    setValidPwd(PWD_REGEX.test(pwd));
  }, [pwd]);

  const handlePwdChange = (e) => {
    setPwd(e.target.value);
  };

  return (
    <div className="my-form">
      <h1>Login</h1>
      <form onSubmit={loginUser}>
        <div className="form-group row">
          <label
            className="col-md-4 col-form-label text-md-right"
            htmlFor="email"
          >
            E-mail address
            <FontAwesomeIcon
              icon={faCheck}
              className={emailFocus && validEmail ? "valid" : "hide"}
            />
            <FontAwesomeIcon
              icon={faTimes}
              className={emailFocus && !validEmail ? "invalid" : "hide"}
            />
          </label>
          <div className="col-md-6">
            <input
              type="text"
              className="form-control"
              id="email"
              onChange={handleEmailChange}
              value={email}
              name="email"
              autoComplete="off"
              required
              aria-invalid={validEmail ? "false" : "true"}
              aria-describedby="uidnote"
              onFocus={() => setEmailFocus(true)}
              onBlur={() => setEmailFocus(false)}
              placeholder="E-mail address"
            />
            <p
              id="uidnote"
              className={
                emailFocus && !validEmail ? "instructions" : "offscreen"
              }
            >
              <FontAwesomeIcon icon={faInfoCircle} /> {emailInstruction}
            </p>
          </div>
        </div>
        <p></p>
        <div className="form-group row">
          <label
            htmlFor="pwd"
            className="col-md-4 col-form-label text-md-right"
          >
            Password
            <FontAwesomeIcon
              icon={faCheck}
              className={pwdFocus && validPwd ? "valid" : "hide"}
            />
            <FontAwesomeIcon
              icon={faTimes}
              className={pwdFocus && !validPwd ? "invalid" : "hide"}
            />
          </label>
          <div className="col-md-6">
            <input
              type="password"
              className="form-control"
              id="pwd"
              value={pwd}
              name="password"
              autoComplete="off"
              required
              aria-invalid={validPwd ? "false" : "true"}
              aria-describedby="upassnote"
              onChange={handlePwdChange}
              onFocus={() => setPwdFocus(true)}
              onBlur={() => setPwdFocus(false)}
              placeholder="Password"
            />
            <p
              id="pwdnote"
              className={pwdFocus && !validPwd ? "instructions" : "offscreen"}
            >
              <FontAwesomeIcon icon={faInfoCircle} /> {pwdInstruction}
            </p>
          </div>
        </div>
        <p></p>
        <div className="col-md-8 offset-md-6">
          <span className="register-screen__subtext">
            Don't you have an account?{" "}
            <NavLink to="/register/">Register</NavLink>
            &nbsp;&nbsp;&nbsp;
          </span>
          <button type="submit" className="btn btn-primary">
            Submit
          </button>
        </div>
      </form>
    </div>
  );
};

export default Login;
