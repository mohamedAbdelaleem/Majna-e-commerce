from rest_framework.pagination import PageNumberPagination


class PagePagination(PageNumberPagination):
    page_size = 12


paginator = PagePagination()
