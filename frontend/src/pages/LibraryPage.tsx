import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, ApiError, errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthProvider";
import { BookEditor, DeleteBook } from "../components/BookEditor";
import type { Book, Page, Summary } from "../types";
export function LibraryPage() {
  const { user } = useAuth();
  const [params, setParams] = useSearchParams();
  const urlSearch = params.get("search") || "";
  const [search, setSearch] = useState(urlSearch);
  const [data, setData] = useState<Page<Book> | null>(null);
  const [summary, setSummary] = useState<Summary>({
    total: 0,
    finished: 0,
    unfinished: 0,
  });
  const [revision, setRevision] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [editor, setEditor] = useState<Book | null | undefined>(undefined);
  const [deleting, setDeleting] = useState<Book | null>(null);
  const [pending, setPending] = useState<number | null>(null);
  useEffect(() => {
    setSearch(urlSearch);
  }, [urlSearch]);
  const query = params.toString();
  const page = Math.max(1, Number(params.get("page")) || 1);
  const filter = params.get("finished") || "";
  function update(key: string, value: string) {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    if (key !== "page") next.delete("page");
    setParams(next, { replace: key === "search" });
  }
  useEffect(() => {
    const timer = setTimeout(() => {
      if (search !== (params.get("search") || "")) {
        const next = new URLSearchParams(params);
        if (search) next.set("search", search);
        else next.delete("search");
        next.delete("page");
        setParams(next, { replace: true });
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [search, params, setParams]);
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    Promise.all([
      api<Page<Book>>(`books/?${query}`),
      api<Summary>("books/summary/"),
    ])
      .then(([books, counts]) => {
        if (active) {
          setData(books);
          setSummary(counts);
        }
      })
      .catch((e) => {
        if (!active) return;
        if (e instanceof ApiError && e.status === 404 && page > 1) {
          // Filtering or edits in another tab can remove the last page.
          const next = new URLSearchParams(params);
          next.delete("page");
          setParams(next, { replace: true });
        } else setError(errorMessage(e));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [query, revision, page, params, setParams]);
  function refresh(message: string) {
    setNotice(message);
    setRevision((n) => n + 1);
  }
  async function toggle(book: Book) {
    setPending(book.id);
    try {
      await api(`books/${book.id}/`, "PATCH", { finished: !book.finished });
      refresh(
        book.finished
          ? "Moved to your reading list."
          : "Another chapter completed.",
      );
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setPending(null);
    }
  }
  return (
    <section className="library">
      <div className="page-heading">
        <div>
          <p className="eyebrow">THE READING ROOM / {user?.user_name}</p>
          <h1>Your library.</h1>
          <p className="lede">A home for your next chapter.</p>
        </div>
        <button disabled={pending !== null} onClick={() => setEditor(null)}>
          <span aria-hidden="true">＋</span> Add a book
        </button>
      </div>
      <div className="stats" aria-label="Reading summary">
        <div>
          <span className="stat-value">
            {summary.total.toString().padStart(2, "0")}
          </span>
          <span>On your shelf</span>
        </div>
        <div>
          <span className="stat-value">
            {summary.unfinished.toString().padStart(2, "0")}
          </span>
          <span>Still to discover</span>
        </div>
        <div>
          <span className="stat-value">
            {summary.finished.toString().padStart(2, "0")}
          </span>
          <span>Stories finished</span>
        </div>
        <p>
          “A reader lives a<br />
          thousand lives.”<small>GEORGE R. R. MARTIN</small>
        </p>
      </div>
      <div className="library-toolbar">
        <div className="tabs" role="group" aria-label="Filter books">
          {[
            ["", "All books"],
            ["false", "To read"],
            ["true", "Finished"],
          ].map(([value, label]) => (
            <button
              className={filter === value ? "selected" : ""}
              aria-pressed={filter === value}
              key={label}
              onClick={() => update("finished", value)}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="search-sort">
          <label className="search">
            <span className="sr-only">Search books</span>
            <input
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search title, author or ISBN"
            />
          </label>
          <label>
            <span className="sr-only">Sort books</span>
            <select
              value={params.get("ordering") || "-year"}
              onChange={(e) => update("ordering", e.target.value)}
            >
              <option value="-year">Newest published</option>
              <option value="year">Oldest published</option>
              <option value="title">Title A–Z</option>
              <option value="author">Author A–Z</option>
              <option value="-rating">Highest rated</option>
              <option value="-created_at">Recently added</option>
            </select>
          </label>
        </div>
      </div>
      <p className="sr-only" role="status">
        {loading
          ? "Loading books…"
          : `${data?.count || 0} books found. ${notice}`}
      </p>
      {error && (
        <div className="error" role="alert">
          {error}{" "}
          <button
            className="text-button"
            onClick={() => setRevision((n) => n + 1)}
          >
            Try again
          </button>
        </div>
      )}
      {loading ? (
        <div className="empty">Opening your shelf…</div>
      ) : !error && data?.results.length ? (
        <>
          <div className="book-grid">
            {data.results.map((book, index) => (
              <article className="book-card" key={book.id}>
                <div className={`book-cover cover-${index % 4}`}>
                  {book.cover_url ? (
                    <img
                      src={book.cover_url}
                      alt={`Cover of ${book.title}`}
                      loading="lazy"
                      referrerPolicy="no-referrer"
                      onError={(e) => {
                        e.currentTarget.style.display = "none";
                      }}
                    />
                  ) : null}
                  <div className="cover-type">
                    <span>{book.author}</span>
                    <strong>{book.title}</strong>
                    <span className="cover-year">{book.year}</span>
                  </div>
                  <span
                    className={`status-label ${book.finished ? "done" : ""}`}
                  >
                    {book.finished ? "Finished" : "To read"}
                  </span>
                </div>
                <div className="book-info">
                  <h2>{book.title}</h2>
                  <p>
                    {book.author} <span aria-hidden="true">·</span> {book.year}
                  </p>
                  {book.rating && (
                    <p
                      className="rating"
                      aria-label={`Rated ${book.rating} out of 5`}
                    >
                      {"★".repeat(book.rating)}
                      <span aria-hidden="true">
                        {"☆".repeat(5 - book.rating)}
                      </span>
                    </p>
                  )}
                  {book.notes && <p className="book-note">{book.notes}</p>}
                  <div className="book-actions">
                    <button
                      className="text-button"
                      disabled={pending !== null}
                      onClick={() => void toggle(book)}
                    >
                      {book.finished ? "Read again" : "Mark finished"}
                    </button>
                    <div>
                      <button
                        className="text-button"
                        aria-label={`Edit ${book.title}`}
                        disabled={pending !== null}
                        onClick={() => setEditor(book)}
                      >
                        Edit
                      </button>
                      <button
                        className="text-button muted"
                        aria-label={`Remove ${book.title}`}
                        disabled={pending !== null}
                        onClick={() => setDeleting(book)}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              </article>
            ))}
          </div>
          <div className="pagination">
            <span>
              {data.count} {data.count === 1 ? "book" : "books"} · Page {page}{" "}
              of {Math.ceil(data.count / 12)}
            </span>
            <div>
              <button
                className="secondary"
                disabled={!data.previous}
                onClick={() => update("page", String(page - 1))}
              >
                Previous
              </button>
              <button
                className="secondary"
                disabled={!data.next}
                onClick={() => update("page", String(page + 1))}
              >
                Next
              </button>
            </div>
          </div>
        </>
      ) : (
        !error && (
          <div className="empty">
            <span className="empty-mark" aria-hidden="true">
              b.
            </span>
            <h2>
              {search || filter
                ? "No books on this shelf yet."
                : "Every library begins with one book."}
            </h2>
            <p>
              {search || filter
                ? "Try a different search or browse all your books."
                : "Add the book on your bedside table. Or the one you can’t stop thinking about."}
            </p>
            <button
              className="secondary"
              onClick={() => {
                if (search || filter) {
                  setSearch("");
                  setParams({});
                } else setEditor(null);
              }}
            >
              {search || filter ? "Show all books" : "Add your first book"}
            </button>
          </div>
        )
      )}
      {editor !== undefined && (
        <BookEditor
          book={editor}
          onClose={() => setEditor(undefined)}
          onSaved={() => {
            setEditor(undefined);
            refresh("Book saved.");
          }}
        />
      )}
      {deleting && (
        <DeleteBook
          book={deleting}
          onClose={() => setDeleting(null)}
          onDeleted={() => {
            setDeleting(null);
            if (data?.results.length === 1 && page > 1)
              update("page", String(page - 1));
            refresh("Book removed.");
          }}
        />
      )}
    </section>
  );
}
