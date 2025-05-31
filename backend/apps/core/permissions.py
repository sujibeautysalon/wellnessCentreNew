from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin users can access any object
        if request.user.is_staff or request.user.role == 'admin':
            return True
            
        # For user objects, check if the user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        # If the object is a user, check if it's the same user
        return obj == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Allow access only to admin users.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or request.user.role == 'admin'))


class IsTherapist(permissions.BasePermission):
    """
    Allow access only to therapist users.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'therapist')


class IsCustomer(permissions.BasePermission):
    """
    Allow access only to customer users.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'customer')


class ReadOnly(permissions.BasePermission):
    """
    Allow read-only access to anyone.
    """
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
