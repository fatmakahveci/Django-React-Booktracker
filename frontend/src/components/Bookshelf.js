import { Table } from "react-bootstrap";
import "../assets/css/App.css";
import Book from "./ToggleBook";

export function Bookshelf(props) {
  const bookshelfName = props.finished ? "Finished Books" : "Unfinished Books";

  let { bookList } = props;
  console.log(bookList);
  bookList = bookList ? bookList : [];

  return (
    <div className="card row">
      <div className="card-header">{bookshelfName}</div>
      <div className="card-body p-0">
        <Table className="p-0 m-0">
          <tbody>
            {bookList.map((book) => {
              return (
                <tr key={book.id}>
                  <td className="p-3">
                    <Book
                      book={book}
                      handleToggleBook={props.handleToggleBook}
                      handleDeleteBook={props.handleDeleteBook}
                    />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </Table>
      </div>
    </div>
  );
}
