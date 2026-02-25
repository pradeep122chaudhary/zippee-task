from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class TaskPagination(PageNumberPagination):

    page_size = settings.REST_FRAMEWORK.get("PAGE_SIZE", 10)
