from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @permission_classes([IsAuthenticated,])
    def filter_book(self, request, finished):
        book_list = Book.objects.filter(user=request.user, finished=finished)
        serializer = self.get_serializer(book_list, many=True)
        return Response(serializer.data)

    @permission_classes([IsAuthenticated,])
    @action(detail=False)
    def finished(self, request):
        return self.filter_book(request, finished=True)

    @permission_classes([IsAuthenticated,])
    @action(detail=False)
    def unfinished(self, request):
        return self.filter_book(request, finished=False)
