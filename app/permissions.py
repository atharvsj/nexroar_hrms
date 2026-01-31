from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role_id.role_name == 'Admin'

class IsReportingManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role_id.role_name == 'Reporting Manager'

class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role_id.role_name == 'Employee'
