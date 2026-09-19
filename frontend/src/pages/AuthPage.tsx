import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthProvider";
const titles: Record<string, string> = {
  login: "Welcome back.",
  register: "Start your next chapter.",
  "forgot-password": "A fresh start.",
  "reset-password": "Choose a new password.",
  "verify-email": "Make it official.",
  "resend-verification": "Check your inbox.",
};
export function AuthPage({ mode }: { mode: string }) {
  return <AuthForm key={mode} mode={mode} />;
}
function AuthForm({ mode }: { mode: string }) {
  const { user, signIn } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  if (user && ["login", "register"].includes(mode))
    return <Navigate to="/library" replace />;
  const hasEmail = [
    "login",
    "register",
    "forgot-password",
    "resend-verification",
  ].includes(mode);
  const hasPassword = ["login", "register", "reset-password"].includes(mode);
  const label =
    mode === "login"
      ? "Sign in"
      : mode === "register"
        ? "Create account"
        : mode === "verify-email"
          ? "Verify email"
          : mode === "reset-password"
            ? "Save new password"
            : "Send email";
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setError("");
    setBusy(true);
    try {
      if (mode === "login") {
        await signIn(String(data.get("email")), String(data.get("password")));
        navigate("/library");
        return;
      }
      const paths: Record<string, string> = {
        register: "register",
        "forgot-password": "password/reset",
        "reset-password": "password/reset/confirm",
        "verify-email": "email/verify",
        "resend-verification": "email/resend",
      };
      const body = Object.fromEntries(data);
      if (["reset-password", "verify-email"].includes(mode)) {
        body.uid = params.get("uid") || "";
        body.token = params.get("token") || "";
      }
      const result = await api<{ detail: string }>(
        `auth/${paths[mode]}/`,
        "POST",
        body,
        false,
      );
      setMessage(result.detail);
      if (["reset-password", "verify-email"].includes(mode))
        window.history.replaceState(null, "", window.location.pathname);
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="auth-layout">
      <aside>
        <p className="eyebrow">A SHELF OF YOUR OWN</p>
        <h1>{titles[mode]}</h1>
        <p className="lede">
          One book at a time.
          <br />
          Keep the stories that stay with you.
        </p>
        <p className="auth-note">
          Your library is private. Only you can see your books and notes.
        </p>
      </aside>
      <div className="panel auth-panel">
        <h2>{label}</h2>
        {message ? (
          <div role="status">
            <p className="success">{message}</p>
            <Link className="button" to="/login">
              Continue to sign in
            </Link>
          </div>
        ) : (
          <form onSubmit={(e) => void submit(e)}>
            {error && (
              <p role="alert" className="error">
                {error}
              </p>
            )}
            {mode === "register" && (
              <label>
                Username
                <input
                  name="user_name"
                  autoComplete="username"
                  minLength={4}
                  maxLength={24}
                  required
                />
              </label>
            )}
            {hasEmail && (
              <label>
                Email address
                <input
                  name="email"
                  type="email"
                  autoComplete="email"
                  maxLength={150}
                  required
                />
              </label>
            )}
            {hasPassword && (
              <label>
                {mode === "reset-password" ? "New password" : "Password"}
                <input
                  name="password"
                  type="password"
                  autoComplete={
                    mode === "login" ? "current-password" : "new-password"
                  }
                  minLength={mode === "login" ? undefined : 8}
                  maxLength={128}
                  aria-describedby={
                    mode !== "login" ? "password-help" : undefined
                  }
                  required
                />
              </label>
            )}
            {hasPassword && mode !== "login" && (
              <p className="field-hint" id="password-help">
                At least 8 characters. Avoid common passwords and personal
                details.
              </p>
            )}
            {mode === "verify-email" && (
              <p>Confirm this email address to open your library.</p>
            )}
            <button disabled={busy} type="submit">
              {busy ? "Please wait…" : label}
            </button>
          </form>
        )}
        <div className="auth-links">
          {mode === "login" && (
            <>
              <Link to="/forgot-password">Forgot your password?</Link>
              <Link to="/resend-verification">Resend verification email</Link>
              <p>
                New here? <Link to="/register">Create an account</Link>
              </p>
            </>
          )}
          {mode === "register" && (
            <p>
              Already have an account? <Link to="/login">Sign in</Link>
            </p>
          )}
          {!["login", "register"].includes(mode) && (
            <Link to="/login">Back to sign in</Link>
          )}
        </div>
      </div>
    </section>
  );
}
