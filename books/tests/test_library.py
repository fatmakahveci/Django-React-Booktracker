from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import CustomUser
from books.models import Book


class LibraryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user("library@example.com", "library", "test-pass")
        Book.objects.bulk_create(
            [
                Book(
                    user=cls.user,
                    title=f"Story {i:02}",
                    author="Ursula" if i % 2 else "Virginia",
                    year=2000 + i,
                    finished=i % 2 == 0,
                )
                for i in range(25)
            ]
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_search_filter_order_and_bounded_pagination(self):
        first = self.client.get("/books/?ordering=title").data
        self.assertEqual(first["count"], 25)
        self.assertEqual(len(first["results"]), 12)
        self.assertEqual(first["results"][0]["title"], "Story 00")
        self.assertEqual(len(self.client.get("/books/?page=3").data["results"]), 1)
        found = self.client.get("/books/?search=Ursula&finished=false&ordering=year").data
        self.assertEqual(found["count"], 12)
        self.assertEqual(found["results"][0]["year"], 2001)
        self.assertEqual(self.client.get("/books/?year=no").status_code, 400)
        self.assertEqual(self.client.get("/books/?finished=yes").status_code, 400)
        self.assertEqual(
            self.client.get("/books/summary/").data, {"total": 25, "finished": 13, "unfinished": 12}
        )

    def test_metadata_validation_and_error_contract(self):
        body = {
            "title": "A book",
            "author": "An author",
            "year": 2026,
            "isbn": "9780140328721",
            "rating": 5,
            "notes": "A favourite",
            "finished": True,
            "started_on": "2026-01-01",
            "finished_on": "2026-02-01",
        }
        response = self.client.post("/books/", body)
        self.assertEqual(response.status_code, 201)
        path = f"/books/{response.data['id']}/"
        for update in [
            {"isbn": "1234567890"},
            {"rating": 6},
            {"year": -1},
            {"cover_url": "http://example.com/cover.jpg"},
            {"finished_on": "2025-01-01"},
        ]:
            with self.subTest(update=update):
                response = self.client.patch(path, update)
                self.assertEqual(response.status_code, 400)
                self.assertIn("fields", response.data["error"])
        self.assertIsNone(self.client.patch(path, {"finished": False}).data["finished_on"])

    def test_isbn_rejects_unicode_digits_and_non_isbn_bar_codes(self):
        for isbn in ("²" * 13, "²" * 10, "９７８０１４０３２８７２１", "0000000000000"):
            with self.subTest(isbn=isbn):
                response = self.client.post(
                    "/books/",
                    {"title": "A book", "author": "An author", "year": 2026, "isbn": isbn},
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("isbn", response.data["error"]["fields"])
        for isbn, normalized in (
            ("978-0-14-032872-1", "9780140328721"),
            ("0-8044-2957-x", "080442957X"),
        ):
            with self.subTest(isbn=isbn):
                response = self.client.post(
                    "/books/",
                    {"title": "A book", "author": "An author", "year": 2026, "isbn": isbn},
                )
                self.assertEqual(response.status_code, 201)
                self.assertEqual(response.data["isbn"], normalized)

    def test_reopening_a_book_clears_finish_date_before_validating_new_start(self):
        book = Book.objects.create(
            user=self.user,
            title="Read again",
            author="Reader",
            year=2026,
            finished=True,
            started_on="2026-01-01",
            finished_on="2026-02-01",
        )
        response = self.client.patch(
            f"/books/{book.pk}/", {"finished": False, "started_on": "2026-03-01"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["finished_on"])
        response = self.client.patch(f"/books/{book.pk}/", {"finished_on": "2026-04-01"})
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["finished_on"])

    def test_summary_uses_one_query_and_excludes_other_users(self):
        other = CustomUser.objects.create_user("other@example.com", "other_reader", "test-pass")
        Book.objects.create(user=other, title="Private", author="Other", year=2026, finished=True)
        with self.assertNumQueries(1):
            response = self.client.get("/books/summary/")
        self.assertEqual(response.data, {"total": 25, "finished": 13, "unfinished": 12})
        self.client.force_authenticate(other)
        Book.objects.filter(user=other).delete()
        self.assertEqual(
            self.client.get("/books/summary/").data, {"total": 0, "finished": 0, "unfinished": 0}
        )
