from django.db.models import Count, F, Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from accounts.schema import SummarySerializer

from .models import Book
from .serializers import BookSerializer


class StableOrderingFilter(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view) or []
        expressions = []
        for field in ordering:
            expression = F(field.lstrip("-"))
            expressions.append(
                expression.desc(nulls_last=True)
                if field.startswith("-")
                else expression.asc(nulls_last=True)
            )
        return queryset.order_by(*expressions, "-pk")


class LibraryPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(parameters=[OpenApiParameter("finished", bool), OpenApiParameter("year", int)])
class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    pagination_class = LibraryPagination
    filter_backends = [filters.SearchFilter, StableOrderingFilter]
    search_fields = ["title", "author", "isbn"]
    ordering_fields = ["title", "author", "year", "rating", "created_at"]
    ordering = ["-year", "-id"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Book.objects.none()
        queryset = Book.objects.filter(user=self.request.user)
        finished = self.request.query_params.get("finished")
        if finished is not None:
            if finished not in ("true", "false"):
                raise ValidationError({"finished": "Use true or false."})
            queryset = queryset.filter(finished=finished == "true")
        year = self.request.query_params.get("year")
        if year:
            try:
                queryset = queryset.filter(year=int(year))
            except ValueError:
                raise ValidationError({"year": "Use an integer."}) from None
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(responses=BookSerializer(many=True))
    @action(detail=False, pagination_class=None)
    def finished(self, request):
        return Response(
            self.get_serializer(self.get_queryset().filter(finished=True), many=True).data
        )

    @extend_schema(responses=BookSerializer(many=True))
    @action(detail=False, pagination_class=None)
    def unfinished(self, request):
        return Response(
            self.get_serializer(self.get_queryset().filter(finished=False), many=True).data
        )

    @extend_schema(responses=SummarySerializer, parameters=[])
    @action(detail=False, pagination_class=None, filter_backends=[])
    def summary(self, request):
        counts = Book.objects.filter(user=request.user).aggregate(
            total=Count("pk"), finished=Count("pk", filter=Q(finished=True))
        )
        # Use one database snapshot so concurrent edits cannot produce conflicting counts.
        return Response({**counts, "unfinished": counts["total"] - counts["finished"]})
