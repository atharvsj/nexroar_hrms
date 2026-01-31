"""
Django REST Framework APIView for Training Management
Converted from PHP CodeIgniter HRMS System
Handles Training Sessions with Trainer and Employee Assignment
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


class TrainingCreateAPIView(APIView):
    """
    API View to create a new training session
    POST /api/training/create/
    
    Features:
    - Assign trainer to training
    - Assign multiple employees to training
    - Set training type/skill, dates, cost
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """
        Create a new training session
        
        Payload:
        {
            "type": "add_record",
            "trainer": 5,
            "training_type": 3,
            "training_cost": "5000",
            "employee_id": [12, 15, 18],  # Multiple employees
            "start_date": "2026-01-25",
            "end_date": "2026-01-30",
            "description": "Python training session"
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
            trainer = request.data.get('trainer', '').strip() if isinstance(request.data.get('trainer'), str) else request.data.get('trainer')
            training_type = request.data.get('training_type', '').strip() if isinstance(request.data.get('training_type'), str) else request.data.get('training_type')
            training_cost = request.data.get('training_cost', '0').strip()
            start_date = request.data.get('start_date', '').strip()
            end_date = request.data.get('end_date', '').strip()
            description = request.data.get('description', '').strip()
            employee_ids = request.data.get('employee_id', [])
            
            # Validation
            validation_errors = self._validate_training_data(
                trainer, training_type, start_date, end_date
            )
            
            if validation_errors:
                response_data['error'] = validation_errors
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user from JWT token
            user_id = request.user.id
            
            if not user_id:
                response_data['error'] = 'User session not found. Please login.'
                return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get user info to determine company_id and permissions
            user_info = self._get_user_info(user_id)
            
            if not user_info:
                response_data['error'] = 'User information not found'
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            
            # Determine company_id and employee assignment based on user type
            if user_info['user_type'] == 'staff':
                # Staff users can only assign themselves
                company_id = user_info['company_id']
                staff_id = str(user_id)  # Self-assign
            else:
                # Company users can assign multiple employees
                company_id = user_id
                
                # Convert employee_ids array to comma-separated string
                if isinstance(employee_ids, list):
                    # Filter out empty values and convert to string
                    employee_ids = [str(emp_id) for emp_id in employee_ids if emp_id]
                    staff_id = ','.join(employee_ids) if employee_ids else '0'
                else:
                    staff_id = str(employee_ids) if employee_ids else '0'
            
            # Prepare data for insertion
            training_data = {
                'company_id': company_id,
                'employee_id': staff_id,  # Comma-separated employee IDs
                'training_type_id': training_type,
                'trainer_id': trainer,
                'start_date': start_date,
                'finish_date': end_date,
                'training_cost': training_cost if training_cost else '0',
                'description': description,
                'training_status': 1,  # Active
                'performance': 0,
                'remarks': '',
                'created_at': datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            }
            
            # Insert training into database
            training_id = self._insert_training(training_data)
            
            if training_id:
                response_data['result'] = 'Training session has been successfully added.'
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                response_data['error'] = 'Failed to create training session. Please try again.'
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
    
    
    def _validate_training_data(self, trainer, training_type, start_date, end_date):
        """
        Validate training creation data
        
        Args:
            trainer: Trainer ID
            training_type: Training type/skill ID
            start_date: Training start date
            end_date: Training end date
            
        Returns:
            str: Error message if validation fails, empty string otherwise
        """
        errors = []
        
        # Validate trainer
        if not trainer:
            errors.append('Trainer is required.')
        
        # Validate training_type
        if not training_type:
            errors.append('Training type/skill is required.')
        
        # Validate start_date
        if not start_date:
            errors.append('Start date is required.')
        else:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                errors.append('Invalid start date format. Use YYYY-MM-DD.')
        
        # Validate end_date
        if not end_date:
            errors.append('End date is required.')
        else:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                if start_date:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    if end_dt < start_dt:
                        errors.append('End date must be after start date.')
            except ValueError:
                errors.append('Invalid end date format. Use YYYY-MM-DD.')
        
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
    def _insert_training(self, training_data):
        """
        Insert new training into database using cursor
        
        Args:
            training_data (dict): Training data to insert
            
        Returns:
            int: Inserted training ID or None
        """
        try:
            with connection.cursor() as cursor:
                # Insert query
                sql = """
                    INSERT INTO ci_erp_training 
                    (company_id, employee_id, training_type_id, trainer_id, 
                     start_date, finish_date, training_cost, description, 
                     training_status, performance, remarks, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(sql, [
                    training_data['company_id'],
                    training_data['employee_id'],
                    training_data['training_type_id'],
                    training_data['trainer_id'],
                    training_data['start_date'],
                    training_data['finish_date'],
                    training_data['training_cost'],
                    training_data['description'],
                    training_data['training_status'],
                    training_data['performance'],
                    training_data['remarks'],
                    training_data['created_at']
                ])
                
                # Get last inserted ID
                training_id = cursor.lastrowid
                
                return training_id
                
        except Exception as e:
            print(f"Error inserting training: {str(e)}")
            raise e


class TrainingUpdateAPIView(APIView):
    """
    API View to update an existing training session
    POST /api/training/update/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """
        Update an existing training session
        
        Payload:
        {
            "type": "edit_record",
            "training_id": 123,
            "trainer": 5,
            "training_type": 3,
            "training_cost": "6000",
            "employee_id": [12, 15, 18],
            "start_date": "2026-01-25",
            "end_date": "2026-01-30",
            "description": "Updated Python training"
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
            training_id = request.data.get('training_id', None)
            trainer = request.data.get('trainer', '').strip() if isinstance(request.data.get('trainer'), str) else request.data.get('trainer')
            training_type = request.data.get('training_type', '').strip() if isinstance(request.data.get('training_type'), str) else request.data.get('training_type')
            training_cost = request.data.get('training_cost', '0').strip()
            start_date = request.data.get('start_date', '').strip()
            end_date = request.data.get('end_date', '').strip()
            description = request.data.get('description', '').strip()
            employee_ids = request.data.get('employee_id', [])
            
            # Validate training_id
            if not training_id:
                response_data['error'] = 'Training ID is required'
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Validation
            validation_errors = self._validate_training_data(
                trainer, training_type, start_date, end_date
            )
            
            if validation_errors:
                response_data['error'] = validation_errors
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user from JWT token
            user_id = request.user.id
            user_info = self._get_user_info(user_id)
            
            # Convert employee_ids to comma-separated string
            if user_info and user_info['user_type'] == 'company':
                if isinstance(employee_ids, list):
                    employee_ids = [str(emp_id) for emp_id in employee_ids if emp_id]
                    staff_id = ','.join(employee_ids) if employee_ids else '0'
                else:
                    staff_id = str(employee_ids) if employee_ids else '0'
            else:
                staff_id = str(user_id)
            
            # Update training in database
            updated = self._update_training(
                training_id, trainer, training_type, training_cost,
                staff_id, start_date, end_date, description
            )
            
            if updated:
                response_data['result'] = 'Training session has been successfully updated.'
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data['error'] = 'Failed to update training session.'
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            response_data['error'] = f'An error occurred: {str(e)}'
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def _validate_training_data(self, trainer, training_type, start_date, end_date):
        """Validate training data - same as TrainingCreateAPIView"""
        errors = []
        
        if not trainer:
            errors.append('Trainer is required.')
        if not training_type:
            errors.append('Training type is required.')
        if not start_date:
            errors.append('Start date is required.')
        if not end_date:
            errors.append('End date is required.')
        
        return ' '.join(errors) if errors else ''
    
    
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
    
    
    @transaction.atomic
    def _update_training(self, training_id, trainer, training_type, training_cost,employee_id, start_date, end_date, description):
        """
        Update training in database using cursor
        
        Args:
            training_id (int): Training ID to update
            trainer: Trainer ID
            training_type: Training type ID
            training_cost: Cost of training
            employee_id: Comma-separated employee IDs
            start_date: Start date
            end_date: End date
            description: Training description
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with connection.cursor() as cursor:
                sql = """
                    UPDATE ci_erp_training 
                    SET trainer_id = %s,
                        training_type_id = %s,
                        training_cost = %s,
                        employee_id = %s,
                        start_date = %s,
                        finish_date = %s,
                        description = %s
                    WHERE training_id = %s
                """
                
                cursor.execute(sql, [
                    trainer,
                    training_type,
                    training_cost,
                    employee_id,
                    start_date,
                    end_date,
                    description,
                    training_id
                ])
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error updating training: {str(e)}")
            raise e


class TrainingDeleteAPIView(APIView):
    """
    API View to delete a training session
    POST /api/training/delete/<training_id>/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, training_id=None, *args, **kwargs):
        """
        Delete a training session by ID
        """
        
        response_data = {
            'result': '',
            'error': '',
            'csrf_hash': ''
        }
        
        try:
            if not training_id:
                response_data['error'] = 'Training ID is required'
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if training exists
            training_exists = self._check_training_exists(training_id)
            
            if not training_exists:
                response_data['error'] = 'Training session not found'
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            
            # Delete training
            deleted = self._delete_training(training_id)
            
            if deleted:
                response_data['result'] = 'Training session has been successfully deleted.'
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data['error'] = 'Failed to delete training session.'
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            response_data['error'] = f'An error occurred: {str(e)}'
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def _check_training_exists(self, training_id):
        """Check if training exists"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM ci_erp_training 
                    WHERE training_id = %s
                """, [training_id])
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            print(f"Error checking training exists: {str(e)}")
            return False
    
    
    @transaction.atomic
    def _delete_training(self, training_id):
        """Delete training from database"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM ci_erp_training 
                    WHERE training_id = %s
                """, [training_id])
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting training: {str(e)}")
            raise e


class TrainingListAPIView(APIView):
    """
    API View to list all training sessions
    GET /api/training/list/
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Get list of all training sessions for the company
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
            
            # Get trainings for company
            trainings = self._get_trainings_by_company(company_id)
            
            return Response({
                'data': trainings
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
    
    
    def _get_trainings_by_company(self, company_id):
        """Get all training sessions for a company"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        t.training_id,
                        t.company_id,
                        t.employee_id,
                        t.training_type_id,
                        t.trainer_id,
                        t.start_date,
                        t.finish_date,
                        t.training_cost,
                        t.description,
                        t.training_status,
                        t.performance,
                        t.remarks,
                        t.created_at,
                        tr.first_name AS trainer_first_name,
                        tr.last_name AS trainer_last_name,
                        c.category_name AS training_type_name
                    FROM ci_erp_training t
                    LEFT JOIN ci_erp_trainers tr ON t.trainer_id = tr.trainer_id
                    LEFT JOIN ci_erp_constants c ON t.training_type_id = c.constants_id
                    WHERE t.company_id = %s
                    ORDER BY t.training_id DESC
                """, [company_id])
                
                columns = [col[0] for col in cursor.description]
                trainings = []
                
                for row in cursor.fetchall():
                    training_dict = dict(zip(columns, row))
                    
                    # Convert employee_id string to array
                    if training_dict.get('employee_id'):
                        training_dict['employee_id_array'] = training_dict['employee_id'].split(',')
                    else:
                        training_dict['employee_id_array'] = []
                    
                    # Add trainer full name
                    if training_dict.get('trainer_first_name'):
                        training_dict['trainer_name'] = f"{training_dict['trainer_first_name']} {training_dict['trainer_last_name']}"
                    else:
                        training_dict['trainer_name'] = 'N/A'
                    
                    # Add status label
                    training_dict['status_label'] = self._get_status_label(training_dict['training_status'])
                    
                    trainings.append(training_dict)
                
                return trainings
                
        except Exception as e:
            print(f"Error fetching trainings: {str(e)}")
            return []
    
    
    def _get_status_label(self, status):
        """Get training status label"""
        status_map = {
            0: 'Pending',
            1: 'Active',
            2: 'Completed',
            3: 'Cancelled'
        }
        return status_map.get(status, 'Unknown')


class TrainingDetailsAPIView(APIView):
    """
    API View to get training session details with employees
    GET /api/training/details/<training_id>/
    """
    
    def get(self, request, training_id=None, *args, **kwargs):
        """
        Get detailed information about a training session including assigned employees
        """
        
        try:
            if not training_id:
                return Response({
                    'error': 'Training ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get training details
            training = self._get_training_details(training_id)
            
            if not training:
                return Response({
                    'error': 'Training session not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get assigned employees details
            employee_ids = training.get('employee_id', '').split(',')
            employees = self._get_employees_details(employee_ids)
            training['assigned_employees'] = employees
            
            return Response({
                'data': training
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def _get_training_details(self, training_id):
        """Get training details by ID"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        t.*,
                        tr.first_name AS trainer_first_name,
                        tr.last_name AS trainer_last_name,
                        tr.email AS trainer_email,
                        c.category_name AS training_type_name
                    FROM ci_erp_training t
                    LEFT JOIN ci_erp_trainers tr ON t.trainer_id = tr.trainer_id
                    LEFT JOIN ci_erp_constants c ON t.training_type_id = c.constants_id
                    WHERE t.training_id = %s
                    LIMIT 1
                """, [training_id])
                
                row = cursor.fetchone()
                
                if row:
                    columns = [col[0] for col in cursor.description]
                    training_dict = dict(zip(columns, row))
                    
                    # Add trainer full name
                    training_dict['trainer_name'] = f"{training_dict['trainer_first_name']} {training_dict['trainer_last_name']}"
                    
                    return training_dict
                
                return None
                
        except Exception as e:
            print(f"Error fetching training details: {str(e)}")
            return None
    
    
    def _get_employees_details(self, employee_ids):
        """Get details of assigned employees"""
        try:
            if not employee_ids or employee_ids == ['0']:
                return []
            
            with connection.cursor() as cursor:
                placeholders = ','.join(['%s'] * len(employee_ids))
                cursor.execute(f"""
                    SELECT 
                        user_id,
                        first_name,
                        last_name,
                        email,
                        employee_id AS emp_code
                    FROM ci_erp_users
                    WHERE user_id IN ({placeholders})
                """, employee_ids)
                
                columns = [col[0] for col in cursor.description]
                employees = []
                
                for row in cursor.fetchall():
                    emp_dict = dict(zip(columns, row))
                    emp_dict['full_name'] = f"{emp_dict['first_name']} {emp_dict['last_name']}"
                    employees.append(emp_dict)
                
                return employees
                
        except Exception as e:
            print(f"Error fetching employees: {str(e)}")
            return []


class TrainingUpdateStatusAPIView(APIView):
    """
    API View to update training status
    POST /api/training/update-status/
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """
        Update training status
        
        Payload:
        {
            "training_id": 123,
            "training_status": 2,  # 0=Pending, 1=Active, 2=Completed, 3=Cancelled
            "performance": 85,
            "remarks": "Excellent performance"
        }
        """
        
        response_data = {
            'result': '',
            'error': '',
            'csrf_hash': ''
        }
        
        try:
            training_id = request.data.get('training_id', None)
            training_status = request.data.get('training_status', None)
            performance = request.data.get('performance', 0)
            remarks = request.data.get('remarks', '').strip()
            
            if not training_id:
                response_data['error'] = 'Training ID is required'
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            if training_status is None:
                response_data['error'] = 'Training status is required'
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            # Update status
            updated = self._update_status(training_id, training_status, performance, remarks)
            
            if updated:
                response_data['result'] = 'Training status has been successfully updated.'
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data['error'] = 'Failed to update training status.'
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            response_data['error'] = f'An error occurred: {str(e)}'
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    @transaction.atomic
    def _update_status(self, training_id, training_status, performance, remarks):
        """Update training status in database"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ci_erp_training 
                    SET training_status = %s,
                        performance = %s,
                        remarks = %s
                    WHERE training_id = %s
                """, [training_status, performance, remarks, training_id])
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error updating training status: {str(e)}")
            raise e


# URL Configuration (urls.py)
"""
from django.urls import path
from .training_views_django import (
    TrainingCreateAPIView,
    TrainingUpdateAPIView,
    TrainingDeleteAPIView,
    TrainingListAPIView,
    TrainingDetailsAPIView,
    TrainingUpdateStatusAPIView
)

urlpatterns = [
    path('api/training/create/', TrainingCreateAPIView.as_view(), name='training-create'),
    path('api/training/update/', TrainingUpdateAPIView.as_view(), name='training-update'),
    path('api/training/delete/<int:training_id>/', TrainingDeleteAPIView.as_view(), name='training-delete'),
    path('api/training/list/', TrainingListAPIView.as_view(), name='training-list'),
    path('api/training/details/<int:training_id>/', TrainingDetailsAPIView.as_view(), name='training-details'),
    path('api/training/update-status/', TrainingUpdateStatusAPIView.as_view(), name='training-update-status'),
]
"""

# Example API Usage
"""
# CREATE TRAINING
POST /api/training/create/
Content-Type: application/json

{
    "type": "add_record",
    "trainer": 5,
    "training_type": 3,
    "training_cost": "5000",
    "employee_id": [12, 15, 18, 22],
    "start_date": "2026-01-25",
    "end_date": "2026-01-30",
    "description": "Advanced Python and Django Training Session"
}

Response:
{
    "result": "Training session has been successfully added.",
    "error": "",
    "csrf_hash": ""
}


# UPDATE TRAINING
POST /api/training/update/
Content-Type: application/json

{
    "type": "edit_record",
    "training_id": 123,
    "trainer": 5,
    "training_type": 3,
    "training_cost": "6000",
    "employee_id": [12, 15, 18],
    "start_date": "2026-01-26",
    "end_date": "2026-02-01",
    "description": "Updated training details"
}


# DELETE TRAINING
POST /api/training/delete/123/

Response:
{
    "result": "Training session has been successfully deleted.",
    "error": "",
    "csrf_hash": ""
}


# LIST TRAININGS
GET /api/training/list/

Response:
{
    "data": [
        {
            "training_id": 123,
            "company_id": 1,
            "employee_id": "12,15,18",
            "employee_id_array": ["12", "15", "18"],
            "trainer_id": 5,
            "trainer_name": "John Doe",
            "training_type_name": "Python Programming",
            "start_date": "2026-01-25",
            "finish_date": "2026-01-30",
            "training_cost": "5000",
            "training_status": 1,
            "status_label": "Active",
            "performance": 0,
            "created_at": "22-01-2026 10:30:45"
        }
    ]
}


# GET TRAINING DETAILS
GET /api/training/details/123/

Response:
{
    "data": {
        "training_id": 123,
        "trainer_name": "John Doe",
        "trainer_email": "john@example.com",
        "training_type_name": "Python Programming",
        "start_date": "2026-01-25",
        "finish_date": "2026-01-30",
        "training_cost": "5000",
        "description": "Advanced Python training",
        "assigned_employees": [
            {
                "user_id": 12,
                "full_name": "Alice Smith",
                "email": "alice@example.com",
                "emp_code": "EMP001"
            },
            {
                "user_id": 15,
                "full_name": "Bob Johnson",
                "email": "bob@example.com",
                "emp_code": "EMP002"
            }
        ]
    }
}


# UPDATE TRAINING STATUS
POST /api/training/update-status/
Content-Type: application/json

{
    "training_id": 123,
    "training_status": 2,
    "performance": 85,
    "remarks": "Excellent performance by all participants"
}

Response:
{
    "result": "Training status has been successfully updated.",
    "error": "",
    "csrf_hash": ""
}
"""
