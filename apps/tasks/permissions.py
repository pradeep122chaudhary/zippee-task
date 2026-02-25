from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):

    message = "You do not have permission to access this task."

    def has_object_permission(self, request, view, obj) -> bool:
        if (
            request.user
            and request.user.is_authenticated
            and request.user.has_global_data_access()
        ):
            return True
        return obj.user_id == request.user.id
