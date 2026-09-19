from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "user", "year", "finished")
    list_select_related = ("user",)
    search_fields = ("title", "author", "isbn")
    list_filter = ("finished",)
