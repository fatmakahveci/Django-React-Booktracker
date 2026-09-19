import { useEffect, useRef, useState, type FormEvent } from "react";
import { api, errorMessage } from "../api/client";
import type { Book, BookInput } from "../types";
export function BookEditor({
  book,
  onClose,
  onSaved,
}: {
  book: Book | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [finished, setFinished] = useState(book?.finished || false);
  useEffect(() => {
    const opener = document.activeElement as HTMLElement | null;
    const el = dialog.current!;
    el.showModal();
    el.querySelector<HTMLInputElement>('input[name="title"]')?.focus();
    return () => {
      el.close();
      opener?.focus();
    };
  }, []);
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setBusy(true);
    setError("");
    const body: BookInput = {
      title: String(data.get("title")).trim(),
      author: String(data.get("author")).trim(),
      year: Number(data.get("year")),
      finished,
      isbn: String(data.get("isbn")),
      cover_url: String(data.get("cover_url")),
      notes: String(data.get("notes")),
      rating: data.get("rating") ? Number(data.get("rating")) : null,
      started_on: String(data.get("started_on") || "") || null,
      finished_on: finished
        ? String(data.get("finished_on") || "") || null
        : null,
    };
    try {
      await api(
        `books/${book ? `${book.id}/` : ""}`,
        book ? "PATCH" : "POST",
        body,
      );
      onSaved();
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <dialog
      ref={dialog}
      aria-labelledby="editor-title"
      onCancel={(event) => {
        event.preventDefault();
        if (!busy) onClose();
      }}
    >
      <form onSubmit={(e) => void save(e)}>
        <div className="dialog-heading">
          <div>
            <p className="eyebrow">YOUR COLLECTION</p>
            <h2 id="editor-title">
              {book ? "Edit your book" : "Make room for a book"}
            </h2>
          </div>
          <button
            className="icon-button"
            type="button"
            aria-label="Close book editor"
            disabled={busy}
            onClick={onClose}
          >
            ×
          </button>
        </div>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        <div className="form-grid">
          <label className="wide">
            Title
            <input
              name="title"
              defaultValue={book?.title}
              maxLength={140}
              required
            />
          </label>
          <label>
            Author
            <input
              name="author"
              defaultValue={book?.author}
              maxLength={140}
              required
            />
          </label>
          <label>
            Publication year
            <input
              name="year"
              type="number"
              min={1}
              max={new Date().getFullYear() + 2}
              defaultValue={book?.year || new Date().getFullYear()}
              required
            />
          </label>
          <label>
            ISBN <span className="muted">(optional)</span>
            <input name="isbn" defaultValue={book?.isbn} maxLength={20} />
          </label>
          <label>
            Rating
            <select
              aria-label="Rating"
              name="rating"
              defaultValue={book?.rating || ""}
            >
              <option value="">Not rated</option>
              {[1, 2, 3, 4, 5].map((n) => (
                <option value={n} key={n}>
                  {n} / 5
                </option>
              ))}
            </select>
          </label>
          <label className="wide">
            Cover image URL <span className="muted">(optional)</span>
            <input
              name="cover_url"
              type="url"
              placeholder="https://…"
              defaultValue={book?.cover_url}
              maxLength={500}
            />
            <span className="field-hint">
              External images load from the address you provide.
            </span>
          </label>
          <label className="check-label wide">
            <input
              name="finished"
              type="checkbox"
              checked={finished}
              onChange={(e) => setFinished(e.target.checked)}
            />
            I finished this book
          </label>
          <label>
            Started on
            <input
              name="started_on"
              type="date"
              defaultValue={book?.started_on || ""}
            />
          </label>
          {finished && (
            <label>
              Finished on
              <input
                name="finished_on"
                type="date"
                defaultValue={book?.finished_on || ""}
              />
            </label>
          )}
          <label className="wide">
            Reading notes
            <textarea
              name="notes"
              rows={4}
              maxLength={10000}
              placeholder="A thought, a favourite passage, something to remember…"
              defaultValue={book?.notes}
            />
          </label>
        </div>
        <div className="dialog-actions">
          <button
            type="button"
            className="secondary"
            disabled={busy}
            onClick={onClose}
          >
            Cancel
          </button>
          <button disabled={busy}>
            {busy ? "Saving…" : book ? "Save changes" : "Add book"}
          </button>
        </div>
      </form>
    </dialog>
  );
}
export function DeleteBook({
  book,
  onClose,
  onDeleted,
}: {
  book: Book;
  onClose: () => void;
  onDeleted: () => void;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    const opener = document.activeElement as HTMLElement | null;
    const dialog = ref.current!;
    dialog.showModal();
    dialog.querySelector<HTMLButtonElement>("button")?.focus();
    return () => {
      dialog.close();
      opener?.focus();
    };
  }, []);
  async function remove() {
    setBusy(true);
    try {
      await api(`books/${book.id}/`, "DELETE");
      onDeleted();
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <dialog
      ref={ref}
      aria-labelledby="delete-title"
      onCancel={(e) => {
        e.preventDefault();
        if (!busy) onClose();
      }}
    >
      <h2 id="delete-title">Remove “{book.title}”?</h2>
      <p>This also deletes its notes and reading dates.</p>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      <div className="dialog-actions">
        <button className="secondary" disabled={busy} onClick={onClose}>
          Keep book
        </button>
        <button
          className="danger"
          disabled={busy}
          onClick={() => void remove()}
        >
          {busy ? "Removing…" : "Remove book"}
        </button>
      </div>
    </dialog>
  );
}
