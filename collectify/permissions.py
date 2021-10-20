from rest_framework import permissions

from authentication.models import User


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object, if the object has an owner.
        if hasattr(obj, 'user'):
            if callable(obj.user):
                print("checking auth")
                return obj.user() == request.user
            print(obj.user)
            print(request.user)
            return obj.user == request.user

        if isinstance(obj, User):
            return obj == request.user

        print("checked auth")
        # For apis that are not owned by anyone
        return True
