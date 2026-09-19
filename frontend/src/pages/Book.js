import axios from "../api";
import { useEffect, useRef, useState } from "react";
import { Alert, Button, Col, Container, Modal, Row } from "react-bootstrap";
import { AddBook } from "../components/AddBook";
import { BookForm } from "../components/BookForm";
import { Bookshelf } from "../components/Bookshelf";

export async function fetchFinishedList(config) {
  const response = await axios.get("/books/finished/", config);
  return response.data ?? response;
}

function errorMessage(error, fallback) {
  const data = error.response?.data;
  if (data && typeof data === "object") {
    const details = Object.entries(data)
      .filter(([, value]) => typeof value === "string" || Array.isArray(value))
      .map(([field, value]) => `${field === "detail" || field === "non_field_errors" ? "" : `${field}: `}${Array.isArray(value) ? value.join(" ") : value}`);
    if (details.length) return `${fallback} ${details.join(" ")}`;
  }
  return `${fallback} Please try again.`;
}

function Book() {
  const [books, setBooks] = useState([]);
  const [editingBook, setEditingBook] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadFailed, setLoadFailed] = useState(false);
  const [loadAttempt, setLoadAttempt] = useState(0);
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setLoadFailed(false);
    setError("");
    axios.get("/books/")
      .then(({ data }) => { if (active) setBooks(data); })
      .catch((err) => {
        if (active) {
          setLoadFailed(true);
          setError(errorMessage(err, "Could not load your books."));
        }
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [loadAttempt]);

  async function mutate(request, onSuccess, message) {
    if (pending.current) return false;
    pending.current = true;
    setBusy(true);
    setError("");
    try {
      const response = await request();
      onSuccess(response.data);
      return true;
    } catch (err) {
      setError(errorMessage(err, message));
      return false;
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }

  const replaceBook = (saved) => setBooks((current) => current.map((book) => book.id === saved.id ? saved : book));
  const handleAddBook = (book) => mutate(
    () => axios.post("/books/", book),
    (saved) => setBooks((current) => [...current, saved]),
    "Could not add the book.",
  );
  const handleToggleBook = (book) => mutate(
    () => axios.patch(`/books/${book.id}/`, { finished: !book.finished }),
    replaceBook,
    "Could not change the reading status.",
  );
  const handleDeleteBook = (book) => mutate(
    () => axios.delete(`/books/${book.id}/`),
    () => setBooks((current) => current.filter((item) => item.id !== book.id)),
    "Could not delete the book.",
  );
  const handleEditBook = (changes) => mutate(
    () => axios.patch(`/books/${editingBook.id}/`, changes),
    (saved) => { replaceBook(saved); setEditingBook(null); },
    "Could not save your changes.",
  );
  function closeEditor() {
    if (pending.current) return;
    setEditingBook(null);
    setError("");
  }
  const sortedBooks = [...books].sort((a, b) => b.year - a.year);

  return (
    <Container className="mt-3">
      {error && !editingBook && <Alert variant="danger" role="alert">{error}</Alert>}
      {loading && <p role="status">Loading your books…</p>}
      {loadFailed && <Button className="mb-3" onClick={() => setLoadAttempt((value) => value + 1)}>Retry loading books</Button>}
      <Row>
        <Col lg={4}><AddBook handleAddBook={handleAddBook} busy={busy} disabled={loading || loadFailed} /></Col>
        {[false, true].map((finished) => (
          <Col lg={4} key={String(finished)}>
            <Bookshelf
              finished={finished}
              bookList={sortedBooks.filter((book) => book.finished === finished)}
              handleToggleBook={handleToggleBook}
              handleDeleteBook={handleDeleteBook}
              handleEditBook={(book) => { setError(""); setEditingBook(book); }}
              busy={busy || loading}
            />
          </Col>
        ))}
      </Row>
      <Modal show={Boolean(editingBook)} onHide={closeEditor} backdrop={busy ? "static" : true} keyboard={!busy} aria-labelledby="edit-book-heading">
        <Modal.Header closeButton={!busy}><Modal.Title id="edit-book-heading">Edit book</Modal.Title></Modal.Header>
        <Modal.Body>
          {error && <Alert variant="danger" role="alert">{error}</Alert>}
          {editingBook && <BookForm key={editingBook.id} initialBook={editingBook} onSave={handleEditBook} onCancel={closeEditor} busy={busy} />}
        </Modal.Body>
      </Modal>
    </Container>
  );
}

export default Book;
