from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

class IsTrainer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_trainer)

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        author_attr = getattr(obj, 'author', None)
        if author_attr is None:
             author_attr = getattr(obj, 'user', None)

        return author_attr == request.user

class IsProfileOwnerOrAdmin(permissions.BasePermission):
     def has_object_permission(self, request, view, obj):
         return obj.user == request.user or request.user.is_staff