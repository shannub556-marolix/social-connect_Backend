from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access admin panel endpoints.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has admin permission.
        """
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Check if user has admin role
        return request.user.role == 'admin'
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to access the specific object.
        Admin users can access all objects.
        """
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Check if user has admin role
        return request.user.role == 'admin'
