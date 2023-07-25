import logging
from books.models import Book
from books.tests.base import BaseBookTest
from rest_framework import status


class BookAPITest(BaseBookTest):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_save_books_with_valid_credentials(self):
        """
        Save books if credentials are valid, return status code 200
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/books/",
            {
                "user": self.user.id,
                "title": self.title,
                "author": self.author,
                "year": self.year,
                "finished": self.finished,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_save_books_with_invalid_credentials_missing_user(self):
        """
        Do not save books if credentials are invalid, return status code 400
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/books/",
            {
                "title": self.title,
                "author": self.author,
                "year": self.year,
                "finished": self.finished,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_books_with_invalid_credentials_missing_user(self):
        """
        Do not save books if informations are invalid, return status code 400
        Here title is missing.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/books/",
            {
                "user": self.user.id,
                "author": self.author,
                "year": self.year,
                "finished": self.finished,
            },
        )
        self.assertTrue("This field is required." in str(response.content))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_books_with_valid_credentials(self):
        """
        Save books if credentials are valid, return status code 200
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/books/",
            {
                "user": self.user.id,
                "title": self.title,
                "author": self.author,
                "year": self.year,
                "finished": self.finished,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get("/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_finished_books_with_valid_credentials(self):
        """
        Save books if credentials are valid, return status code 200
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/books/",
            {
                "user": self.user.id,
                "title": self.title,
                "author": self.author,
                "year": self.year,
                "finished": self.finished,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get("/books/finished/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_unfinished_books_with_valid_credentials(self):
        """
        Save books if credentials are valid, return status code 200
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/books/",
            {
                "user": self.user.id,
                "title": self.title,
                "author": self.author,
                "year": self.year,
                "finished": self.finished,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get("/books/unfinished/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_make_finished_book_unfinished(self):
        """
        Change book's finished to unfinished
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/books/",
            {
                "user": self.user.id,
                "title": self.title,
                "author": self.author,
                "year": self.year,
                "finished": True,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.patch(
            f"/books/1/",
            {"finished": False},
        )
        self.assertFalse(Book.objects.get(user=self.user).finished)

    def test_make_unfinished_book_finished(self):
        """
        Change book's unfinished to finished
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/books/",
            {
                "user": self.user.id,
                "title": self.title,
                "author": self.author,
                "year": self.year,
                "finished": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.patch(
            f"/books/1/",
            {"finished": True},
        )
        self.assertTrue(Book.objects.get(user=self.user).finished)

    def test_delete_valid_book(self):
        """
        Delete a valid book, return status code 204
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/books/",
            {
                "user": self.user.id,
                "title": self.title,
                "author": self.author,
                "year": self.year,
                "finished": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.delete("/books/1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
