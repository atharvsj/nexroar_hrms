"""
Django REST Framework APIView for Role Creation
Converted from PHP CodeIgniter HRMS System
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import connection, transaction
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime


class UserRolePermissionsAPIView(APIView):
    """
    API View to get user's role-based permissions for sidebar access
    GET /api/roles/user-permissions/
    GET /api/roles/user-permissions/<user_id>/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None, *args, **kwargs):
        """
        Get role-based permissions for a user
        
        Returns sidebar access permissions based on user's assigned role
        
        Response:
        {
            "user_id": 123,
            "role_id": 5,
            "role_name": "Manager",
            "role_access": "2",
            "role_access_label": "Custom Menu",
            "permissions": [
                "attendance",
                "hr_projects",
                "project1",
                "project2",
                "task1"
            ],
            "has_all_access": false
        }
        """
        
        try:
            # Get user_id from URL parameter or JWT token
            if not user_id:
                user_id = request.user.id
            
            if not user_id:
                return Response({
                    'error': 'User ID is required or session not found'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get user's role and permissions
            user_role_data = self._get_user_role_permissions(user_id)
            
            if not user_role_data:
                return Response({
                    'error': 'User or role information not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response(user_role_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def _get_user_role_permissions(self, user_id):
        """
        Get user's role and permissions from database
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict: User role and permissions data
        """
        try:
            with connection.cursor() as cursor:
                # Get user info with role details
                cursor.execute("""
                    SELECT 
                        u.user_id,
                        u.user_role_id,
                        u.user_type,
                        r.role_id,
                        r.role_name,
                        r.role_access,
                        r.role_resources
                    FROM ci_erp_users u
                    LEFT JOIN ci_staff_roles r ON u.user_role_id = r.role_id
                    WHERE u.id = %s
                    LIMIT 1
                """, [user_id])
                
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                user_data = {
                    'user_id': row[0],
                    'user_role_id': row[1],
                    'user_type': row[2],
                    'role_id': row[3],
                    'role_name': row[4],
                    'role_access': row[5],
                    'role_resources': row[6]
                }
                
                # If user is company type, they have all access
                if user_data['user_type'] == 'company':
                    return {
                        'user_id': user_data['user_id'],
                        'user_type': 'company',
                        'role_id': None,
                        'role_name': 'Company Admin',
                        'role_access': '1',
                        'role_access_label': 'All Menu Access',
                        'permissions': ['all'],
                        'has_all_access': True
                    }
                
                # Parse role_resources into array
                if user_data['role_resources']:
                    permissions = user_data['role_resources'].split(',')
                    # Remove empty strings
                    permissions = [p.strip() for p in permissions if p.strip()]
                else:
                    permissions = []
                
                # Determine if user has all access
                has_all_access = user_data['role_access'] == '1'
                
                return {
                    'user_id': user_data['user_id'],
                    'user_type': user_data['user_type'],
                    'role_id': user_data['role_id'],
                    'role_name': user_data['role_name'] if user_data['role_name'] else 'No Role Assigned',
                    'role_access': user_data['role_access'] if user_data['role_access'] else '0',
                    'role_access_label': 'All Menu Access' if has_all_access else 'Custom Menu Access',
                    'permissions': permissions,
                    'has_all_access': has_all_access
                }
                
        except Exception as e:
            print(f"Error fetching user role permissions: {str(e)}")
            return None


class CheckPermissionAPIView(APIView):
    """
    API View to check if user has specific permission
    POST /api/roles/check-permission/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Check if user has a specific permission
        
        Payload:
        {
            "user_id": 123,  # Optional, will use JWT token if not provided
            "permission": "hr_projects"
        }
        
        Response:
        {
            "has_permission": true,
            "permission": "hr_projects",
            "user_id": 123
        }
        """
        
        try:
            # Get user_id and permission
            user_id = request.data.get('user_id', None)
            permission = request.data.get('permission', '').strip()
            
            if not user_id:
                user_id = request.user.id
            
            if not user_id:
                return Response({
                    'error': 'User ID is required'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if not permission:
                return Response({
                    'error': 'Permission name is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user permissions
            user_role_data = self._get_user_role_permissions(user_id)
            
            if not user_role_data:
                return Response({
                    'has_permission': False,
                    'permission': permission,
                    'user_id': user_id,
                    'error': 'User role not found'
                }, status=status.HTTP_200_OK)
            
            # Check if user has the permission
            has_permission = (
                user_role_data['has_all_access'] or 
                permission in user_role_data['permissions']
            )
            
            return Response({
                'has_permission': has_permission,
                'permission': permission,
                'user_id': user_id,
                'role_name': user_role_data.get('role_name')
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def _get_user_role_permissions(self, user_id):
        """Get user role permissions - same logic as UserRolePermissionsAPIView"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        u.user_id,
                        u.user_type,
                        r.role_access,
                        r.role_name,
                        r.role_resources
                    FROM ci_erp_users u
                    LEFT JOIN ci_staff_roles r ON u.user_role_id = r.role_id
                    WHERE u.id = %s
                    LIMIT 1
                """, [user_id])
                
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                user_type = row[1]
                role_access = row[2]
                role_name = row[3]
                role_resources = row[4]
                
                # Company users have all access
                if user_type == 'company':
                    return {
                        'has_all_access': True,
                        'permissions': ['all'],
                        'role_name': 'Company Admin'
                    }
                
                # Parse permissions
                permissions = []
                if role_resources:
                    permissions = [p.strip() for p in role_resources.split(',') if p.strip()]
                
                has_all_access = role_access == '1'
                
                return {
                    'has_all_access': has_all_access,
                    'permissions': permissions,
                    'role_name': role_name
                }
                
        except Exception as e:
            print(f"Error in _get_user_role_permissions: {str(e)}")
            return None


class CheckMultiplePermissionsAPIView(APIView):
    """
    API View to check multiple permissions at once
    POST /api/roles/check-multiple-permissions/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Check if user has multiple permissions
        
        Payload:
        {
            "user_id": 123,  # Optional
            "permissions": ["hr_projects", "task1", "attendance", "leave2"]
        }
        
        Response:
        {
            "user_id": 123,
            "role_name": "Manager",
            "has_all_access": false,
            "results": {
                "hr_projects": true,
                "task1": true,
                "attendance": false,
                "leave2": true
            },
            "granted": ["hr_projects", "task1", "leave2"],
            "denied": ["attendance"]
        }
        """
        
        try:
            user_id = request.data.get('user_id', None)
            permissions = request.data.get('permissions', [])
            
            if not user_id:
                user_id = request.user.id
            
            if not user_id:
                return Response({
                    'error': 'User ID is required'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if not permissions or not isinstance(permissions, list):
                return Response({
                    'error': 'Permissions array is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user permissions
            user_role_data = self._get_user_role_permissions(user_id)
            
            if not user_role_data:
                return Response({
                    'error': 'User role not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check each permission
            results = {}
            granted = []
            denied = []
            
            for permission in permissions:
                has_perm = (
                    user_role_data['has_all_access'] or
                    permission in user_role_data['permissions']
                )
                results[permission] = has_perm
                
                if has_perm:
                    granted.append(permission)
                else:
                    denied.append(permission)
            
            return Response({
                'user_id': user_id,
                'role_name': user_role_data.get('role_name'),
                'has_all_access': user_role_data['has_all_access'],
                'results': results,
                'granted': granted,
                'denied': denied
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def _get_user_role_permissions(self, user_id):
        """Get user role permissions"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        u.user_type,
                        r.role_access,
                        r.role_name,
                        r.role_resources
                    FROM ci_erp_users u
                    LEFT JOIN ci_staff_roles r ON u.user_role_id = r.role_id
                    WHERE u.id = %s
                    LIMIT 1
                """, [user_id])
                
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                user_type = row[0]
                role_access = row[1]
                role_name = row[2]
                role_resources = row[3]
                
                if user_type == 'company':
                    return {
                        'has_all_access': True,
                        'permissions': ['all'],
                        'role_name': 'Company Admin'
                    }
                
                permissions = []
                if role_resources:
                    permissions = [p.strip() for p in role_resources.split(',') if p.strip()]
                
                return {
                    'has_all_access': role_access == '1',
                    'permissions': permissions,
                    'role_name': role_name
                }
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return None


class RoleCreateAPIView(APIView):
    """
    API View to create a new role with permissions
    POST /api/roles/create/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """
        Create a new role with the provided data
        
        Payload:
        {
            "role_name": "Manager",
            "role_access": "2",  # 1=All Menu, 2=Custom Menu
            "role_resources": ["0", "attendance", "hr_projects", "project1", ...]
        }
        """
        
        # Initialize response structure
        response_data = {
            'result': '',
            'error': '',
            'csrf_hash': ''
        }
        
        try:
            # Get request type validation
            request_type = request.data.get('type', None)
            
            if request_type != 'add_record':
                response_data['error'] = 'Invalid request type'
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Get POST data
            role_name = request.data.get('role_name', '').strip()
            role_access = request.data.get('role_access', '').strip()
            role_resources = request.data.get('role_resources', [])
            
            # Validation
            validation_errors = self._validate_role_data(role_name, role_access)
            
            if validation_errors:
                response_data['error'] = validation_errors
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user from JWT token
            user_id = request.user.id
            
            if not user_id:
                response_data['error'] = 'User session not found. Please login.'
                return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get user info to determine company_id
            user_info = self._get_user_info(user_id)
            
            if not user_info:
                response_data['error'] = 'User information not found'
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            
            # Determine company_id based on user type
            if user_info['user_type'] == 'staff':
                company_id = user_info['company_id']
            else:
                company_id = user_id
            
            # Convert role_resources array to comma-separated string
            if isinstance(role_resources, list):
                role_resources_str = ','.join(str(item) for item in role_resources)
            else:
                role_resources_str = str(role_resources)
            
            # Prepare data for insertion
            role_data = {
                'role_name': role_name,
                'company_id': company_id,
                'role_access': role_access,
                'role_resources': role_resources_str,
                'created_at': datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            }
            
            # Insert role into database using cursor
            role_id = self._insert_role(role_data)
            
            if role_id:
                response_data['result'] = 'Role has been successfully added.'
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                response_data['error'] = 'Failed to create role. Please try again.'
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except KeyError as e:
            response_data['error'] = f'Missing required field: {str(e)}'
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
        except ValueError as e:
            response_data['error'] = f'Invalid value provided: {str(e)}'
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            response_data['error'] = f'An error occurred: {str(e)}'
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def _validate_role_data(self, role_name, role_access):
        """
        Validate role creation data
        
        Args:
            role_name (str): Name of the role
            role_access (str): Access level (1 or 2)
            
        Returns:
            str: Error message if validation fails, empty string otherwise
        """
        errors = []
        
        # Validate role_name
        if not role_name:
            errors.append('Role name is required.')
        elif len(role_name) < 3:
            errors.append('Role name must be at least 3 characters long.')
        elif len(role_name) > 100:
            errors.append('Role name must not exceed 100 characters.')
        
        # Validate role_access
        if not role_access:
            errors.append('Role access level is required.')
        elif role_access not in ['1', '2']:
            errors.append('Invalid role access level. Must be 1 (All Menu) or 2 (Custom Menu).')
        
        return ' '.join(errors) if errors else ''
    
    
    def _get_user_info(self, user_id):
        """
        Get user information from database using cursor
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict: User information or None
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, user_type, company_id 
                    FROM ci_erp_users 
                    WHERE id = %s
                    LIMIT 1
                """, [user_id])
                
                row = cursor.fetchone()
                
                if row:
                    return {
                        'user_id': row[0],
                        'user_type': row[1],
                        'company_id': row[2]
                    }
                return None
                
        except Exception as e:
            print(f"Error fetching user info: {str(e)}")
            return None
    
    
    @transaction.atomic
    def _insert_role(self, role_data):
        """
        Insert new role into database using cursor
        
        Args:
            role_data (dict): Role data to insert
            
        Returns:
            int: Inserted role ID or None
        """
        try:
            with connection.cursor() as cursor:
                # Insert query
                sql = """
                    INSERT INTO ci_staff_roles 
                    (role_name, company_id, role_access, role_resources, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """
                
                cursor.execute(sql, [
                    role_data['role_name'],
                    role_data['company_id'],
                    role_data['role_access'],
                    role_data['role_resources'],
                    role_data['created_at']
                ])
                
                # Get last inserted ID
                role_id = cursor.lastrowid
                
                return role_id
                
        except Exception as e:
            print(f"Error inserting role: {str(e)}")
            raise e


class RoleUpdateAPIView(APIView):
    """
    API View to update an existing role
    POST /api/roles/update/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """
        Update an existing role
        
        Payload:
        {
            "role_id": 123,
            "role_name": "Senior Manager",
            "role_access": "2",
            "role_resources": ["0", "attendance", "hr_projects", ...]
        }
        """
        
        response_data = {
            'result': '',
            'error': '',
            'csrf_hash': ''
        }
        
        try:
            # Get request type validation
            request_type = request.data.get('type', None)
            
            if request_type != 'edit_record':
                response_data['error'] = 'Invalid request type'
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Get POST data
            role_id = request.data.get('role_id', None)
            role_name = request.data.get('role_name', '').strip()
            role_access = request.data.get('role_access', '').strip()
            role_resources = request.data.get('role_resources', [])
            
            # Validate role_id
            if not role_id:
                response_data['error'] = 'Role ID is required'
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Validation
            validation_errors = self._validate_role_data(role_name, role_access)
            
            if validation_errors:
                response_data['error'] = validation_errors
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Convert role_resources array to comma-separated string
            if isinstance(role_resources, list):
                role_resources_str = ','.join(str(item) for item in role_resources)
            else:
                role_resources_str = str(role_resources)
            
            # Update role in database
            updated = self._update_role(role_id, role_name, role_access, role_resources_str)
            
            if updated:
                response_data['result'] = 'Role has been successfully updated.'
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data['error'] = 'Failed to update role. Please try again.'
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            response_data['error'] = f'An error occurred: {str(e)}'
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def _validate_role_data(self, role_name, role_access):
        """Validate role data - same as RoleCreateAPIView"""
        errors = []
        
        if not role_name:
            errors.append('Role name is required.')
        elif len(role_name) < 3:
            errors.append('Role name must be at least 3 characters long.')
        
        if not role_access:
            errors.append('Role access level is required.')
        elif role_access not in ['1', '2']:
            errors.append('Invalid role access level.')
        
        return ' '.join(errors) if errors else ''
    
    
    @transaction.atomic
    def _update_role(self, role_id, role_name, role_access, role_resources):
        """
        Update role in database using cursor
        
        Args:
            role_id (int): Role ID to update
            role_name (str): New role name
            role_access (str): New access level
            role_resources (str): Comma-separated permissions
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with connection.cursor() as cursor:
                sql = """
                    UPDATE ci_staff_roles 
                    SET role_name = %s,
                        role_access = %s,
                        role_resources = %s
                    WHERE role_id = %s
                """
                
                cursor.execute(sql, [
                    role_name,
                    role_access,
                    role_resources,
                    role_id
                ])
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error updating role: {str(e)}")
            raise e


class RoleDeleteAPIView(APIView):
    """
    API View to delete a role
    POST /api/roles/delete/<role_id>/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, role_id=None, *args, **kwargs):
        """
        Delete a role by ID
        """
        
        response_data = {
            'result': '',
            'error': '',
            'csrf_hash': ''
        }
        
        try:
            if not role_id:
                response_data['error'] = 'Role ID is required'
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if role exists
            role_exists = self._check_role_exists(role_id)
            
            if not role_exists:
                response_data['error'] = 'Role not found'
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            
            # Check if role is assigned to any users
            users_count = self._count_users_with_role(role_id)
            
            if users_count > 0:
                response_data['error'] = f'Cannot delete role. {users_count} user(s) are assigned to this role.'
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Delete role
            deleted = self._delete_role(role_id)
            
            if deleted:
                response_data['result'] = 'Role has been successfully deleted.'
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data['error'] = 'Failed to delete role.'
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            response_data['error'] = f'An error occurred: {str(e)}'
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def _check_role_exists(self, role_id):
        """Check if role exists"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM ci_staff_roles 
                    WHERE role_id = %s
                """, [role_id])
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            print(f"Error checking role exists: {str(e)}")
            return False
    
    
    def _count_users_with_role(self, role_id):
        """Count users assigned to this role"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM ci_erp_users 
                    WHERE user_role_id = %s
                """, [role_id])
                
                count = cursor.fetchone()[0]
                return count
                
        except Exception as e:
            print(f"Error counting users with role: {str(e)}")
            return 0
    
    
    @transaction.atomic
    def _delete_role(self, role_id):
        """Delete role from database"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM ci_staff_roles 
                    WHERE role_id = %s
                """, [role_id])
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting role: {str(e)}")
            raise e


class RoleListAPIView(APIView):
    """
    API View to list all roles
    GET /api/roles/list/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Get list of all roles for the company
        """
        
        try:
            # Get user from JWT token
            user_id = request.user.id
            
            if not user_id:
                return Response({
                    'error': 'User session not found'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get user info to determine company_id
            user_info = self._get_user_info(user_id)
            
            if not user_info:
                return Response({
                    'error': 'User information not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Determine company_id
            if user_info['user_type'] == 'staff':
                company_id = user_info['company_id']
            else:
                company_id = user_id
            
            # Get roles for company
            roles = self._get_roles_by_company(company_id)
            
            return Response({
                'data': roles
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def _get_user_info(self, user_id):
        """Get user information"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, user_type, company_id 
                    FROM ci_erp_users 
                    WHERE id = %s
                    LIMIT 1
                """, [user_id])
                
                row = cursor.fetchone()
                
                if row:
                    return {
                        'user_id': row[0],
                        'user_type': row[1],
                        'company_id': row[2]
                    }
                return None
                
        except Exception as e:
            print(f"Error fetching user info: {str(e)}")
            return None
    
    
    def _get_roles_by_company(self, company_id):
        """Get all roles for a company"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        role_id,
                        role_name,
                        role_access,
                        role_resources,
                        created_at
                    FROM ci_staff_roles
                    WHERE company_id = %s
                    ORDER BY role_id ASC
                """, [company_id])
                
                columns = [col[0] for col in cursor.description]
                roles = []
                
                for row in cursor.fetchall():
                    role_dict = dict(zip(columns, row))
                    
                    # Convert role_resources string to array
                    if role_dict.get('role_resources'):
                        role_dict['role_resources_array'] = role_dict['role_resources'].split(',')
                    else:
                        role_dict['role_resources_array'] = []
                    
                    # Add role access label
                    role_dict['role_access_label'] = 'All Menu' if role_dict['role_access'] == '1' else 'Custom Menu'
                    
                    roles.append(role_dict)
                
                return roles
                
        except Exception as e:
            print(f"Error fetching roles: {str(e)}")
            return []


# URL Configuration (urls.py)
"""
from django.urls import path
from .role_views_django import (
    UserRolePermissionsAPIView,
    CheckPermissionAPIView,
    CheckMultiplePermissionsAPIView,
    RoleCreateAPIView, 
    RoleUpdateAPIView, 
    RoleDeleteAPIView,
    RoleListAPIView
)

urlpatterns = [
    # Permission Check APIs (GET methods)
    path('api/roles/user-permissions/', UserRolePermissionsAPIView.as_view(), name='user-permissions'),
    path('api/roles/user-permissions/<int:user_id>/', UserRolePermissionsAPIView.as_view(), name='user-permissions-by-id'),
    path('api/roles/check-permission/', CheckPermissionAPIView.as_view(), name='check-permission'),
    path('api/roles/check-multiple-permissions/', CheckMultiplePermissionsAPIView.as_view(), name='check-multiple-permissions'),
    
    # Role Management APIs
    path('api/roles/create/', RoleCreateAPIView.as_view(), name='role-create'),
    path('api/roles/update/', RoleUpdateAPIView.as_view(), name='role-update'),
    path('api/roles/delete/<int:role_id>/', RoleDeleteAPIView.as_view(), name='role-delete'),
    path('api/roles/list/', RoleListAPIView.as_view(), name='role-list'),
]
"""

# Example API Usage
"""
# ==========================================
# GET USER ROLE-BASED PERMISSIONS (SIDEBAR ACCESS)
# ==========================================

# Get current user's permissions (from session)
GET /api/roles/user-permissions/

Response:
{
    "user_id": 123,
    "user_type": "staff",
    "role_id": 5,
    "role_name": "Manager",
    "role_access": "2",
    "role_access_label": "Custom Menu Access",
    "permissions": [
        "attendance",
        "hr_projects",
        "project1",
        "project2",
        "project3",
        "task1",
        "task2",
        "pay1",
        "leave2"
    ],
    "has_all_access": false
}

# Get specific user's permissions
GET /api/roles/user-permissions/123/

Response:
{
    "user_id": 123,
    "user_type": "staff",
    "role_id": 5,
    "role_name": "Manager",
    "role_access": "2",
    "role_access_label": "Custom Menu Access",
    "permissions": [
        "attendance",
        "hr_projects",
        "project1"
    ],
    "has_all_access": false
}

# Company admin response (has all access)
GET /api/roles/user-permissions/1/

Response:
{
    "user_id": 1,
    "user_type": "company",
    "role_id": null,
    "role_name": "Company Admin",
    "role_access": "1",
    "role_access_label": "All Menu Access",
    "permissions": ["all"],
    "has_all_access": true
}


# ==========================================
# CHECK SINGLE PERMISSION
# ==========================================

POST /api/roles/check-permission/
Content-Type: application/json

{
    "user_id": 123,
    "permission": "hr_projects"
}

Response:
{
    "has_permission": true,
    "permission": "hr_projects",
    "user_id": 123,
    "role_name": "Manager"
}


# ==========================================
# CHECK MULTIPLE PERMISSIONS AT ONCE
# ==========================================

POST /api/roles/check-multiple-permissions/
Content-Type: application/json

{
    "user_id": 123,
    "permissions": ["hr_projects", "task1", "attendance", "leave2", "hr_staff"]
}

Response:
{
    "user_id": 123,
    "role_name": "Manager",
    "has_all_access": false,
    "results": {
        "hr_projects": true,
        "task1": true,
        "attendance": false,
        "leave2": true,
        "hr_staff": false
    },
    "granted": ["hr_projects", "task1", "leave2"],
    "denied": ["attendance", "hr_staff"]
}


# ==========================================
# ROLE MANAGEMENT APIs
# ==========================================

# CREATE ROLE
POST /api/roles/create/
Content-Type: application/json

{
    "type": "add_record",
    "role_name": "Manager",
    "role_access": "2",
    "role_resources": [
        "0",
        "attendance",
        "hr_projects",
        "project1",
        "project2",
        "project3",
        "task1",
        "pay1",
        "leave2"
    ]
}

Response:
{
    "result": "Role has been successfully added.",
    "error": "",
    "csrf_hash": ""
}


# UPDATE ROLE
POST /api/roles/update/
Content-Type: application/json

{
    "type": "edit_record",
    "role_id": 5,
    "role_name": "Senior Manager",
    "role_access": "1",
    "role_resources": [
        "0",
        "attendance",
        "hr_projects",
        "hr_staff"
    ]
}


# DELETE ROLE
POST /api/roles/delete/5/

Response:
{
    "result": "Role has been successfully deleted.",
    "error": "",
    "csrf_hash": ""
}


# LIST ROLES
GET /api/roles/list/

Response:
{
    "data": [
        {
            "role_id": 1,
            "role_name": "Manager",
            "role_access": "2",
            "role_resources": "0,attendance,hr_projects,project1",
            "role_resources_array": ["0", "attendance", "hr_projects", "project1"],
            "role_access_label": "Custom Menu",
            "created_at": "21-01-2026 10:30:45"
        }
    ]
}


# ==========================================
# USAGE IN FRONTEND/MIDDLEWARE
# ==========================================

# Example: Check if user can access Projects module
GET /api/roles/user-permissions/

# Then in frontend:
if "hr_projects" in response.permissions or response.has_all_access:
    # Show Projects menu in sidebar
    pass

# Example: Check multiple permissions before rendering page
POST /api/roles/check-multiple-permissions/
{
    "permissions": ["hr_projects", "project1", "project2"]
}

# If all granted, show full page, else show limited view
"""
