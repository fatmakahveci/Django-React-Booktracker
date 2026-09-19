from datetime import date
from urllib.parse import urlparse

from rest_framework import serializers

from books.models import Book


class BookSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField(min_value=1, max_value=9999)
    rating = serializers.IntegerField(min_value=1, max_value=5, allow_null=True, required=False)
    isbn = serializers.CharField(max_length=32, allow_blank=True, required=False)

    class Meta:
        model = Book
        fields = (
            "id",
            "user",
            "title",
            "author",
            "year",
            "finished",
            "isbn",
            "cover_url",
            "notes",
            "rating",
            "started_on",
            "finished_on",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "created_at", "updated_at")

    def validate_year(self, value):
        if not 1 <= value <= date.today().year + 2:
            raise serializers.ValidationError("Enter a valid publication year.")
        return value

    def validate_isbn(self, value):
        value = value.replace("-", "").replace(" ", "").upper()
        if not value:
            return value
        valid = False
        # str.isdigit() includes characters such as superscripts that int() cannot parse.
        if value.isascii() and len(value) == 13 and value.isdigit() and value[:3] in ("978", "979"):
            valid = (
                sum(int(digit) * (1 if i % 2 == 0 else 3) for i, digit in enumerate(value)) % 10
                == 0
            )
        elif (
            value.isascii()
            and len(value) == 10
            and value[:9].isdigit()
            and (value[-1].isdigit() or value[-1] == "X")
        ):
            valid = (
                sum(
                    (10 - i) * (10 if digit == "X" else int(digit)) for i, digit in enumerate(value)
                )
                % 11
                == 0
            )
        if not valid:
            raise serializers.ValidationError("Enter a valid ISBN-10 or ISBN-13.")
        return value

    def validate_cover_url(self, value):
        # Browser-only image URLs; the API never fetches arbitrary remote resources.
        if value and urlparse(value).scheme != "https":
            raise serializers.ValidationError("Cover images must use HTTPS.")
        return value

    def validate(self, attrs):
        if not attrs.get("finished", getattr(self.instance, "finished", False)):
            # Clear the old finish date before checking dates when a book is reopened.
            attrs["finished_on"] = None
        start = attrs.get("started_on", getattr(self.instance, "started_on", None))
        finish = attrs.get("finished_on", getattr(self.instance, "finished_on", None))
        if start and finish and finish < start:
            raise serializers.ValidationError(
                {"finished_on": "Finish date cannot precede start date."}
            )
        return attrs
