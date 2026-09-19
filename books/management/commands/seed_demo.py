import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import CustomUser
from books.models import Book


class Command(BaseCommand):
    help = "Create a synthetic local demo library; never overwrite an existing account."

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Demo seeding is disabled outside development.")
        password = os.environ.get("BOOKTRACKER_DEMO_PASSWORD", "")
        if len(password) < 12:
            raise CommandError("Set BOOKTRACKER_DEMO_PASSWORD to at least 12 characters.")
        if CustomUser.objects.filter(email="demo@example.invalid").exists():
            raise CommandError("Demo account already exists; no data changed.")
        user = CustomUser.objects.create_user(
            "demo@example.invalid", "the_reading_room", password, email_verified=True
        )
        books = [
            ("The Left Hand of Darkness", "Ursula K. Le Guin", 1969, True, 5),
            ("A Room of One’s Own", "Virginia Woolf", 1929, True, 5),
            ("The Dispossessed", "Ursula K. Le Guin", 1974, False, None),
            ("The Book of Disquiet", "Fernando Pessoa", 1982, False, None),
            ("Piranesi", "Susanna Clarke", 2020, True, 5),
            ("Invisible Cities", "Italo Calvino", 1972, False, None),
            ("The Waves", "Virginia Woolf", 1931, False, None),
            ("The Summer Book", "Tove Jansson", 1972, True, 4),
        ]
        Book.objects.bulk_create(
            [
                Book(user=user, title=title, author=author, year=year, finished=done, rating=rating)
                for title, author, year, done, rating in books
            ]
        )
        self.stdout.write(
            "Synthetic demo account and eight books created. Sign in as demo@example.invalid."
        )
