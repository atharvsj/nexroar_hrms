
from datetime import date, datetime, time
from django.db import connection, transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from app.permissions import IsAdmin
from hrms_app.permissions import *
from rest_framework import status, generics

import os
from urllib.parse import quote
from django.conf import settings
from django.core.files.storage import default_storage
import os
from django.contrib.auth.hashers import make_password

import re
import bcrypt


# class Payroll(APIView):

    # def get(self, request):

        # try:
        #     with connection.cursor() as c:
                

        # except Exception as e:
        #     return Response({"status":"error","message": f"An error occured: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        