import { useEffect, useState, Component, type ReactNode } from "react";
import {
  Link,
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import { useAuth } from "./auth/AuthProvider";
import { errorMessage } from "./api/client";
import { AuthPage } from "./pages/AuthPage";
import { LibraryPage } from "./pages/LibraryPage";
import { AccountPage } from "./pages/AccountPage";
class ErrorBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? (
      <main id="main" className="empty">
        <h1>Something went wrong</h1>
        <p>Reload to try again. Your saved books are safe.</p>
        <button onClick={() => location.reload()}>Reload</button>
      </main>
    ) : (
      this.props.children
    );
  }
}
function Protected({ children }: { children: ReactNode }) {
  const { user, loading, error, reload } = useAuth();
  if (loading)
    return (
      <p role="status" className="empty">
        Opening your library…
      </p>
    );
  if (error)
    return (
      <div className="empty" role="alert">
        {error}
        <button onClick={() => void reload()}>Retry</button>
      </div>
    );
  return user ? children : <Navigate to="/login" replace />;
}
export default function App() {
  const { user, signOut } = useAuth();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const location = useLocation();
  useEffect(() => {
    document.title = `${location.pathname === "/library" ? "Your library" : location.pathname === "/account" ? "Your account" : "A little space for your reading"} · Booktracker`;
    document.getElementById("main")?.focus();
  }, [location.pathname]);
  async function logout() {
    setBusy(true);
    setError("");
    try {
      await signOut();
    } catch (e) {
      setError(
        errorMessage(e) + " Sign out again to finish ending your session.",
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="header">
        <Link className="brand" to={user ? "/library" : "/"}>
          <span className="brand-mark" aria-hidden="true">
            b.
          </span>
          booktracker<span className="brand-dot">/</span>
        </Link>
        <nav aria-label="Main navigation">
          {user ? (
            <>
              <NavLink to="/library">Library</NavLink>
              <NavLink to="/account">Account</NavLink>
              <button
                className="text-button"
                disabled={busy}
                onClick={() => void logout()}
              >
                {busy ? "Signing out…" : "Sign out"}
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login">Sign in</NavLink>
              <Link className="button small" to="/register">
                Start a library
              </Link>
            </>
          )}
        </nav>
      </header>
      {error && (
        <p className="error banner" role="alert">
          {error}
        </p>
      )}
      <ErrorBoundary>
        <main id="main" tabIndex={-1}>
          <Routes>
            <Route
              path="/"
              element={user ? <Navigate to="/library" replace /> : <Landing />}
            />
            <Route
              path="/library"
              element={
                <Protected>
                  <LibraryPage />
                </Protected>
              }
            />
            <Route
              path="/account"
              element={
                <Protected>
                  <AccountPage />
                </Protected>
              }
            />
            {[
              "login",
              "register",
              "forgot-password",
              "reset-password",
              "verify-email",
              "resend-verification",
            ].map((mode) => (
              <Route
                key={mode}
                path={`/${mode}`}
                element={<AuthPage mode={mode} />}
              />
            ))}
            <Route
              path="*"
              element={
                <div className="empty">
                  <h1>This page is still unwritten.</h1>
                  <p>Let's return to your next good read.</p>
                  <Link to="/">Back home</Link>
                </div>
              }
            />
          </Routes>
        </main>
      </ErrorBoundary>
      <footer>
        <span>booktracker / A little space for your reading.</span>
        <span>Read at your own pace.</span>
      </footer>
    </>
  );
}
function Landing() {
  return (
    <section className="landing">
      <div>
        <p className="eyebrow">YOUR PERSONAL READING COMPANION</p>
        <h1>
          Good books.
          <br />A place to keep them.
        </h1>
        <p className="lede">
          The ones you loved. The ones you’re reading.
          <br />
          The stories you haven’t met yet. Make a little room for all of them.
        </p>
        <Link className="button" to="/register">
          Build your bookshelf <span aria-hidden="true">↗</span>
        </Link>
        <p className="muted">
          Your books, notes and reading memories. All in one quiet corner.
        </p>
      </div>
      <div
        className="landing-shelf"
        aria-label="A preview of a personal reading list"
      >
        <p className="eyebrow">ON THE SHELF</p>
        {[
          ["01", "The Left Hand of Darkness", "Ursula K. Le Guin", "Finished"],
          ["02", "A Room of One’s Own", "Virginia Woolf", "Reading"],
          ["03", "The Dispossessed", "Ursula K. Le Guin", "Up next"],
        ].map(([n, title, author, status]) => (
          <div className="sample-book" key={n}>
            <span className="sample-number">{n}</span>
            <div>
              <h2>{title}</h2>
              <p>{author}</p>
            </div>
            <span className="pill">{status}</span>
          </div>
        ))}
        <p className="shelf-caption">
          A few possibilities for your next chapter.
        </p>
      </div>
    </section>
  );
}
