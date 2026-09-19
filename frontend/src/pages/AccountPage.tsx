import { useState, type FormEvent } from "react";
import { api, errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthProvider";
import type { User } from "../types";
type AccountAction = "me" | "password/change" | "sessions/revoke" | "account";
export function AccountPage() {
  const { user, setUser } = useAuth();
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(
    event: FormEvent<HTMLFormElement>,
    action: AccountAction,
  ) {
    event.preventDefault();
    const form = event.currentTarget;
    const body = Object.fromEntries(new FormData(form));
    setError("");
    setMessage("");
    setBusy(true);
    try {
      if (action === "me") {
        setUser(await api<User>("auth/me/", "PATCH", body));
        setMessage("Profile updated.");
      } else {
        await api(
          `auth/${action}/`,
          action === "account" ? "DELETE" : "POST",
          body,
        );
        setUser(null);
      }
      if (action !== "me") form.reset();
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="account">
      <p className="eyebrow">YOUR SPACE</p>
      <h1>Account & security.</h1>
      <p className="lede">A few details to keep your reading life yours.</p>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      {message && (
        <p className="success" role="status">
          {message}
        </p>
      )}
      <div className="account-grid">
        <section className="panel">
          <h2>Your profile</h2>
          <p>
            {user?.email}{" "}
            <span className="pill">
              {user?.email_verified ? "Verified" : "Unverified"}
            </span>
          </p>
          <form onSubmit={(e) => void submit(e, "me")}>
            <label>
              Username
              <input
                name="user_name"
                defaultValue={user?.user_name}
                minLength={4}
                maxLength={24}
                required
              />
            </label>
            <button disabled={busy}>Save profile</button>
          </form>
        </section>
        <section className="panel">
          <h2>Change password</h2>
          <p>Changing your password signs you out on every device.</p>
          <form onSubmit={(e) => void submit(e, "password/change")}>
            <label>
              Current password
              <input
                name="current_password"
                type="password"
                autoComplete="current-password"
                maxLength={128}
                required
              />
            </label>
            <label>
              New password
              <input
                name="new_password"
                type="password"
                autoComplete="new-password"
                minLength={8}
                maxLength={128}
                required
              />
            </label>
            <button disabled={busy}>Change password</button>
          </form>
        </section>
        <section className="panel">
          <h2>Sign out everywhere</h2>
          <p>End every active session, including this one.</p>
          <form onSubmit={(e) => void submit(e, "sessions/revoke")}>
            <label>
              Confirm your password
              <input
                name="password"
                type="password"
                autoComplete="current-password"
                maxLength={128}
                required
              />
            </label>
            <button disabled={busy} className="secondary">
              Sign out all devices
            </button>
          </form>
        </section>
        <section className="panel danger-panel">
          <h2>Delete your account</h2>
          <p>Your account, books and notes will be permanently deleted.</p>
          <form onSubmit={(e) => void submit(e, "account")}>
            <label>
              Your password
              <input
                name="password"
                type="password"
                autoComplete="current-password"
                maxLength={128}
                required
              />
            </label>
            <label className="check-label">
              <input type="checkbox" required />I understand this cannot be
              undone.
            </label>
            <button className="danger" disabled={busy}>
              Permanently delete account
            </button>
          </form>
        </section>
      </div>
    </section>
  );
}
