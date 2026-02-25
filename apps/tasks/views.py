from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import filters, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import TaskFilter
from .models import Task
from .pagination import TaskPagination
from .permissions import IsOwnerOrAdmin
from .serializers import TaskSerializer


class TaskListCreateAPIView(APIView):

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TaskFilter
    search_fields = ["title"]

    def get_queryset(self, request):
        queryset = Task.objects.select_related("user").all()
        if not request.user.has_global_data_access():
            queryset = queryset.filter(user=request.user)
        return queryset

    def apply_filters(self, request, queryset):
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(request, queryset, self)
        return queryset

    @extend_schema(
        tags=["Tasks"],
        description="List tasks for the authenticated user (or all tasks for admin users).",
        parameters=[
            OpenApiParameter(
                name="completed",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Filter tasks by completion status.",
            ),
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Search tasks by title.",
            ),
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Page number for paginated results.",
            ),
            OpenApiParameter(
                name="user_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Filter tasks by owner user id (admin/super admin only).",
            ),
        ],
        responses={200: TaskSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)
        user_id = request.query_params.get("user_id")
        if user_id and request.user.has_global_data_access():
            queryset = queryset.filter(user_id=user_id)
        queryset = self.apply_filters(request, queryset)

        paginator = TaskPagination()
        paginated_tasks = paginator.paginate_queryset(queryset, request, view=self)
        serializer = TaskSerializer(paginated_tasks, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        tags=["Tasks"],
        description="Create a new task for the authenticated user.",
        request=TaskSerializer,
        examples=[
            OpenApiExample(
                "Create task payload",
                value={"title": "Finish report", "description": "Submit by EOD", "completed": False},
                request_only=True,
            )
        ],
        responses={201: TaskSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = TaskSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": "Task creation failed.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save(user=request.user)
        return Response(
            {"message": "Task created successfully.", "task": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class TaskDetailAPIView(APIView):

    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self, task_id: int) -> Task:
        try:
            return Task.objects.select_related("user").get(id=task_id)
        except Task.DoesNotExist as exc:
            raise NotFound(detail="Task not found.") from exc

    @extend_schema(
        tags=["Tasks"],
        description="Retrieve a single task. Accessible by owner or admin.",
        responses={200: TaskSerializer},
    )
    def get(self, request, task_id: int, *args, **kwargs):
        task = self.get_object(task_id)
        self.check_object_permissions(request, task)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Tasks"],
        description="Fully update a task. Accessible by owner or admin.",
        request=TaskSerializer,
        responses={200: TaskSerializer},
    )
    def put(self, request, task_id: int, *args, **kwargs):
        task = self.get_object(task_id)
        self.check_object_permissions(request, task)

        serializer = TaskSerializer(task, data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": "Task update failed.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(user=task.user)
        return Response(
            {"message": "Task updated successfully.", "task": serializer.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Tasks"],
        description="Delete a task. Accessible by owner or admin.",
        responses={204: None},
    )
    def delete(self, request, task_id: int, *args, **kwargs):
        task = self.get_object(task_id)
        self.check_object_permissions(request, task)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
