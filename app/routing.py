"""
WebSocket URL Routing for Notifications

This module defines the WebSocket URL patterns for the notification system.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Personal notifications for a specific employee (by employee_id)
    # Example: ws://localhost:8013/ws/notifications/EMP001/
    re_path(
        r'ws/notifications/(?P<employee_id>[\w-]+)/$',
        consumers.NotificationConsumer.as_asgi()
    ),
    
    # Personal notifications for a specific user (by user_id)
    # Example: ws://localhost:8013/ws/notifications/user/123/
    re_path(
        r'ws/notifications/user/(?P<user_id>\d+)/$',
        consumers.NotificationConsumer.as_asgi()
    ),
    
    # Global notifications channel (birthdays, announcements, etc.)
    # Example: ws://localhost:8013/ws/notifications/global/
    re_path(
        r'ws/notifications/global/$',
        consumers.GlobalNotificationConsumer.as_asgi()
    ),
]
