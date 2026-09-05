from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import CustomUser
from books.models import Book


class BookOwnershipTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = CustomUser.objects.create_user("owner@example.com", "owner", "test-only-password")
        cls.other = CustomUser.objects.create_user("other@example.com", "other", "test-only-password")
        cls.book = Book.objects.create(user=cls.other, title="Private", author="Author", year=2025, finished=True)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.owner)

    def test_lists_never_expose_other_users_books(self):
        for path in ("/books/", "/books/finished/", "/books/unfinished/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data, [])

    def test_other_users_book_cannot_be_read_changed_or_deleted(self):
        for method in ("get", "patch", "put", "delete"):
            with self.subTest(method=method):
                response = getattr(self.client, method)(f"/books/{self.book.pk}/")
                self.assertEqual(response.status_code, 404)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

    def test_owner_cannot_be_spoofed_or_reassigned(self):
        response = self.client.post("/books/", {
            "user": self.other.pk, "title": "Mine", "author": "Author", "year": 2025, "finished": False,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"], self.owner.pk)
        response = self.client.patch(f'/books/{response.data["id"]}/', {"user": self.other.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"], self.owner.pk)

    def test_anonymous_and_invalid_token_requests_are_rejected(self):
        self.client.force_authenticate(None)
        for token in ("", "Token invalid", "Bearer invalid"):
            with self.subTest(token=token):
                self.client.credentials(HTTP_AUTHORIZATION=token)
                self.assertEqual(self.client.get("/books/").status_code, 401)
