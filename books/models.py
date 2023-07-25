from django.db import models
from accounts.models import CustomUser


class Book(models.Model):
    user = models.ForeignKey(
        to=CustomUser, on_delete=models.CASCADE, related_name="books"
    )
    title = models.CharField(max_length=140)
    author = models.CharField(max_length=140)
    year = models.IntegerField()
    finished = models.BooleanField()

    def __repr__(self) -> str:
        return f"""
        user: {self.user}
        title: {self.title}
        author: {self.author}
        year: {self.year}
        finished: {self.finished}
        """

    class Meta:
        ordering = ["-year"]
