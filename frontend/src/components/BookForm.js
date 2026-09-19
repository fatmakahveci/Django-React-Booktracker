import { useState } from "react";
import { Button, FloatingLabel, Form } from "react-bootstrap";

const blankBook = () => ({ title: "", author: "", year: "", finished: false });

export function BookForm({ initialBook, onSave, onCancel, busy, disabled = false }) {
  const [book, setBook] = useState(() => initialBook || blankBook());
  const editing = Boolean(initialBook);
  const prefix = editing ? "edit-book" : "add-book";

  function handleChange(event) {
    const { name, value, type, checked } = event.target;
    setBook((current) => ({ ...current, [name]: type === "checkbox" ? checked : value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (busy || disabled) return;
    const saved = await onSave({
      title: book.title.trim(),
      author: book.author.trim(),
      year: Number(book.year),
      ...(!editing && { finished: book.finished }),
    });
    if (saved && !editing) setBook(blankBook());
  }

  return (
    <Form onSubmit={handleSubmit} aria-label={editing ? "Edit book" : "Add book"}>
      <fieldset disabled={busy || disabled}>
        {[
          { name: "title", label: "Title", type: "text" },
          { name: "author", label: "Author", type: "text" },
          { name: "year", label: "Year", type: "number" },
        ].map(({ name, label, type }) => (
          <FloatingLabel key={name} controlId={`${prefix}-${name}`} label={label} className="mb-2">
            <Form.Control
              type={type}
              name={name}
              placeholder={label}
              value={book[name]}
              onChange={handleChange}
              maxLength={type === "text" ? 140 : undefined}
              pattern={type === "text" ? ".*\\S.*" : undefined}
              step={type === "number" ? 1 : undefined}
              required
            />
          </FloatingLabel>
        ))}
        {!editing && (
          <Form.Check id={`${prefix}-finished`} type="checkbox" name="finished"
            label="Finished?" checked={book.finished} onChange={handleChange} />
        )}
        <div className="d-flex gap-2 mt-2">
          <Button type="submit" className="flex-grow-1">
            {busy ? "Saving…" : editing ? "Save changes" : "Save"}
          </Button>
          {onCancel && <Button variant="secondary" onClick={onCancel}>Cancel</Button>}
        </div>
      </fieldset>
    </Form>
  );
}
