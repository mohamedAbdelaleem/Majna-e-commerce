from rest_framework.pagination import PageNumberPagination


class PagePagination(PageNumberPagination):
    page_size = 12


class ProductPagination(PageNumberPagination):
    page_size = 12