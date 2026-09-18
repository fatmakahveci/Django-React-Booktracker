import { Button, Col, Row } from "react-bootstrap";
import "../assets/css/App.css";

export default function Book(props) {
  const { book } = props;
  const toggleButtonText = book.finished ? "Unfinish" : "Finish";
  return (
    <div className="row">
      <Row>
        <Col lg={3} sm={12}>
          Title:
        </Col>
        <Col lg={9} sm={12}>
          {book.title}
        </Col>
      </Row>
      <Row>
        <Col lg={3} sm={12}>
          Author:
        </Col>
        <Col lg={9} sm={12}>
          {book.author}
        </Col>
      </Row>
      <Row>
        <Col lg={3} sm={12}>
          Year:
        </Col>
        <Col lg={9} sm={12}>
          {book.year}
        </Col>
      </Row>
      <Row className="mt-3">
        <Col lg={4} sm={12} className="p-1 d-grid">
          <Button variant="outline-primary" disabled={props.busy} onClick={() => props.handleEditBook(book)}>Edit</Button>
        </Col>
        <Col lg={4} sm={12} className="p-1 d-grid">
          <Button
            variant="primary"
            disabled={props.busy}
            onClick={() => props.handleToggleBook(book)}
          >
            {toggleButtonText}
          </Button>
        </Col>
        <Col lg={4} sm={12} className="p-1 d-grid">
          <Button disabled={props.busy} variant="danger" onClick={() => props.handleDeleteBook(book)}>
            Delete
          </Button>
        </Col>
      </Row>
    </div>
  );
}
