import axios from "axios";
import { useContext, useEffect, useMemo, useState } from "react";
import { Col, Container, Row } from "react-bootstrap";
import { AddBook } from "../components/AddBook";
import { Bookshelf } from "../components/Bookshelf";
import AuthContext from "../context/AuthContext";

function Book() {
  let { authTokens } = useContext(AuthContext);

  const [unfinishedList, setUnfinishedList] = useState([]);
  const [finishedList, setFinishedList] = useState([]);

  axios.defaults.baseURL = "http://localhost:8000/books";

  const config = useMemo(
    () => ({
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + authTokens?.access,
      },
    }),
    [authTokens?.access]
  );

  useEffect(async () => {
    const unfinishedList = await axios
      .get("/unfinished/", config)
      .then((response) => {
        return response.data;
      })
      .catch((err) => {
        console.log(err);
      });
    setUnfinishedList(unfinishedList);

    const finishedList = await axios
      .get("/finished/", config)
      .then((response) => {
        return response.data;
      })
      .catch((err) => {
        console.log(err);
      });
    setFinishedList(finishedList);
  }, [config]);

  async function setFinished(book, finished) {
    await axios
      .patch(`/${book.id}/`, { finished: finished }, config)
      .then((response) => {
        return response;
      })
      .catch((err) => {
        console.log(err);
      });
  }

  async function deleteBook(book) {
    await axios.delete(`${book.id}/`, config);
  }

  const handleAddBook = async (book) => {
    let savedBook = await axios
      .post("/", book, config)
      .then((response) => {
        return response.data;
      })
      .catch((err) => {
        console.log(err);
      });
    if (savedBook.finished) {
      setFinishedList([...finishedList, savedBook]);
    } else {
      setUnfinishedList([...unfinishedList, savedBook]);
    }
  };

  const handleToggleBook = async (book) => {
    const moveBook = (sourceList, setSourceList, destList, setDestList) => {
      const newSourceList = sourceList.filter((mBook) => {
        return mBook.id !== book.id;
      });
      setSourceList(newSourceList);

      const newDestList = [...destList, { ...book, finished: !book.finished }];
      setDestList(newDestList);
    };

    await setFinished(book, !book.finished);

    if (book.finished) {
      moveBook(
        finishedList,
        setFinishedList,
        unfinishedList,
        setUnfinishedList
      );
    } else {
      moveBook(
        unfinishedList,
        setUnfinishedList,
        finishedList,
        setFinishedList
      );
    }
  };

  const handleDeleteBook = (book) => {
    const deleteFromList = (list, setList) => {
      const newList = list.filter((mBook) => mBook.id !== book.id);
      setList(newList);
    };

    deleteBook(book).then((_) => {
      if (book.finished) {
        deleteFromList(finishedList, setFinishedList);
      } else {
        deleteFromList(unfinishedList, setUnfinishedList);
      }
    });
  };

  return (
    <Container className="mt-3">
      <article className="row">
        <Row>
          <Col lg={4}>
            <AddBook handleAddBook={handleAddBook} />
          </Col>
          <Col lg={4}>
            <Bookshelf
              finished={false}
              bookList={unfinishedList}
              handleToggleBook={handleToggleBook}
              handleDeleteBook={handleDeleteBook}
            />
          </Col>
          <Col lg={4}>
            <Bookshelf
              finished={true}
              bookList={finishedList}
              handleToggleBook={handleToggleBook}
              handleDeleteBook={handleDeleteBook}
            />
          </Col>
        </Row>
      </article>
    </Container>
  );
}

export default Book;
