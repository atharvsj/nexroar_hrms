from datetime import date, datetime, time
from django.db import connection, transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from hrms_app.permissions import *
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated


class EmployeeManagerDropdown(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        try:
            with connection.cursor() as c:

                c.execute(
                    """select u.id, concat(first_name,' ', last_name) as emp_name, ud.employee_id from ci_erp_users u left join ci_erp_users_details ud on u.id = ud.user_id group by u.id"""
                )
                employee = c.fetchall()

                c.execute(
                    """select id, concat(first_name,' ', last_name) as emp_name from ci_erp_users where user_role_id = 2"""
                )
                manager = c.fetchall()

                emp_data = [
                    {
                        "id": row[0],
                        "employee_name": row[1],
                        "employee_id": row[2],
                    }
                    for row in employee
                ]

                manager_data = [
                    {
                        "manager_id": row[0],
                        "manager_name": row[1],
                    }
                    for row in manager
                ]

            return Response(
                {
                    "status": "success",
                    "employee_data": emp_data,
                    "manager_data": manager_data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DesignationDepartmentDropdown(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        dept_id = request.query_params.get("dept_id")

        try:
            with connection.cursor() as c:
                if dept_id:
                    
                    c.execute(
                        """
                        SELECT designation_id, designation_name 
                        FROM ci_designations 
                        WHERE department_id = %s 
                        GROUP BY designation_id
                        """,
                        [dept_id],
                    )
                    designations = c.fetchall()

                    desig_data = [
                        {"desig_id": row[0], "desig_name": row[1]}
                        for row in designations
                    ]

                    return Response(
                        {"status": "success", "desig_data": desig_data},
                        status=status.HTTP_200_OK,
                    )
                else:
                    
                    c.execute(
                        """
                        SELECT department_id, department_name 
                        FROM ci_departments 
                        GROUP BY department_id
                        """
                    )
                    departments = c.fetchall()

                    dept_data = [
                        {"dept_id": row[0], "dept_name": row[1]} for row in departments
                    ]

                    return Response(
                        {"status": "success", "dept_data": dept_data},
                        status=status.HTTP_200_OK,
                    )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# class OfficeShiftDropdown(APIView):

#     permission_classes = [AllowAny]

#     def get(self, request):

#         try:
#             with connection.cursor() as c:

#                 c.execute(
#                     """select office_shift_id, shift_name from ci_office_shifts group by office_shift_id"""
#                 )
#                 office_shift = c.fetchall()

#                 office_shift_data = [
#                     {
#                         "office_shift_id": row[0],
#                         "office_shift_name": row[1],
#                     }
#                     for row in office_shift
#                 ]

#             return Response(
#                 {
#                     "status": "success",
#                     "office_shift_data": office_shift_data,
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occured: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )
