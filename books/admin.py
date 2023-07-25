from django.contrib import admin
from .models import Book


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'year', 'finished') # 'user', 


admin.site.register(Book, BookAdmin)
