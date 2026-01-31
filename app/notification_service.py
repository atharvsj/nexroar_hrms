"""
Notification Broadcasting Utility

This module provides helper functions to send real-time notifications
to connected WebSocket clients.

Usage:
    from app.notification_service import send_notification, send_global_notification
    
    # Send notification to a specific employee
    send_notification(employee_id='EMP001', notification_data={...})
    
    # Send notification to a specific user by user_id
    send_notification_to_user(user_id=123, notification_data={...})
    
    # Send global notification (birthdays, announcements)
    send_global_notification(notification_type='birthday', data={...})
"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging

logger = logging.getLogger(__name__)


def send_notification(employee_id: str, notification_data: dict) -> bool:
    """
    Send a real-time notification to a specific employee.
    
    Args:
        employee_id: The employee ID (e.g., 'EMP001', 'V0921')
        notification_data: Dictionary containing notification details
            {
                'notification_id': int,
                'title': str,
                'message': str,
                'type': str,  # 'leave_request', 'announcement', etc.
                'created_at': str,
                'url': str (optional) - URL to redirect when clicked
            }
    
    Returns:
        bool: True if sent successfully, False otherwise
    
    Example:
        send_notification(
            employee_id='EMP001',
            notification_data={
                'notification_id': 123,
                'title': 'Leave Request',
                'message': 'John Doe has requested leave',
                'type': 'leave_request',
                'created_at': '2025-12-12T10:30:00',
                'url': '/leaves/requests/123'
            }
        )
    """
    try:
        channel_layer = get_channel_layer()
        group_name = f'notifications_{employee_id}'
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notification_message',
                'notification': notification_data
            }
        )
        
        logger.info(f"Notification sent to {employee_id}: {notification_data.get('title', 'No title')}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send notification to {employee_id}: {str(e)}")
        return False


def send_notification_to_user(user_id: int, notification_data: dict) -> bool:
    """
    Send a real-time notification to a specific user by user_id.
    
    Args:
        user_id: The user's ID from ci_erp_users table
        notification_data: Dictionary containing notification details
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        channel_layer = get_channel_layer()
        group_name = f'notifications_user_{user_id}'
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notification_message',
                'notification': notification_data
            }
        )
        
        logger.info(f"Notification sent to user {user_id}: {notification_data.get('title', 'No title')}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send notification to user {user_id}: {str(e)}")
        return False


def send_global_notification(notification_type: str, data: dict) -> bool:
    """
    Send a notification to all connected clients (global channel).
    
    Args:
        notification_type: Type of notification 
            ('birthday', 'anniversary', 'new_joiner', 'announcement')
        data: Dictionary containing notification details
    
    Returns:
        bool: True if sent successfully, False otherwise
    
    Example:
        send_global_notification(
            notification_type='birthday',
            data={
                'full_name': 'John Doe',
                'department': 'Engineering',
                'message': 'Happy Birthday!'
            }
        )
    """
    try:
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            'global_notifications',
            {
                'type': 'broadcast_message',
                'notification_type': notification_type,
                'data': data
            }
        )
        
        logger.info(f"Global notification sent: {notification_type}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send global notification: {str(e)}")
        return False


def send_notification_to_multiple(employee_ids: list, notification_data: dict) -> dict:
    """
    Send the same notification to multiple employees.
    
    Args:
        employee_ids: List of employee IDs
        notification_data: Dictionary containing notification details
    
    Returns:
        dict: {'success': [...], 'failed': [...]}
    """
    results = {'success': [], 'failed': []}
    
    for employee_id in employee_ids:
        if send_notification(employee_id, notification_data):
            results['success'].append(employee_id)
        else:
            results['failed'].append(employee_id)
    
    return results


# Helper function to create notification and broadcast it
def create_and_broadcast_notification(
    send_to_id: int,
    employee_id: str,
    title: str,
    message: str,
    notification_type: str = 'general',
    url: str = None
) -> bool:
    """
    Create a notification in the database and broadcast it via WebSocket.
    
    This is a convenience function that combines database insert with broadcast.
    Call this when you want to both persist and broadcast a notification.
    
    Note: This function only broadcasts. You should still create the database
    record using your existing notification creation logic.
    
    Args:
        send_to_id: The user_id to send notification to
        employee_id: The employee_id to send notification to
        title: Notification title
        message: Notification message/content
        notification_type: Type of notification
        url: Optional URL for redirect on click
    
    Returns:
        bool: True if broadcast successful
    """
    from datetime import datetime
    
    notification_data = {
        'title': title,
        'message': message,
        'type': notification_type,
        'created_at': datetime.now().isoformat(),
        'url': url,
        'is_read': False
    }
    
    # Try both methods to ensure delivery
    success_by_employee = send_notification(employee_id, notification_data) if employee_id else False
    success_by_user = send_notification_to_user(send_to_id, notification_data) if send_to_id else False
    
    return success_by_employee or success_by_user
