import { Card } from "react-bootstrap";
import { BookForm } from "./BookForm";

export function AddBook({ handleAddBook, busy, disabled }) {
  return (
    <section className="input_section">
      <Card>
        <Card.Header>Add a new book</Card.Header>
        <Card.Body>
          <BookForm onSave={handleAddBook} busy={busy} disabled={disabled} />
        </Card.Body>
      </Card>
    </section>
  );
}
