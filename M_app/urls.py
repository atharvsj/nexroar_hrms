
# hrapp/urls.py

from django.urls import path
from .views import AnnouncementApiView, AnnouncementDetailApiView, PolicyListApiView, PolicyDetailApiView,PolicyAcknowledgeListView,AnnouncementAcknowledgeView,CreateTicketView,DepartmentEmployeeListView,TicketDetailView

urlpatterns = [
    # This URL will serve the raw JSON data
    path('announcements/', AnnouncementApiView.as_view(), name='announcement-api-list'), # get, post
    path('announcements_details/<int:announcement_id>/', AnnouncementDetailApiView.as_view(), name='announcement-api-list'), # put delete
    path('policies/', PolicyListApiView.as_view(), name='policy-api-list'), # get, post
    path('policies_details/<int:policy_id>/', PolicyDetailApiView.as_view(), name='policy-api-detail'),  # put, detele
    path('policies_acknowledgements/', PolicyAcknowledgeListView.as_view(), name='policy-acknowledge-list'),  # get
    path('policies_dashboard/', AnnouncementAcknowledgeView.as_view(), name='policy-acknowledgements'),
    path('create_tickets/', CreateTicketView.as_view(), name='support-ticket-list-create'), # post- put
    path('department_wise_employee/', DepartmentEmployeeListView.as_view(), name='support-ticket-list-create'), # post
    path('ticket_view/<int:ticket_id>/', TicketDetailView.as_view(), name='ticket-detail'),

    
]