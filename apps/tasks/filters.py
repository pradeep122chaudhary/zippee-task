import django_filters

from .models import Task


class TaskFilter(django_filters.FilterSet):

    completed = django_filters.BooleanFilter(field_name="completed")

    class Meta:
        model = Task
        fields = ("completed",)
