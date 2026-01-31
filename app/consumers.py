"""
WebSocket Consumer for Real-Time Notifications

This module handles WebSocket connections for pushing notifications
to connected clients in real-time.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import connection
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time notifications.
    
    Each employee connects to their own notification channel based on their employee_id.
    When a new notification is created, it gets broadcast to the specific employee's channel.
    """

    async def connect(self):
        """
        Handle WebSocket connection.
        
        URL pattern: ws/notifications/<employee_id>/
        Each employee joins a group named 'notifications_<employee_id>'
        """
        self.employee_id = self.scope['url_route']['kwargs'].get('employee_id')
        self.user_id = self.scope['url_route']['kwargs'].get('user_id')
        
        # Create a unique group name for this employee/user
        if self.employee_id:
            self.room_group_name = f'notifications_{self.employee_id}'
        elif self.user_id:
            self.room_group_name = f'notifications_user_{self.user_id}'
        else:
            # Reject connection if no identifier provided
            await self.close()
            return

        # Join the notification group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Send initial connection success message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to notification service',
            'group': self.room_group_name
        }))
        
        logger.info(f"WebSocket connected: {self.room_group_name}")

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        Remove the client from the notification group.
        """
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"WebSocket disconnected: {self.room_group_name}")

    async def receive(self, text_data):
        """
        Handle incoming messages from WebSocket.
        
        Clients can send:
        - ping: Keep-alive message
        - mark_read: Mark notification as read
        - fetch_unread: Request unread notifications count
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type', '')

            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
            
            elif message_type == 'mark_read':
                notification_id = data.get('notification_id')
                if notification_id:
                    await self.mark_notification_read(notification_id)
                    await self.send(text_data=json.dumps({
                        'type': 'notification_marked_read',
                        'notification_id': notification_id
                    }))
            
            elif message_type == 'fetch_unread_count':
                count = await self.get_unread_count()
                await self.send(text_data=json.dumps({
                    'type': 'unread_count',
                    'count': count
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'An error occurred'
            }))

    async def notification_message(self, event):
        """
        Handler for notification messages sent to the group.
        
        This is called when send_notification() broadcasts a message.
        The event contains the notification data to be sent to the client.
        """
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))

    async def global_notification(self, event):
        """
        Handler for global notifications (birthdays, announcements, etc.)
        """
        await self.send(text_data=json.dumps({
            'type': 'global_notification',
            'data': event['data']
        }))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a notification as clicked/read in the database."""
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE ci_notification SET is_click = 'Y' WHERE notification_id = %s",
                [notification_id]
            )

    @database_sync_to_async
    def get_unread_count(self):
        """Get the count of unread notifications for this user."""
        with connection.cursor() as cursor:
            if self.user_id:
                cursor.execute(
                    "SELECT COUNT(*) FROM ci_notification WHERE send_to_id = %s AND is_click = 'N'",
                    [self.user_id]
                )
            else:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM ci_notification cn
                    JOIN ci_erp_users u ON cn.send_to_id = u.id
                    JOIN ci_erp_users_details ud ON u.id = ud.user_id
                    WHERE ud.employee_id = %s AND cn.is_click = 'N'
                    """,
                    [self.employee_id]
                )
            result = cursor.fetchone()
            return result[0] if result else 0


class GlobalNotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for global notifications that all employees receive.
    
    Used for:
    - Birthday announcements
    - Work anniversaries
    - Company-wide announcements
    - New employee joins
    """

    async def connect(self):
        """Connect to the global notifications channel."""
        self.room_group_name = 'global_notifications'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to global notification service'
        }))

    async def disconnect(self, close_code):
        """Disconnect from the global notifications channel."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming messages."""
        try:
            data = json.loads(text_data)
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
        except json.JSONDecodeError:
            pass

    async def broadcast_message(self, event):
        """Handle broadcast messages sent to the global group."""
        await self.send(text_data=json.dumps({
            'type': event.get('notification_type', 'announcement'),
            'data': event['data']
        }))
