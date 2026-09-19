from django.db import models

from accounts.models import CustomUser


class Book(models.Model):
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name="books")
    title = models.CharField(max_length=140)
    author = models.CharField(max_length=140)
    year = models.IntegerField()
    finished = models.BooleanField(default=False)
    isbn = models.CharField(max_length=13, blank=True)
    cover_url = models.URLField(max_length=500, blank=True)
    notes = models.TextField(blank=True, max_length=10000)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    started_on = models.DateField(null=True, blank=True)
    finished_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __repr__(self) -> str:
        return f"""
        user: {self.user}
        title: {self.title}
        author: {self.author}
        year: {self.year}
        finished: {self.finished}
        """

    class Meta:
        ordering = ["-year", "-pk"]
        indexes = [models.Index(fields=["user", "finished", "-year"], name="book_user_shelf_year")]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__isnull=True) | models.Q(rating__gte=1, rating__lte=5),
                name="book_rating_1_to_5",
            )
        ]
