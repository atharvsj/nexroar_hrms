import calendar
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
from decimal import Decimal, InvalidOperation

import os
from urllib.parse import quote
from django.conf import settings
from django.core.files.storage import default_storage
import os
from django.contrib.auth.hashers import make_password

import re
import bcrypt


class AdminOnlyView(APIView):
    permission_classes = [AllowAny]


class ContractDetails(AdminOnlyView):

    def post(self, request):
        return self._get_contract_details(request)

    def patch(self, request):
        return self._update_contract_details(request)

    def delete(self, request):

        type = int(request.data.get("type"))
        pay_id = int(request.data.get("pay_id"))

        if not type or not pay_id:
            return Response(
                {"status": "error", "message": "type or pay_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                with connection.cursor() as c:

                    if type == 2:
                        c.execute(
                            """delete from ci_payslip_allowances where payslip_allowances_id = %s""",
                            [pay_id],
                        )
                    elif type == 3:
                        c.execute(
                            """delete from ci_payslip_commissions where payslip_commissions_id = %s""",
                            [pay_id],
                        )
                    elif type == 4:
                        c.execute(
                            """delete from ci_payslip_statutory_deductions where payslip_deduction_id = %s""",
                            [pay_id],
                        )
                    elif type == 5:
                        c.execute(
                            """delete from ci_payslip_other_payments where payslip_other_payment_id = %s""",
                            [pay_id],
                        )

            return Response(
                {
                    "status": "success",
                    "message": "contract details deleted successfully",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_contract_details(self, request):
        user_id = request.data.get("user_id")
        type = int(request.data.get("type", 0))

        if not type or not user_id:
            return Response(
                {"status": "error", "message": "type or user_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:
                # Fetch user info
                c.execute(
                    "SELECT user_type, email FROM ci_erp_users WHERE id = %s", [user_id]
                )
                user_info = c.fetchone()

                if not user_info:
                    return Response(
                        {"status": "error", "message": "User not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                contract_details = {}
                if type == 1:
                    query = """
                        SELECT 
                            u.user_type, 
                            u.email,
                            ud.date_of_joining AS contract_date,
                            ud.billing,
                            ud.department_id as department_id,
                            dpt.department_name AS department,
                            ud.designation_id as designation_id,
                            dsg.designation_name AS designation,
                            ud.basic_salary,
                            ud.gross_salary,
                            ud.hourly_rate,
                            ud.payslip_type,
                            ud.office_shift_id as office_shift_id,
                            ofc.shift_name AS office_shift,
                            DATE_FORMAT(ee.exit_date, '%%d-%%m-%%Y') AS contract_end,
                            ud.probation AS probation,
                            ud.probation_end_date AS probation_end_date,
                            CONCAT(uu.first_name, ' ', uu.last_name) AS manager_name,
                            ud.role_description
                        FROM ci_erp_users u
                        LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
                        LEFT JOIN ci_departments dpt ON ud.department_id = dpt.department_id
                        LEFT JOIN ci_designations dsg ON ud.designation_id = dsg.designation_id
                        LEFT JOIN ci_office_shifts ofc ON ud.office_shift_id = ofc.office_shift_id
                        LEFT JOIN ci_employee_exit ee ON ud.user_id = ee.employee_id
                        LEFT JOIN ci_erp_users uu ON ud.manager = uu.id
                        WHERE u.id = %s
                    """
                    c.execute(query, [user_id])
                    columns = [col[0] for col in c.description]
                    contract_details = [dict(zip(columns, row)) for row in c.fetchall()]

                else:
                    query_map = {
                        2: {
                            "query": """
                                SELECT payslip_allowances_id as id, pay_title AS title, pay_amount AS amount,
                                       is_taxable AS allowance_option, is_fixed AS amount_option
                                FROM ci_payslip_allowances
                                WHERE staff_id = %s
                            """
                        },
                        3: {
                            "query": """
                                SELECT payslip_commissions_id as id, pay_title AS title, pay_amount AS amount,
                                       is_taxable AS commission_option, is_fixed AS amount_option
                                FROM ci_payslip_commissions
                                WHERE staff_id = %s
                            """
                        },
                        4: {
                            "query": """
                                SELECT payslip_deduction_id as id, pay_title AS title, pay_amount AS amount,
                                       is_fixed AS deduction_option
                                FROM ci_payslip_statutory_deductions
                                WHERE staff_id = %s
                            """
                        },
                        5: {
                            "query": """
                                SELECT payslip_other_payment_id as id, pay_title AS title, pay_amount AS amount,
                                       is_taxable AS reimbursement_option, is_fixed AS amount_option
                                FROM ci_payslip_other_payments
                                WHERE staff_id = %s
                            """
                        },
                    }

                    if type in query_map:
                        c.execute(query_map[type]["query"], [user_id])
                        rows = c.fetchall()
                        if rows:
                            columns = [col[0] for col in c.description]
                            contract_details = [dict(zip(columns, row)) for row in rows]

            return Response(
                {
                    "user_info": {"user_type": user_info[0], "email": user_info[1]},
                    "contract_details": contract_details,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    
    # def _update_contract_details(self, request):

    #     user_id = request.data.get("user_id")
    #     type = int(request.data.get("type", 0))

    #     if not type or not user_id:
    #         return Response(
    #             {"status": "error", "message": "type or user_id is missing"},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )

    #     if type != 1:
    #         pay_id = request.data.get("pay_id")

    #         # if not pay_id:
    #         #     return Response(
    #         #         {"status": "error", "message": "pay_id is required"},
    #         #         status=status.HTTP_400_BAD_REQUEST,
    #         #     )

    #     try:
    #         with connection.cursor() as c:
    #             if type == 1:
    #                 # Collect fields for ci_erp_users_details
    #                 probation_value = request.data.get("probation")
    #                 details_fields = {
    #                     "department_id": request.data.get("department_id"),
    #                     "designation_id": request.data.get("designation_id"),
    #                     "basic_salary": request.data.get("basic_salary"),
    #                     "gross_salary": request.data.get("gross_salary"),
    #                     "hourly_rate": request.data.get("hourly_rate"),
    #                     "payslip_type": request.data.get("payslip_type"),
    #                     "office_shift_id": request.data.get("office_shift_id"),
    #                     "probation": request.data.get("probation"),
    #                     "probation_end_date": request.data.get("probation_end_date"),
    #                     "manager": request.data.get("manager"),
    #                     "role_description": request.data.get("role_description"),
    #                     "billing": request.data.get("billing"),
    #                     "contract_date": request.data.get("contract_date"),

    #                 }
    #                 details_update = [
    #                     f"{key} = %s"
    #                     for key, val in details_fields.items()
    #                     if val is not None
    #                 ]
    #                 details_values = [
    #                     val for val in details_fields.values() if val is not None
    #                 ]

    #                 if details_update:
    #                     details_values.append(user_id)
    #                     c.execute(
    #                         f"""
    #                         UPDATE ci_erp_users_details
    #                         SET {", ".join(details_update)}
    #                         WHERE user_id = %s
    #                         """,
    #                         details_values,
    #                     )
    #                 if probation_value in ["N", "n"]:
    #                     c.execute(
    #                         """
    #                         SELECT ud.employee_id, CONCAT(u.first_name, ' ', u.last_name)
    #                         FROM ci_erp_users u
    #                         JOIN ci_erp_users_details ud ON u.id = ud.user_id
    #                         WHERE u.id = %s
    #                         """,
    #                         [user_id],
    #                     )
    #                     row = c.fetchone()
    #                     if row:
    #                         emp_id, employee_name = row
    #                         self._init_leave_balances(c, emp_id, employee_name)


    #                 company_id = request.data.get("company_id")

    #                 contract_date = request.data.get("contract_date")
    #                 if contract_date:
    #                     c.execute(
    #                         "UPDATE ci_erp_users SET company_id = %s, created_at = %s WHERE id = %s",
    #                         [company_id, contract_date, user_id],
    #                     )

    #             else:


    #                 update_map = {
    #                     2: {
    #                         "table": "ci_payslip_allowances",
    #                         "id_field": "payslip_allowances_id",
    #                         "fields": [
    #                             "pay_title",
    #                             "pay_amount",
    #                             "is_taxable",
    #                             "is_fixed",
    #                             "salary_month",
    #                         ],
    #                     },
    #                     3: {
    #                         "table": "ci_payslip_commissions",
    #                         "id_field": "payslip_commissions_id",
    #                         "fields": [
    #                             "pay_title",
    #                             "pay_amount",
    #                             "is_taxable",
    #                             "is_fixed",
    #                             "salary_month",
    #                         ],
    #                     },
    #                     4: {
    #                         "table": "ci_payslip_statutory_deductions",
    #                         "id_field": "payslip_deduction_id",
    #                         "fields": [
    #                             "pay_title",
    #                             "pay_amount",
    #                             "is_fixed",
    #                             "salary_month",
    #                         ],
    #                     },
    #                     5: {
    #                         "table": "ci_payslip_other_payments",
    #                         "id_field": "payslip_other_payment_id",
    #                         "fields": [
    #                             "pay_title",
    #                             "pay_amount",
    #                             "is_taxable",
    #                             "is_fixed",
    #                             "salary_month",
    #                         ],
    #                     },
    #                 }

    #                 config = update_map.get(type)
    #                 if not config:
    #                     return Response(
    #                         {"status": "error", "message": "Invalid type for update"},
    #                         status=status.HTTP_400_BAD_REQUEST,
    #                     )

    #                 table = config["table"]
    #                 id_field = config["id_field"]
    #                 fields = config["fields"]

    #                 update_fields = []
    #                 update_values = []

    #                 insert_columns = []
    #                 insert_values = []
    #                 insert_placeholders = []

    #                 for field in fields:
    #                     if field in request.data:
    #                         update_fields.append(f"{field} = %s")
    #                         update_values.append(request.data[field])
    #                         insert_columns.append(field)
    #                         insert_values.append(request.data[field])
    #                         insert_placeholders.append("%s")

    #                 # Always include staff_id
    #                 update_values.append(user_id)
    #                 update_values.append(pay_id)

    #                 update_query = f"""
    #                     UPDATE {table}
    #                     SET {", ".join(update_fields)}
    #                     WHERE staff_id = %s AND {id_field} = %s
    #                 """

    #                 c.execute(update_query, update_values)

    #                 # If no rows were updated, insert new
    #                 if c.rowcount == 0:
    #                     insert_columns += ["staff_id"]
    #                     insert_values += [user_id]
    #                     insert_placeholders += ["%s"]

    #                     insert_query = f"""
    #                         INSERT INTO {table} ({", ".join(insert_columns)})
    #                         VALUES ({", ".join(insert_placeholders)})
    #                     """

    #                     c.execute(insert_query, insert_values)

    #         return Response(
    #             {
    #                 "status": "success",
    #                 "message": "Contract details updated successfully",
    #             },
    #             status=status.HTTP_200_OK,
    #         )

    #     except Exception as e:
    #         return Response(
    #             {"status": "error", "message": f"An error occurred: {str(e)}"},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         )
    
     
    def _update_contract_details(self, request):
 
        user_id = request.data.get("user_id")
        type = int(request.data.get("type", 0))
 
        if not type or not user_id:
            return Response(
                {"status": "error", "message": "type or user_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )
 
        if type != 1:
            pay_id = request.data.get("pay_id")
 
            # if not pay_id:
            #     return Response(
            #         {"status": "error", "message": "pay_id is required"},
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )
 
        try:
            with connection.cursor() as c:
                if type == 1:
                    # Collect fields for ci_erp_users_details
                    probation_value = request.data.get("probation")
                    details_fields = {
                        "department_id": request.data.get("department_id"),
                        "designation_id": request.data.get("designation_id"),
                        "basic_salary": request.data.get("basic_salary"),
                        "gross_salary": request.data.get("gross_salary"),
                        "hourly_rate": request.data.get("hourly_rate"),
                        "payslip_type": request.data.get("payslip_type"),
                        "office_shift_id": request.data.get("office_shift_id"),
                        "probation": request.data.get("probation"),
                        "probation_end_date": request.data.get("probation_end_date"),
                        "manager": request.data.get("manager"),
                        "role_description": request.data.get("role_description"),
                        "billing": request.data.get("billing"),
                        "date_of_joining": request.data.get("contract_date"),
                    }
                    details_update = [
                        f"{key} = %s"
                        for key, val in details_fields.items()
                        if val is not None
                    ]
                    details_values = [
                        val for val in details_fields.values() if val is not None
                    ]
 
                    if details_update:
                        details_values.append(user_id)
                        c.execute(
                            f"""
                            UPDATE ci_erp_users_details
                            SET {", ".join(details_update)}
                            WHERE user_id = %s
                            """,
                            details_values,
                        )
                    if probation_value in ["N", "n"]:
                        c.execute(
                            """
                            SELECT ud.employee_id, CONCAT(u.first_name, ' ', u.last_name)
                            FROM ci_erp_users u
                            JOIN ci_erp_users_details ud ON u.id = ud.user_id
                            WHERE u.id = %s
                            """,
                            [user_id],
                        )
                        row = c.fetchone()
                        if row:
                            emp_id, employee_name = row
                            self._init_leave_balances(c, emp_id, employee_name)
 
 
                    company_id = request.data.get("company_id")
 
                    # contract_date = request.data.get("contract_date")
                    # if contract_date:
                    #     c.execute(
                    #         "UPDATE ci_erp_users SET company_id = %s, created_at = %s WHERE id = %s",
                    #         [company_id, contract_date, user_id],
                    #     )
 
                else:
                    update_map = {
                        2: {
                            "table": "ci_payslip_allowances",
                            "id_field": "payslip_allowances_id",
                            "fields": [
                                "pay_title",
                                "pay_amount",
                                "is_taxable",
                                "is_fixed",
                                "salary_month",
                            ],
                        },
                        3: {
                            "table": "ci_payslip_commissions",
                            "id_field": "payslip_commissions_id",
                            "fields": [
                                "pay_title",
                                "pay_amount",
                                "is_taxable",
                                "is_fixed",
                                "salary_month",
                            ],
                        },
                        4: {
                            "table": "ci_payslip_statutory_deductions",
                            "id_field": "payslip_deduction_id",
                            "fields": [
                                "pay_title",
                                "pay_amount",
                                "is_fixed",
                                "salary_month",
                            ],
                        },
                        5: {
                            "table": "ci_payslip_other_payments",
                            "id_field": "payslip_other_payment_id",
                            "fields": [
                                "pay_title",
                                "pay_amount",
                                "is_taxable",
                                "is_fixed",
                                "salary_month",
                            ],
                        },
                    }
 
                    config = update_map.get(type)
                    if not config:
                        return Response(
                            {"status": "error", "message": "Invalid type for update"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
 
                    table = config["table"]
                    id_field = config["id_field"]
                    fields = config["fields"]
 
                    update_fields = []
                    update_values = []
 
                    insert_columns = []
                    insert_values = []
                    insert_placeholders = []
 
                    for field in fields:
                        if field in request.data:
                            update_fields.append(f"{field} = %s")
                            update_values.append(request.data[field])
                            insert_columns.append(field)
                            insert_values.append(request.data[field])
                            insert_placeholders.append("%s")
 
                    # Always include staff_id
                    update_values.append(user_id)
                    update_values.append(pay_id)
 
                    update_query = f"""
                        UPDATE {table}
                        SET {", ".join(update_fields)}
                        WHERE staff_id = %s AND {id_field} = %s
                    """
 
                    c.execute(update_query, update_values)
 
                    # If no rows were updated, insert new
                    if c.rowcount == 0:
                        insert_columns += ["staff_id"]
                        insert_values += [user_id]
                        insert_placeholders += ["%s"]
 
                        insert_query = f"""
                            INSERT INTO {table} ({", ".join(insert_columns)})
                            VALUES ({", ".join(insert_placeholders)})
                        """
 
                        c.execute(insert_query, insert_values)
 
            return Response(
                {
                    "status": "success",
                    "message": "Contract details updated successfully",
                },
                status=status.HTTP_200_OK,
            )
 
        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
            
    def _init_leave_balances(self, cursor, employee_id, employee_name):
        """Initialize leave balances only if not already assigned"""
        current_year = datetime.now().year
        leave_assignments = {
            "Casual Leave (CL)": 6,
            "Medical Leave (ML)": 7,
            "Maternity Leave": 182,
            "Paid Leave": 0,
            "Paternity Leave": 3,
        }

        # ✅ Check if already exists for this year
        cursor.execute(
            "SELECT COUNT(*) FROM ci_leave_balance WHERE employee_id = %s AND year = %s",
            [employee_id, current_year],
        )
        (count,) = cursor.fetchone()
        if count > 0:
            return  # Skip if already allocated

        # Insert fresh balances
        cursor.execute(
            "SELECT constants_id, category_name FROM ci_erp_constants WHERE type = 'leave_type' AND category_name IN %s",
            [tuple(leave_assignments.keys())],
        )
        leave_types = cursor.fetchall()

        for constants_id, category_name in leave_types:
            cursor.execute(
                """
                INSERT INTO ci_leave_balance 
                (employee_id, employee_name, leave_type_id, leave_type, balance_leave, carry_forward, last_paid_leave_given_at, year, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Y')
                """,
                [employee_id, employee_name, constants_id, category_name,
                leave_assignments[category_name], 0, None, current_year],
            )


 
class EmployeeBasicInformation(AdminOnlyView):


    gender_map = {1: "Male", 2: "Female", 0: "Others"}
    gender_reverse_map = {"male": 1, "female": 2, "others": 0}

    marital_status_map = {1: "Married", 0: "Unmarried"}
    marital_status_reverse_map = {"married": 1, "unmarried": 0}

    is_active_map = {1: "Active", 0: "Inactive"}
    is_active_reverse_map = {"active": 1, "inactive": 0}


    def post(self, request):
        return self._get_contract_details(request)

    def patch(self, request):
        return self._update_contract_details(request)

    def _get_contract_details(self, request):

        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"status": "error", "message": "user_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:

                query = """SELECT 
                                u.first_name,
                                u.middle_name,
                                u.last_name,
                                u.contact_number,
                                u.gender,
                                u.age,
                                ud.employee_id,
                                CONCAT(um.first_name, ' ', um.last_name) AS manager,
                                
                                ud.date_of_birth,
                                u.is_active,
                                ud.marital_status,
                                u.user_role_id as role_id,
                                sr.role_name,
                                u.state as state_id,
                                ecs.category_name as state,
                                u.country as country_id,
                                ec.category_name as country,
                                eh.employee_hub_name,
                                u.city,
                                u.zipcode,
                                ud.blood_group,
                                u.address_1,
                                u.address_2,
                                u.correspondence_state,
                                u.correspondence_country,
                                u.correspondence_city,
                                u.correspondence_pincode
                            FROM
                                ci_erp_users u
                                    LEFT JOIN
                                ci_erp_users_details ud ON u.id = ud.user_id
                                    LEFT JOIN
                                ci_staff_roles sr ON u.user_role_id = sr.role_id
                                    LEFT JOIN
                                ci_erp_constants ecr ON ud.religion_id = ecr.constants_id
                                    AND ecr.type = 'religion'
                                    LEFT JOIN
                                ci_erp_constants ecs ON u.state = ecs.constants_id
         AND ecs.type = 'state'
                                    LEFT JOIN
                                ci_erp_constants ec ON u.country = ec.constants_id
         AND ec.type = 'country'
                                    LEFT JOIN
                                ci_employee_hub eh ON u.employee_hub_id = eh.employee_hub_id
                                    LEFT JOIN 
                                ci_erp_users um ON ud.manager = um.id
                            WHERE
                                u.id = %s;"""

                c.execute(query, [user_id])

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, row)) for row in c.fetchall()]


            for r in response:
                if r.get("gender") is not None:
                    r["gender"] = self.gender_map.get(int(r["gender"]), "Unknown")
                if r.get("marital_status") is not None:
                    r["marital_status"] = self.marital_status_map.get(int(r["marital_status"]), "Unknown")
                if r.get("is_active") is not None:
                    r["is_active"] = self.is_active_map.get(int(r["is_active"]), "Unknown")


            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



    def _update_contract_details(self, request):

        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"status": "error", "message": "user_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:

                 # --- Convert char to number before update ---
                gender_val = request.data.get("gender")
                # if gender_val:
                #     gender_val = self.gender_reverse_map.get(gender_val.lower())
                if gender_val is not None:
                    if isinstance(gender_val, int):  # already numeric
                        pass
                    elif isinstance(gender_val, str):
                        gender_val = self.gender_reverse_map.get(gender_val.lower())

                marital_val = request.data.get("marital_status")
                if marital_val:
                    marital_val = self.marital_status_reverse_map.get(marital_val.lower())

                # is_active_val = request.data.get("is_active")
                # if is_active_val:
                #     is_active_val = self.is_active_reverse_map.get(is_active_val.lower())


                # --- ci_erp_users dynamic update ---
                user_fields = {
                    "first_name": request.data.get("first_name"),
                    "middle_name": request.data.get("middle_name"),
                    "last_name": request.data.get("last_name"),
                    "contact_number": request.data.get("contact_number"),
                    "gender": gender_val,   
                    "age": request.data.get("age"),
                    "is_active": request.data.get("is_active"),
                    "user_role_id": request.data.get("role_id"),
                    "state": request.data.get("state_id"),
                    "country": request.data.get("country_id"),
                    "correspondence_state": request.data.get("correspondence_state"),
                    "correspondence_country": request.data.get("correspondence_country"),
                    "correspondence_city": request.data.get("correspondence_city"),
                    "correspondence_pincode": request.data.get("correspondence_pincode"),
                    "employee_hub_id": request.data.get("employee_hub_id"),
                    "city": request.data.get("city"),
                    "zipcode": request.data.get("zipcode"),
                    "address_1": request.data.get("address_1"),
                    "address_2": request.data.get("address_2"),
                }

                user_update_clauses = []
                user_values = []

                for key, value in user_fields.items():
                    if value is not None:
                        user_update_clauses.append(f"{key} = %s")
                        user_values.append(value)

                if user_update_clauses:
                    user_update_query = f"""
                        UPDATE ci_erp_users
                        SET {', '.join(user_update_clauses)}
                        WHERE id = %s
                    """
                    user_values.append(user_id)
                    c.execute(user_update_query, user_values)

                # --- ci_erp_users_details dynamic update ---
                detail_fields = {
                    "employee_id": request.data.get("employee_id"),
                    "date_of_birth": request.data.get("date_of_birth"),
                    "marital_status": marital_val,
                    "religion_id": request.data.get("religion_id"),
                    "blood_group": request.data.get("blood_group"),                    
                }

                detail_update_clauses = []
                detail_values = []

                for key, value in detail_fields.items():
                    if value is not None:
                        detail_update_clauses.append(f"{key} = %s")
                        detail_values.append(value)

                if detail_update_clauses:
                    detail_update_query = f"""
                        UPDATE ci_erp_users_details
                        SET {', '.join(detail_update_clauses)}
                        WHERE user_id = %s
                    """
                    detail_values.append(user_id)
                    c.execute(detail_update_query, detail_values)

            return Response(
                {"status": "success", "message": "User details updated successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
 
# class PersonalInformation(AdminOnlyView):

#     def post(self, request):
#         return self._get_personal_details(request)

#     def patch(self, request):
#         return self._update_personal_details(request)

#     def _get_personal_details(self, request):

#         user_id = request.data.get("user_id")
#         type = int(request.data.get("type", 0))

#         if not type or not user_id:
#             return Response(
#                 {"status": "error", "message": "type or user_id is missing"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             with connection.cursor() as c:

#                 personal_details = {}
#                 if type == 1:

#                     query = """select bio,experience 
#                                 from ci_erp_users_details 
#                                 where user_id = %s;"""

#                     c.execute(query, [user_id])

#                     columns = [col[0] for col in c.description]
#                     row = c.fetchone()
#                     if row:
#                         columns = [col[0] for col in c.description]
#                         personal_details = dict(zip(columns, row))

#                 elif type == 2:

#                     query = """select fb_profile,twitter_profile,gplus_profile,linkedin_profile
#                                 from ci_erp_users_details 
#                                 where user_id = %s;"""

#                     c.execute(query, [user_id])

#                     columns = [col[0] for col in c.description]
#                     row = c.fetchone()
#                     if row:
#                         columns = [col[0] for col in c.description]
#                         personal_details = dict(zip(columns, row))

#                 elif type == 3:

#                     query = """select account_title,account_number,bank_name,iban,bank_branch,pan_number,esic_number,pf_number,uan_number,ifsc_code,swift_code
#                                 from ci_erp_users_details 
#                                 where user_id = %s;"""

#                     c.execute(query, [user_id])

#                     columns = [col[0] for col in c.description]
#                     row = c.fetchone()
#                     if row:
#                         columns = [col[0] for col in c.description]
#                         personal_details = dict(zip(columns, row))

#                 elif type == 4:

#                     query = """select contact_full_name,contact_phone_no,contact_email,contact_address
#                                 from ci_erp_users_details 
#                                 where user_id = %s;"""

#                     c.execute(query, [user_id])

#                     columns = [col[0] for col in c.description]
#                     row = c.fetchone()
#                     if row:
#                         columns = [col[0] for col in c.description]
#                         personal_details = dict(zip(columns, row))

#                 elif type == 6:

#                     query = """select passport_no,vehicle_no,driving_licence_no,aadhar_no
#                                 from ci_erp_users_details
#                                 where user_id = %s;"""

#                     c.execute(query, [user_id])

#                     columns = [col[0] for col in c.description]
#                     row = c.fetchone()
#                     if row:
#                         columns = [col[0] for col in c.description]
#                         personal_details = dict(zip(columns, row))

#             return Response(
#                 {"status": "success", "personal_details": personal_details},
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


#     def _update_personal_details(self, request):

#         user_id = request.data.get("user_id")
#         type = int(request.data.get("type", 0))

#         if not type or not user_id:
#             return Response(
#                 {"status": "error", "message": "type or user_id is missing"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             with connection.cursor() as c:

#                 field_map = {}

#                 if type == 1:
#                     field_map = {
#                         "bio": request.data.get("bio"),
#                         "experience": request.data.get("experience"),
#                     }

#                 elif type == 2:
#                     field_map = {
#                         "fb_profile": request.data.get("fb_profile"),
#                         "twitter_profile": request.data.get("twitter_profile"),
#                         "gplus_profile": request.data.get("gplus_profile"),
#                         "linkedin_profile": request.data.get("linkedin_profile"),
#                     }

#                 elif type == 3:
#                     field_map = {
#                         "account_title": request.data.get("account_title"),
#                         "account_number": request.data.get("account_number"),
#                         "bank_name": request.data.get("bank_name"),
#                         "iban": request.data.get("iban"),
#                         "bank_branch": request.data.get("bank_branch"),
#                         "pf_number": request.data.get("pf_number"),
#                         "pan_number": request.data.get("pan_number"),
#                         "esic_number": request.data.get("esic_number"),
#                         "uan_number": request.data.get("uan_number"),
#                         "ifsc_code": request.data.get("ifsc_code"),
#                         "swift_code": request.data.get("swift_code"),
#                     }

#                 elif type == 4:
#                     field_map = {
#                         "contact_full_name": request.data.get("contact_full_name"),
#                         "contact_phone_no": request.data.get("contact_phone_no"),
#                         "contact_email": request.data.get("contact_email"),
#                         "contact_address": request.data.get("contact_address"),
#                     }

#                 elif type == 6:
#                     field_map = {
#                         "passport_no": request.data.get("passport_no"),
#                         "vehicle_no": request.data.get("vehicle_no"),"aadhar_no": request.data.get("aadhar_no"),
#                         "driving_licence_no": request.data.get("driving_licence_no"),
#                     }

#                 # Filter out None values (i.e., not provided by frontend)
#                 update_fields = []
#                 values = []

#                 for field, val in field_map.items():
#                     if val is not None:
#                         update_fields.append(f"{field} = %s")
#                         values.append(val)

#                 if not update_fields:
#                     return Response(
#                         {
#                             "status": "error",
#                             "message": "No valid data provided to update.",
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 # Final query
#                 query = f"""
#                     UPDATE ci_erp_users_details
#                     SET {', '.join(update_fields)}
#                     WHERE user_id = %s
#                 """
#                 values.append(user_id)

#                 c.execute(query, values)

#             return Response(
#                 {
#                     "status": "success",
#                     "message": "Personal details updated successfully.",
#                     "map": field_map
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


# class PersonalInformation(AdminOnlyView):
 
#     def post(self, request):
#         return self._get_personal_details(request)
 
#     def patch(self, request):
#         return self._update_personal_details(request)
 
#     def _get_personal_details(self, request):
 
#         user_id = request.data.get("user_id")
#         type = int(request.data.get("type", 0))
 
#         if not type or not user_id:
#             return Response(
#                 {"status": "error", "message": "type or user_id is missing"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
 
#         try:
#             with connection.cursor() as c:
 
#                 personal_details = {}
#                 if type == 1:
 
#                     query = """select bio,experience,education_level,degree_name
#                                 from ci_erp_users_details
#                                 where user_id = %s;"""
 
#                     c.execute(query, [user_id])
 
#                     columns = [col[0] for col in c.description]
#                     row = c.fetchone()
#                     if row:
#                         columns = [col[0] for col in c.description]
#                         personal_details = dict(zip(columns, row))
 
#                 elif type == 2:
 
#                     query = """select fb_profile,twitter_profile,gplus_profile,linkedin_profile
#                                 from ci_erp_users_details 
#                                 where user_id = %s;"""
 
#                     c.execute(query, [user_id])
 
#                     columns = [col[0] for col in c.description]
#                     row = c.fetchone()
#                     if row:
#                         columns = [col[0] for col in c.description]
#                         personal_details = dict(zip(columns, row))
 
#                 elif type == 3:

#                     query = """select bank_account_number,bank_code
#                                 from ci_erp_users_details 
#                                 where user_id = %s;"""
 
#                     c.execute(query, [user_id])
 
#                     columns = [col[0] for col in c.description]
#                     row = c.fetchone()
#                     if row:
#                         columns = [col[0] for col in c.description]
#                         personal_details = dict(zip(columns, row))
 
#                 elif type == 4:
 
#                     query = """select contact_full_name,contact_phone_no,contact_phone_no_2,contact_email,contact_address
#                                 from ci_erp_users_details 
#                                 where user_id = %s;"""
 
#                     c.execute(query, [user_id])
 
#                     columns = [col[0] for col in c.description]
#                     row = c.fetchone()
#                     if row:
#                         columns = [col[0] for col in c.description]
#                         personal_details = dict(zip(columns, row))
 
#                 elif type == 5:
 
#                     query = """select epf_number,socso_number,eis_category,income_tax_number,zakat_region,employee_category
#                                 from ci_erp_users_details
#                                 where user_id = %s;"""
 
#                     c.execute(query, [user_id])
 
#                     columns = [col[0] for col in c.description]
#                     row = c.fetchone()
#                     if row:
#                         columns = [col[0] for col in c.description]
#                         personal_details = dict(zip(columns, row))
 
#                 elif type == 6:
 
#                     query = """select nric_number,passport_number,passport_expiry_date
#                                 from ci_erp_users_details
#                                 where user_id = %s;"""
 
#                     c.execute(query, [user_id])
 
#                     columns = [col[0] for col in c.description]
#                     row = c.fetchone()
#                     if row:
#                         columns = [col[0] for col in c.description]
#                         personal_details = dict(zip(columns, row))
 
#             return Response(
#                 {"status": "success", "personal_details": personal_details},
#                 status=status.HTTP_200_OK,
#             )
 
#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )
 
 
#     def _update_personal_details(self, request):
 
#         user_id = request.data.get("user_id")
#         type = int(request.data.get("type", 0))
 
#         if not type or not user_id:
#             return Response(
#                 {"status": "error", "message": "type or user_id is missing"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
 
#         try:
#             with connection.cursor() as c:
 
#                 field_map = {}
 
#                 if type == 1:
#                     field_map = {
#                         "bio": request.data.get("bio"),
#                         "experience": request.data.get("experience"),
#                         "education_level": request.data.get("education_level"),
#                         "degree_name": request.data.get("degree_name"),
#                     }
 
#                 elif type == 2:
#                     field_map = {
#                         "fb_profile": request.data.get("fb_profile"),
#                         "twitter_profile": request.data.get("twitter_profile"),
#                         "gplus_profile": request.data.get("gplus_profile"),
#                         "linkedin_profile": request.data.get("linkedin_profile"),
#                     }
 
#                 elif type == 3:
#                     field_map = {
#                         "account_title": request.data.get("account_title"),
#                         "account_number": request.data.get("account_number"),
#                         "bank_name": request.data.get("bank_name"),
#                         # "iban": request.data.get("iban"),
#                         "bank_branch": request.data.get("bank_branch"),
#                         "uan_number": request.data.get("uan_number"),
#                         "ifsc_code": request.data.get("ifsc_code"),
#                         "swift_code": request.data.get("swift_code"),
#                     }
 
#                 elif type == 4:
#                     field_map = {
#                         "contact_full_name": request.data.get("contact_full_name"),
#                         "contact_phone_no": request.data.get("contact_phone_no"),
#                         "contact_phone_no_2": request.data.get("contact_phone_no_2"),
#                         "contact_email": request.data.get("contact_email"),
#                         "contact_address": request.data.get("contact_address"),
#                     }
 
#                 elif type == 5:
#                     field_map = {
#                         "aadhar_no": request.data.get("aadhar_number"),
#                         "driving_licence_no": request.data.get("driving_licence_number"),
#                         "pf_number": request.data.get("pf_number"),
#                         "pan_number": request.data.get("pan_number"),
#                         "esic_number": request.data.get("esic_number"),
#                         "passport_no": request.data.get("passport_number"),
#                         "vehicle_no": request.data.get("vehicle_number"),
#                         "uan_number": request.data.get("uan_number"),
#                     }
 
#                 elif type == 6:
#                     field_map = {
#                         "police_station_address": request.data.get("police_station_address"),
#                         "police_station_country": request.data.get("police_station_country"),
#                         "police_station_state": request.data.get("police_station_state"),
#                         "police_station_district": request.data.get("police_station_district"),
#                         "police_station_village": request.data.get("police_station_village"),
#                         "police_station_pincode": request.data.get("police_station_pincode"),
#                     }
 
#                 # Filter out None values (i.e., not provided by frontend)
#                 update_fields = []
#                 values = []
 
#                 for field, val in field_map.items():
#                     if val is not None:
#                         update_fields.append(f"{field} = %s")
#                         values.append(val)
 
#                 if not update_fields:
#                     return Response(
#                         {
#                             "status": "error",
#                             "message": "No valid data provided to update.",
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )
 
#                 # Final query
#                 query = f"""
#                     UPDATE ci_erp_users_details
#                     SET {', '.join(update_fields)}
#                     WHERE user_id = %s
#                 """
#                 values.append(user_id)
 
#                 c.execute(query, values)
 
#             return Response(
#                 {
#                     "status": "success",
#                     "message": "Personal details updated successfully.",
#                     "map": field_map
#                 },
#                 status=status.HTTP_200_OK,
#             )
 
#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


from rest_framework.response import Response
from rest_framework import status
from django.db import connection


class PersonalInformation(AdminOnlyView):

    def post(self, request):
        return self._get_personal_details(request)

    def patch(self, request):
        return self._update_personal_details(request)

    # ==============================
    # GET PERSONAL DETAILS
    # ==============================
    def _get_personal_details(self, request):

        user_id = request.data.get("user_id")
        type = int(request.data.get("type", 0))

        if not type or not user_id:
            return Response(
                {"status": "error", "message": "type or user_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:

                personal_details = {}

                if type == 1:
                    query = """
                        SELECT bio, experience, education_level, degree_name
                        FROM ci_erp_users_details
                        WHERE user_id = %s
                    """

                elif type == 2:
                    query = """
                        SELECT fb_profile, twitter_profile, gplus_profile, linkedin_profile
                        FROM ci_erp_users_details
                        WHERE user_id = %s
                    """

                elif type == 3:
                    query = """
                        SELECT bank_account_number, bank_code
                        FROM ci_erp_users_details
                        WHERE user_id = %s
                    """

                elif type == 4:
                    query = """
                        SELECT contact_full_name, contact_phone_no, contact_phone_no_2,
                               contact_email, contact_address
                        FROM ci_erp_users_details
                        WHERE user_id = %s
                    """

                elif type == 5:
                    query = """
                        SELECT epf_number, socso_number, eis_category,
                               income_tax_number, zakat_region, employee_category
                        FROM ci_erp_users_details
                        WHERE user_id = %s
                    """

                elif type == 6:
                    query = """
                        SELECT nric_number, passport_number, passport_expiry_date
                        FROM ci_erp_users_details
                        WHERE user_id = %s
                    """

                else:
                    return Response(
                        {"status": "error", "message": "Invalid type"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                c.execute(query, [user_id])
                row = c.fetchone()

                if row:
                    columns = [col[0] for col in c.description]
                    personal_details = dict(zip(columns, row))

            return Response(
                {"status": "success", "personal_details": personal_details},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ==============================
    # UPDATE PERSONAL DETAILS
    # ==============================
    def _update_personal_details(self, request):

        user_id = request.data.get("user_id")
        type = int(request.data.get("type", 0))

        if not type or not user_id:
            return Response(
                {"status": "error", "message": "type or user_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:

                if type == 1:
                    field_map = {
                        "bio": request.data.get("bio"),
                        "experience": request.data.get("experience"),
                        "education_level": request.data.get("education_level"),
                        "degree_name": request.data.get("degree_name"),
                    }

                elif type == 2:
                    field_map = {
                        "fb_profile": request.data.get("fb_profile"),
                        "twitter_profile": request.data.get("twitter_profile"),
                        "gplus_profile": request.data.get("gplus_profile"),
                        "linkedin_profile": request.data.get("linkedin_profile"),
                    }

                elif type == 3:
                    field_map = {
                        "bank_account_number": request.data.get("bank_account_number"),
                        "bank_code": request.data.get("bank_code"),
                    }

                elif type == 4:
                    field_map = {
                        "contact_full_name": request.data.get("contact_full_name"),
                        "contact_phone_no": request.data.get("contact_phone_no"),
                        "contact_phone_no_2": request.data.get("contact_phone_no_2"),
                        "contact_email": request.data.get("contact_email"),
                        "contact_address": request.data.get("contact_address"),
                    }

                elif type == 5:
                    field_map = {
                        "epf_number": request.data.get("epf_number"),
                        "socso_number": request.data.get("socso_number"),
                        "eis_category": request.data.get("eis_category"),
                        "income_tax_number": request.data.get("income_tax_number"),
                        "zakat_region": request.data.get("zakat_region"),
                        "employee_category": request.data.get("employee_category"),
                    }

                elif type == 6:
                    field_map = {
                        "nric_number": request.data.get("nric_number"),
                        "passport_number": request.data.get("passport_number"),
                        "passport_expiry_date": request.data.get("passport_expiry_date"),
                    }

                else:
                    return Response(
                        {"status": "error", "message": "Invalid type"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                update_fields = []
                values = []

                for field, val in field_map.items():
                    if val is not None:
                        update_fields.append(f"{field} = %s")
                        values.append(val)

                if not update_fields:
                    return Response(
                        {"status": "error", "message": "No valid data provided to update"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                query = f"""
                    UPDATE ci_erp_users_details
                    SET {', '.join(update_fields)}
                    WHERE user_id = %s
                """
                values.append(user_id)

                c.execute(query, values)

            return Response(
                {
                    "status": "success",
                    "message": "Personal details updated successfully",
                    "updated_fields": list(field_map.keys())
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )




# class GetProfilePhoto(APIView):

#     def get(self, request, employee_id):

#         if not employee_id:
#             return Response({"status":"error","message":"employee_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             with connection.cursor() as c:
#                 c.execute("""select profile_photo from ci_erp_users u inner join ci_erp_users_details ud on u.id = ud.user_id where employee_id = %s""", [employee_id])

#                 result = c.fetchone()
                
#                 # Check if user exists
#                 if not result:
#                     return Response(
#                         {"status": "error", "message": "Employee not found"}, 
#                         status=status.HTTP_404_NOT_FOUND
#                     )
                
#                 profile_photo = result[0]
                
#                 # Handle profile photo URL construction
#                 if profile_photo:
#                     # Handle bytes data
#                     if isinstance(profile_photo, bytes):
#                         photo_str = profile_photo.decode('utf-8')
#                     else:
#                         photo_str = str(profile_photo)
                    
#                     # Build absolute URI
#                     pf_photo = request.build_absolute_uri(
#                         f"/hrms-backend/media/documents/{quote(photo_str)}"
#                     )
#                 else:
#                     pf_photo = None

#             return Response(
#                 {"status": "success", "data": pf_photo}, 
#                 status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             return Response({"status":"error","message": f"An error occured: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR   )

# class UpdateProfilePhoto(AdminOnlyView):

#     def post(self, request):

#         user_id = request.data.get("user_id")
#         file = request.FILES["file"]

#         if not user_id or not file:
#             return Response(
#                 {"status": "error", "message": "user_id or file is missing"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             with connection.cursor() as c:
#                 c.execute(
#                     """select first_name,last_name from ci_erp_users where id = %s""",
#                     [user_id],
#                 )

#                 row = c.fetchone()
#                 first_name = row[0]
#                 last_name = row[1]

#                 file_name = file.name
#                 file_extension = file_name.split(".")[-1].lower()

#                 new_file_name = None
#                 if file:
#                     file_name = file.name
#                     file_extension = file_name.split(".")[-1].lower()

#                     if file_extension not in ["jpg", "jpeg", "png"]:
#                         return Response(
#                             {
#                                 "status": "error",
#                                 "message": "Invalid file format. Please upload JPG, JPEG, or PNG.",
#                             },
#                             status=status.HTTP_400_BAD_REQUEST,
#                         )

#                     upload_dir = os.path.join(settings.MEDIA_ROOT, "documents")
#                     os.makedirs(upload_dir, exist_ok=True)
#                     new_file_name = (
#                         f"{user_id}_{first_name}_{last_name}.{file_extension}"
#                     )
#                     destination_path = os.path.join(upload_dir, new_file_name)

#                     with default_storage.open(destination_path, "wb+") as destination:
#                         for chunk in file.chunks():
#                             destination.write(chunk)

#             return Response(
#                 {"status": "success", "message": "profile photo updated successfully"},
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

class GetProfilePhoto(APIView):

    def get(self, request, employee_id):
        if not employee_id:
            return Response(
                {"status": "error", "message": "employee_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:
                c.execute(
                    """
                    SELECT profile_photo
                    FROM ci_erp_users u
                    INNER JOIN ci_erp_users_details ud ON u.id = ud.user_id
                    WHERE employee_id = %s
                    """,
                    [employee_id],
                )

                result = c.fetchone()

                if not result:
                    return Response(
                        {"status": "error", "message": "Employee not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                profile_photo = result[0]
                pf_photo = None

                # if profile_photo:
                #     # Convert from bytes if necessary
                #     if isinstance(profile_photo, bytes):
                #         photo_str = profile_photo.decode("utf-8")
                #     else:
                #         photo_str = str(profile_photo)

                #     # Case 1: Already a full URL
                #     if photo_str.startswith("http"):
                #         pf_photo = photo_str.replace(
                #             "/media/", "/hrms-backend/media/"
                #         )

                #     # Case 2: Already starts with documents/ or profile_pictures/
                #     elif photo_str.startswith("documents/") or photo_str.startswith(
                #         "profile_pictures/"
                #     ):
                #         pf_photo = f"{settings.SITE_URL}/hrms-backend/media/{quote(photo_str)}"

                #     # Case 3: Only filename → check documents first, then profile_pictures
                #     else:
                #         file_name = photo_str.split("/")[-1]

                #         doc_path = os.path.join(
                #             settings.MEDIA_ROOT, "documents", file_name
                #         )
                #         pic_path = os.path.join(
                #             settings.MEDIA_ROOT, "profile_pictures", file_name
                #         )

                #         if os.path.exists(doc_path):
                #             pf_photo = f"{settings.SITE_URL}/hrms-backend/media/documents/{quote(file_name)}"
                #         elif os.path.exists(pic_path):
                #             pf_photo = f"{settings.SITE_URL}/hrms-backend/media/profile_pictures/{quote(file_name)}"
                # pf_photo = f"https://tdtlworld.com/hrms-backend/{profile_photo}"
                pf_photo = f"https://tdtlworld.com/hrms-backend/{quote(profile_photo)}"
                
            return Response(
                {"status": "success", "data": pf_photo},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
 


class UpdateProfilePhoto(AdminOnlyView):

    def post(self, request):

        user_id = request.data.get("user_id")
        file = request.FILES.get("file")

        if not user_id or not file:
            return Response(
                {"status": "error", "message": "user_id or file is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:
                # Get first name and last name for naming
                c.execute(
                    """SELECT first_name, last_name FROM ci_erp_users WHERE id = %s""",
                    [user_id],
                )
                row = c.fetchone()
                if not row:
                    return Response(
                        {"status": "error", "message": "User not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )

                first_name, last_name = row[0], row[1]

                # Validate file extension
                file_extension = file.name.split(".")[-1].lower()
                if file_extension not in ["jpg", "jpeg", "png"]:
                    return Response(
                        {
                            "status": "error",
                            "message": "Invalid file format. Please upload JPG, JPEG, or PNG.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Prepare upload directory
                upload_dir = os.path.join(settings.MEDIA_ROOT, "documents")
                os.makedirs(upload_dir, exist_ok=True)

                # Create new file name
                new_file_name = f"{user_id}_{first_name}_{last_name}.{file_extension}"
                destination_path = os.path.join(upload_dir, new_file_name)

                # Save file to disk
                with open(destination_path, "wb+") as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                # Store relative path in DB (e.g. "documents/494_Ambika_Mitkari.jpeg")
                # relative_path = f"documents/{new_file_name}"
                relative_path = f"media/documents/{new_file_name}"
                c.execute(
                    """
                    UPDATE ci_erp_users
                    SET profile_photo = %s
                    WHERE id = %s
                    """,
                    [relative_path, user_id]
                )

            return Response(
                {
                    "status": "success",
                    "message": "Profile photo updated successfully",
                    "file_path": relative_path
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
 

class AccountInformation(AdminOnlyView):

    def post(self, request):
        return self._get_account_details(request)

    def patch(self, request):
        return self._update_account_details(request)

    def _get_account_details(self, request):

        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"status": "error", "message": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:

                query = """select username,email from ci_erp_users where id = %s"""
                c.execute(query, [user_id])

                row = c.fetchone()
                columns = [col[0] for col in c.description]

                if row:
                    response = dict(zip(columns, row))
                else:
                    response = {}

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _update_account_details(self, request):
        user_id = request.data.get("user_id")
        username = request.data.get("username")
        email = request.data.get("email")

        if not user_id or not username or not email:
            return Response(
                {
                    "status": "error",
                    "message": "user_id, username, and email are required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:
                query = """
                    UPDATE ci_erp_users
                    SET username = %s, email = %s
                    WHERE id = %s
                """
                c.execute(query, [username, email, user_id])

            return Response(
                {
                    "status": "success",
                    "message": "Account details updated successfully",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DocumentDetails(AdminOnlyView):

    def get(self, request):
        return self._get_document_details(request)

    def patch(self, request):
        return self._update_document_details(request)

    def post(self, request):
        return self._add_document_details(request)

    def delete(self, request):
        return self._delete_document_details(request)

    # def _get_document_details(self, request):

    #     user_id = request.GET.get("user_id")

    #     if not user_id:
    #         return Response(
    #             {"status": "error", "message": "user_id is required"},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )

    #     try:
    #         with connection.cursor() as c:

    #             c.execute(
    #                 "SELECT document_id,document_name,document_type,document_file FROM ci_users_documents WHERE user_id = %s",
    #                 [user_id],
    #             )
    #             kyc_docs = c.fetchall()

    #             kyc_documents = []
    #             for doc in kyc_docs:
    #                 file_name = doc[1]
    #                 file_extension = file_name.split(".")[-1].lower()
    #                 file_url = f"/hrms-backend/media/user_document/{quote(file_name)}"

    #                 kyc_documents.append(
    #                     {
    #                         "document_id": doc[0],
    #                         "document_name": file_name,
    #                         "document_type": file_extension,
    #                         "document_file": file_url,
    #                     }
    #                 )
    #         return Response(
    #             {"status": "success", "docs": kyc_documents}, status=status.HTTP_200_OK
    #         )

    #     except Exception as e:
    #         return Response(
    #             {"status": "error", "message": f"An error occurred: {str(e)}"},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         )


    def _get_document_details(self, request):
        user_id = request.GET.get("user_id")

        if not user_id:
            return Response(
                {"status": "error", "message": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:
                # Get user's email
                c.execute(
                    "SELECT email FROM ci_erp_users WHERE id = %s",
                    [user_id],
                )
                user_row = c.fetchone()
                if not user_row:
                    return Response(
                        {"status": "error", "message": "User not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                user_email = user_row[0]

                # Get documents
                c.execute(
                    "SELECT document_id, document_name, document_type, document_file "
                    "FROM ci_users_documents WHERE user_id = %s",
                    [user_id],
                )
                kyc_docs = c.fetchall()

                kyc_documents = []
                for doc in kyc_docs:
                    file_name = doc[1]
                    file_extension = file_name.split(".")[-1].lower()
                    file_url = f"tdtlworld.com/hrms-backend/media/user_document/{quote(file_name)}"

                    kyc_documents.append(
                        {
                            "document_id": doc[0],
                            "document_name": file_name,
                            "document_type": file_extension,
                            "document_file": file_url,
                        }
                    )

            return Response(
                {
                    "status": "success",
                    "email": user_email,
                    "docs": kyc_documents
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
    def _add_document_details(self, request):
        user_id = request.data.get("user_id")
        company_id = request.data.get("company_id", 2)
        document_name = request.data.get("document_name")
        document_type = request.data.get("document_type")
        document_file = request.FILES.get("document_file")

        if not user_id or not document_name or not document_type or not document_file:
            return Response(
                {
                    "status": "error",
                    "message": "some fields are missing",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:
                c.execute(
                    "SELECT first_name, last_name FROM ci_erp_users WHERE id = %s",
                    [user_id],
                )
                row = c.fetchone()

                if not row:
                    return Response(
                        {"status": "error", "message": "User not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                first_name, last_name = row
                file_name = document_file.name
                file_extension = file_name.split(".")[-1].lower()

                if file_extension not in [
                    "jpg",
                    "jpeg",
                    "png",
                    "txt",
                    "pdf",
                    "xls",
                    "xlsx",
                    "doc",
                    "docx",
                ]:
                    return Response(
                        {"status": "error", "message": "Invalid file format"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                upload_dir = os.path.join(settings.MEDIA_ROOT, "user_document")
                os.makedirs(upload_dir, exist_ok=True)

                clean_document_name = re.sub(r"\s+", "_", document_name.strip())
                clean_document_name = re.sub(r"[^\w\-\.]", "", clean_document_name)

                new_file_name = f"{user_id}_{first_name}_{last_name}_{clean_document_name}.{file_extension}"
                destination_path = os.path.join(upload_dir, new_file_name)

                with default_storage.open(destination_path, "wb+") as destination:
                    for chunk in document_file.chunks():
                        destination.write(chunk)

                relative_file_path = f"/hrms-backend/media/user_document/{new_file_name}"

                c.execute(
                    """
                    INSERT INTO ci_users_documents (company_id, user_id, document_name, document_type, document_file)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    [
                        company_id,
                        user_id,
                        new_file_name,
                        document_type,
                        relative_file_path,
                    ],
                )

            return Response(
                {"status": "success", "message": "Document added successfully"},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _update_document_details(self, request):
        # document_id = request.data.get("document_id")
        # user_id = request.data.get("user_id")
        # document_file = request.FILES.get("document_file")
        # document_name = request.data.get("document_name")
        # document_type = request.data.get("document_type")

        # if (
        #     not document_id
        #     or not document_name
        #     or not document_type
        #     or not document_file
        #     or not user_id
        # ):
        #     return Response(
        #         {
        #             "status": "error",
        #             "message": "some fields are missing",
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # try:
        #     with connection.cursor() as c:

        #         c.execute(
        #             "SELECT user_id FROM ci_users_documents WHERE document_id = %s",
        #             [document_id],
        #         )
        #         row = c.fetchone()
        #         if not row:
        #             return Response(
        #                 {"status": "error", "message": "Document not found."},
        #                 status=status.HTTP_404_NOT_FOUND,
        #             )

        #         user_id = row[0]

        #         # Fetch user info
        #         c.execute(
        #             "SELECT first_name, last_name FROM ci_erp_users WHERE id = %s",
        #             [user_id],
        #         )
        #         row = c.fetchone()
        #         if not row:
        #             return Response(
        #                 {"status": "error", "message": "User not found"},
        #                 status=status.HTTP_404_NOT_FOUND,
        #             )

        #         first_name, last_name = row
        #         file_name = document_file.name
        #         file_extension = file_name.split(".")[-1].lower()

        #         if file_extension not in [
        #             "jpg",
        #             "jpeg",
        #             "png",
        #             "txt",
        #             "pdf",
        #             "xls",
        #             "xlsx",
        #             "doc",
        #             "docx",
        #         ]:
        #             return Response(
        #                 {"status": "error", "message": "Invalid file format"},
        #                 status=status.HTTP_400_BAD_REQUEST,
        #             )

        #         upload_dir = os.path.join(settings.MEDIA_ROOT, "user_document")
        #         os.makedirs(upload_dir, exist_ok=True)

        #         clean_document_name = re.sub(r"\s+", "_", document_name.strip())
        #         clean_document_name = re.sub(r"[^\w\-\.]", "", clean_document_name)

        #         new_file_name = f"{user_id}_{first_name}_{last_name}_{clean_document_name}.{file_extension}"
        #         destination_path = os.path.join(upload_dir, new_file_name)

        #         with default_storage.open(destination_path, "wb+") as destination:
        #             for chunk in document_file.chunks():
        #                 destination.write(chunk)

        #         relative_file_path = f"/hrms-backend/media/user_document/{new_file_name}"

        #         # Update document
        #         c.execute(
        #             """UPDATE ci_users_documents
        #            SET company_id = %s, document_name = %s, document_type = %s, document_file = %s
        #            WHERE document_id = %s""",
        #             [2, new_file_name, document_type, relative_file_path, document_id],
        #         )

        #     return Response(
        #         {"status": "success", "message": "Document updated successfully"},
        #         status=status.HTTP_200_OK,
        #     )

        # except Exception as e:
        #     return Response(
        #         {"status": "error", "message": f"An error occurred: {str(e)}"},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     )

        document_id = request.data.get("document_id")
        user_id = request.data.get("user_id")
        document_file = request.FILES.get("document_file")

        if not document_id or not user_id:
            return Response(
                {"status": "error", "message": "document_id or user_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:
                # Verify document exists
                c.execute(
                    "SELECT user_id FROM ci_users_documents WHERE document_id = %s",
                    [document_id],
                )
                row = c.fetchone()
                if not row:
                    return Response(
                        {"status": "error", "message": "Document not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # Fetch user info
                c.execute(
                    "SELECT first_name, last_name FROM ci_erp_users WHERE id = %s",
                    [user_id],
                )
                row = c.fetchone()
                if not row:
                    return Response(
                        {"status": "error", "message": "User not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                first_name, last_name = row
                update_fields = []
                values = []

                # Optional fields
                if "document_name" in request.data:
                    document_name = request.data["document_name"]
                    update_fields.append("document_name = %s")
                    values.append(document_name)
                if "document_type" in request.data:
                    document_type = request.data["document_type"]
                    update_fields.append("document_type = %s")
                    values.append(document_type)

                if document_file:
                    file_name = document_file.name
                    file_extension = file_name.split(".")[-1].lower()

                    if file_extension not in [
                        "jpg",
                        "jpeg",
                        "png",
                        "txt",
                        "pdf",
                        "xls",
                        "xlsx",
                        "doc",
                        "docx",
                    ]:
                        return Response(
                            {"status": "error", "message": "Invalid file format"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    upload_dir = os.path.join(settings.MEDIA_ROOT, "user_document")
                    os.makedirs(upload_dir, exist_ok=True)

                    clean_document_name = re.sub(
                        r"\s+",
                        "_",
                        request.data.get("document_name", "document").strip(),
                    )
                    clean_document_name = re.sub(r"[^\w\-\.]", "", clean_document_name)
                    new_file_name = f"{user_id}_{first_name}_{last_name}_{clean_document_name}.{file_extension}"
                    destination_path = os.path.join(upload_dir, new_file_name)

                    with default_storage.open(destination_path, "wb+") as destination:
                        for chunk in document_file.chunks():
                            destination.write(chunk)

                    relative_file_path = f"/hrms-backend/media/user_document/{new_file_name}"
                    update_fields.append("document_file = %s")
                    values.append(relative_file_path)

                if not update_fields:
                    return Response(
                        {"status": "error", "message": "No fields to update"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                values.append(document_id)
                update_query = f"""
                    UPDATE ci_users_documents
                    SET {', '.join(update_fields)}
                    WHERE document_id = %s
                """

                c.execute(update_query, values)

            return Response(
                {"status": "success", "message": "Document updated successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _delete_document_details(self, request):

        document_id = request.data.get("document_id")

        if not document_id:
            return Response(
                {"status": "error", "message": "document_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                with connection.cursor() as c:

                    c.execute(
                        """delete from ci_users_documents where document_id = %s""",
                        [document_id],
                    )

            return Response(
                {"status": "success", "message": "Document deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChangePassword(AdminOnlyView):

    def get(self, request):
        return self._get_password(request)

    def patch(self, request):
        return self._get_password(request)

    def _get_password(self, request):

        user_id = request.GET.get("user_id")

        if not user_id:
            return Response(
                {"status": "error", "message": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:
                c.execute(
                    """select password from ci_erp_users where id = %s""", [user_id]
                )

                row = c.fetchone()
                current_pass = row[0]

            return Response(
                {"status": "success", "current_password": current_pass},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request):
        user_id = request.data.get("user_id")
        new_password = request.data.get("new_password")

        if not user_id or not new_password:
            return Response(
                {"status": "error", "message": "user_id and new_password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Hash the new password
            hashed_password = bcrypt.hashpw(
                new_password.encode("utf-8"), bcrypt.gensalt()
            )
            hashed_password = hashed_password.decode(
                "utf-8"
            )  # Convert bytes to string for DB storage

            with connection.cursor() as c:
                c.execute(
                    """UPDATE ci_erp_users SET password = %s WHERE id = %s""",
                    [hashed_password, user_id],
                )

            return Response(
                {"status": "success", "message": "Password updated successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TimesheetAgenda(AdminOnlyView):

    def post(self, request):
        return self._get_timesheet_details(request)

    def patch(self, request):
        return self._update_timesheet_details(request)

    def _get_timesheet_details(self, request):

        user_id = request.data.get("user_id")
        type = int(request.data.get("type", 0))

        if not user_id or not type:
            return Response(
                {"status": "error", "message": "user_id or type is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:

                timesheet_details = {}
                if type == 1:  # Leave Request

                    query = """select concat(first_name,' ',last_name) as employee,u.email,ec.category_name as leave_type,date_format(la.from_date, '%%d-%%m-%%Y')as from_date,date_format(la.to_date, '%%d-%%m-%%Y') as to_date,is_half_day,la.created_at,la.status,la.remarks,la.leave_attachment,la.leave_id from ci_erp_users u left join ci_leave_applications la on u.id = la.employee_id left join ci_erp_constants ec on la.leave_type_id = ec.constants_id and type = 'leave_type' where u.id = %s;"""
                    c.execute(query, [user_id])

                    columns = [col[0] for col in c.description]
                    timesheet_details = [
                        dict(zip(columns, rows)) for rows in c.fetchall()
                    ]

                elif type == 2:  # Expense Claim

                    query = """select account_name,fe.name as payee,amount,ecc.category_name as category,reference,ecp.category_name as payment_method,ft.created_at
                    from ci_finance_transactions ft left join ci_finance_accounts fa on ft.account_id = fa.account_id left join ci_erp_constants ecp on ft.payment_method_id = ecp.constants_id and ecp.type = 'payment_method' left join ci_erp_constants ecc on ft.entity_category_id = ecc.constants_id and ecc.type = 'expense_type' left join ci_finance_entity fe on ft.entity_id = fe.entity_id
                    where ft.staff_id = %s;"""
                    c.execute(query, [user_id])

                    columns = [col[0] for col in c.description]
                    timesheet_details = [
                        dict(zip(columns, rows)) for rows in c.fetchall()
                    ]

                elif type == 3:  # Request Loan

                    query = """select * from ci_payroll_allowance_dedcution where employee_id = %s"""
                    c.execute(query, [user_id])

                    columns = [col[0] for col in c.description]
                    timesheet_details = [
                        dict(zip(columns, rows)) for rows in c.fetchall()
                    ]

                elif type == 4:  # Travel Request

                    query = """select concat(first_name,' ',last_name) as employee, visit_place as place_of_visit,visit_purpose as purpose_of_visit,arrangement_type,actual_budget,DATE_FORMAT(end_date, '%%d-%%m-%%Y') as end_date
                    from ci_travels t left join ci_erp_users eu on t.employee_id = eu.id
                    where eu.id = %s;"""
                    c.execute(query, [user_id])

                    columns = [col[0] for col in c.description]
                    timesheet_details = [
                        dict(zip(columns, rows)) for rows in c.fetchall()
                    ]

                elif type == 5:  # Advance Salary

                    query = """select concat(first_name,' ',last_name) as employee,advance_amount as amount,month_year,one_time_deduct,total_paid as emi,DATE_FORMAT(ads.created_at, '%%d-%%m-%%Y')as created_at
                    from ci_advance_salary ads left join ci_erp_users eu on ads.employee_id = eu.id
                    where eu.id = %s;"""
                    c.execute(query, [user_id])

                    columns = [col[0] for col in c.description]
                    timesheet_details = [
                        dict(zip(columns, rows)) for rows in c.fetchall()
                    ]

                elif type == 6:  # Overtime Request

                    query = """select concat(first_name,' ',last_name) as employee,attendance_date as date,clock_in as in_time,clock_out as out_time,total_work as total_hours, attendance_status
                    from ci_timesheet t left join ci_erp_users eu on t.employee_id = eu.id
                    where eu.id = %s;"""
                    c.execute(query, [user_id])

                    columns = [col[0] for col in c.description]
                    timesheet_details = [
                        dict(zip(columns, rows)) for rows in c.fetchall()
                    ]

                elif type == 7:  # Awards

                    query = """select ec.category_name as award_type, concat(first_name,' ',last_name) as employee, gift_item as award_gift,cash_price as award_cash,award_month_year as month_year
                    from ci_awards ad left join ci_erp_users eu on ad.employee_id = eu.id left join ci_erp_constants ec on ad.award_type_id = ec.constants_id and ec.type = 'award_type'
                    where eu.id = %s;"""
                    c.execute(query, [user_id])

                    columns = [col[0] for col in c.description]
                    timesheet_details = [
                        dict(zip(columns, rows)) for rows in c.fetchall()
                    ]

                elif type == 8:  # Projects

                    query = """SELECT 
                                    p.project_id,
                                    p.title as projects,
                                    p.client_id,
                                    DATE_FORMAT(p.start_date, '%%d-%%m-%%Y') as start_date,
                                    DATE_FORMAT(p.end_date, '%%d-%%m-%%Y') as end_date,
                                    GROUP_CONCAT(CONCAT(u.first_name, ' ', u.last_name)) AS team_name,
                                    priority,
                                    project_progress
                                FROM
                                    ci_projects p
                                        LEFT JOIN
                                    ci_erp_users u ON FIND_IN_SET(u.id,
                                            REPLACE(REPLACE(REPLACE(p.assigned_to, '[', ''),
                                                    ']',
                                                    ''),
                                                ' ',
                                                ''))
                                        LEFT JOIN
                                    ci_erp_users c ON c.id = p.client_id
                                WHERE
                                    FIND_IN_SET(%s,
                                            REPLACE(REPLACE(REPLACE(p.assigned_to, '[', ''),
                                                    ']',
                                                    ''),
                                                ' ',
                                                '')) > 0
                                GROUP BY p.project_id;"""
                    c.execute(query, [user_id])

                    columns = [col[0] for col in c.description]
                    timesheet_details = [
                        dict(zip(columns, rows)) for rows in c.fetchall()
                    ]

                elif type == 9:  # Tasks

                    query = """SELECT 
                                    p.project_id,
                                    t.task_id,
                                    t.task_name AS title,
                                    GROUP_CONCAT(CONCAT(u.first_name, ' ', u.last_name)) AS team_name,
                                    DATE_FORMAT(p.start_date, '%%d-%%m-%%Y') AS start_date,
                                    DATE_FORMAT(p.end_date, '%%d-%%m-%%Y') AS end_date,
                                    task_status
                                FROM
                                    ci_tasks t
                                        LEFT JOIN
                                    ci_projects p ON t.project_id = p.project_id
                                        LEFT JOIN
                                    ci_erp_users u ON FIND_IN_SET(u.id,
                                            REPLACE(REPLACE(REPLACE(p.assigned_to, '[', ''),
                                                    ']',
                                                    ''),
                                                ' ',
                                                ''))
                                        LEFT JOIN
                                    ci_erp_users c ON c.id = p.client_id
                                WHERE
                                    FIND_IN_SET(%s,
                                            REPLACE(REPLACE(REPLACE(p.assigned_to, '[', ''),
                                                    ']',
                                                    ''),
                                                ' ',
                                                '')) > 0
                                GROUP BY p.project_id;"""
                    c.execute(query, [user_id])

                    columns = [col[0] for col in c.description]
                    timesheet_details = [
                        dict(zip(columns, rows)) for rows in c.fetchall()
                    ]

                elif type == 10:  # Payslip History

                    query = """select concat(first_name,' ',last_name) as employee,net_salary as net_payable,salary_month,year_to_date as pay_date
                    from ci_payslips cp left join ci_erp_users u on cp.staff_id = u.id
                    where u.id = %s;"""
                    c.execute(query, [user_id])

                    columns = [col[0] for col in c.description]
                    timesheet_details = [
                        dict(zip(columns, rows)) for rows in c.fetchall()
                    ]

            return Response(
                {"status": "success", "timesheet_data": timesheet_details},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _update_timesheet_details(self, request):

        user_id = request.data.get("user_id")
        leave_id = request.data.get("leave_id")
        leave_status = request.data.get("leave_status")

        if not user_id or not leave_status or not leave_id:
            return Response(
                {
                    "status": "error",
                    "message": "user_id, leave_status or leave_id is missing",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:

                c.execute(
                    """update ci_leave_applications set status = %s where employee_id = %s and leave_id = %s""",
                    [leave_status, user_id, leave_id],
                )

            return Response(
                {
                    "status": "success",
                    "message": "leave status updated successfully",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LeaveStatistics(AdminOnlyView):

    def get(self, request):

        user_id = request.GET.get("user_id")

        if not user_id:
            return Response(
                {"status": "error", "message": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:

                query = """SELECT 
                                ec.category_name AS leave_type,
                                COUNT(*) AS leave_count
                            FROM 
                                ci_leave_applications la
                            LEFT JOIN 
                                ci_erp_constants ec ON la.leave_type_id = ec.constants_id AND ec.type = 'leave_type'
                            WHERE 
                                la.employee_id = %s
                            GROUP BY 
                                ec.category_name
                            ORDER BY
                                ec.constants_id;"""

                c.execute(query, [user_id])

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, rows)) for rows in c.fetchall()]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class ViewEmployeeSalarySlip(APIView):

    @staticmethod
    def get_sundays_in_month(year, month):
        sundays = []
        total_days = calendar.monthrange(year, month)[1]
        for day in range(1, total_days + 1):
            current_date = date(year, month, day)
            if current_date.weekday() == 6:  # Sunday
                sundays.append(current_date)
        return sundays

    def safe_decimal(self, value, default="0.00"):
            try:
                if value is None or value == "" or value == "None":
                    return Decimal(default)
                return Decimal(str(value))
            except (InvalidOperation, ValueError, TypeError):
                return Decimal(default)

    def get_all_salary_changes_batch(self, employee_id, year, month):
        """
        Get salary changes for a single employee
        """
        if not employee_id:
            return {}
        
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT employee_id, previous_salary, current_salary, updated_at
                FROM ci_update_salary 
                WHERE employee_id = %s
                AND MONTH(updated_at) = %s 
                AND YEAR(updated_at) = %s
                ORDER BY updated_at ASC
                """,
                [employee_id, month, year]
            )
            
            salary_changes_raw = cursor.fetchall()
            
            # Group by employee_id (in this case, only one employee)
            salary_changes_by_employee = {}
            for emp_id, prev_salary, curr_salary, updated_at in salary_changes_raw:
                if emp_id not in salary_changes_by_employee:
                    salary_changes_by_employee[emp_id] = []
                salary_changes_by_employee[emp_id].append((prev_salary, curr_salary, updated_at))
            
            return salary_changes_by_employee

    def calculate_gross_earning_with_salary_changes_batch(self, employee_data, salary_changes_by_employee, year, month, days_in_month):
        """
        Calculate gross earning for a single employee considering mid-month salary changes
        """
        results = {}
        
        try:
            days_in_month_decimal = self.safe_decimal(days_in_month)
            
            emp_id, payable_days, current_salary = employee_data
            try:
                # Ensure all values are properly converted to Decimal
                current_salary = self.safe_decimal(current_salary)
                payable_days = self.safe_decimal(payable_days)
                salary_changes = salary_changes_by_employee.get(emp_id, [])
                
                if not salary_changes:
                    # No salary changes in this month, use current salary for entire month
                    if days_in_month_decimal > 0:
                        gross = (current_salary / days_in_month_decimal) * payable_days
                    else:
                        gross = self.safe_decimal("0.00")
                    
                    results[emp_id] = {
                        'gross_earning': gross,
                        'total_monthly_earning': current_salary
                    }
                    return results
                
                # Calculate total earnings based on daily rates for different periods
                total_earnings = self.safe_decimal("0.00")
                
                # Start with the first salary (before any changes)
                previous_day = 1
                current_month_salary = self.safe_decimal(salary_changes[0][0])  # previous_salary from first change
                
                for change in salary_changes:
                    try:
                        previous_salary, new_salary, updated_at = change
                        
                        # Ensure updated_at is not None and has day attribute
                        if not updated_at or not hasattr(updated_at, 'day'):
                            continue
                            
                        change_day = updated_at.day
                        
                        # Calculate days with previous salary (from previous_day to change_day-1)
                        days_with_current_salary = change_day - previous_day
                        if days_with_current_salary > 0 and days_in_month_decimal > 0:
                            daily_rate = current_month_salary / days_in_month_decimal
                            total_earnings += daily_rate * self.safe_decimal(days_with_current_salary)
                        
                        # Update for next iteration
                        current_month_salary = self.safe_decimal(new_salary)
                        previous_day = change_day
                        
                    except (AttributeError, TypeError, ValueError) as e:
                        # Skip this salary change if there's an error
                        continue
                
                # Add remaining days of the month with the last salary
                remaining_days = days_in_month - previous_day + 1
                if remaining_days > 0 and days_in_month_decimal > 0:
                    daily_rate = current_month_salary / days_in_month_decimal
                    total_earnings += daily_rate * self.safe_decimal(remaining_days)
                
                # Now calculate the proportional amount based on payable_days
                total_monthly_earnings = total_earnings
                if days_in_month_decimal > 0:
                    calculated_gross = (total_monthly_earnings / days_in_month_decimal) * payable_days
                else:
                    calculated_gross = self.safe_decimal("0.00")
                
                results[emp_id] = {
                    'gross_earning': calculated_gross,
                    'total_monthly_earning': total_monthly_earnings
                }
                
            except Exception as e:
                # If there's any error with this employee, set default values
                results[emp_id] = {
                    'gross_earning': self.safe_decimal("0.00"),
                    'total_monthly_earning': self.safe_decimal(current_salary) if current_salary else self.safe_decimal("0.00")
                }
        
        except Exception as e:
            print(f"Error in salary calculation: {e}")
            
        return results

    def get(self, request, employee_id):

        if not employee_id:
            return Response({"status":" error", "message": "employee_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            month = datetime.now().month
            year = datetime.now().year
            
            days_in_month = calendar.monthrange(year, month)[1]

            with connection.cursor() as cursor:

                # 1. Get Salary Structure (unchanged - this is small and fast)
                cursor.execute("SELECT particulars, value FROM ci_salary_structure")
                salary_structure_raw = cursor.fetchall()
                salary_structure = {k: self.safe_decimal(str(v)) for k, v in salary_structure_raw}

                # 2. Get Employee Details with all required data in one query
                cursor.execute(
                    """
                    SELECT u.id, ud.employee_id, CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                        dt.department_name, ds.designation_name,
                        CASE 
                            WHEN u.gender = 1 THEN 'Male'
                            WHEN u.gender = 2 THEN 'Female'
                            ELSE 'Other'
                        END AS gender,
                        ud.gross_salary,
                        u.employee_hub_id,
                        u.state,
                        ud.office_shift_id,
                        ud.date_of_joining,
                        u.city as location,
                        ud.bank_name,
                        ud.account_number as bank_account_number,
                        ud.pf_number,
                        ud.uan_number,
                        ud.esic_number,
                        ud.pan_number
                    FROM ci_erp_users u
                    LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
                    INNER JOIN ci_departments dt ON ud.department_id = dt.department_id
                    INNER JOIN ci_designations ds ON dt.department_id = ds.department_id
                    WHERE ud.employee_id IS NOT NULL AND u.is_active = 1
                    AND ud.employee_id = %s
                """, [employee_id]
                )
                employee_row = cursor.fetchone()
                
                # Extract employee IDs for single employee (no batch operations needed now)
                if not employee_row:
                    return Response({"results": [], "message": "No employees found"})
                
                emp = employee_row  # Direct tuple from fetchone()
                emp_id = emp[1]  # emp[1] is employee_id
                employee_hub_id = emp[7]
                state = emp[8]
                office_shift_ids = [emp[9]] if emp[9] else []  # Single employee's shift

                # 3. Get office shifts data for single employee
                office_shifts_map = {}

                try:
                    
                    if employee_hub_id or office_shift_ids:

                        # Prepare parameters for the query
                        query_params = []
                        conditions = []
                        
                        # Add employee_hub_id condition if we have hub ID
                        if employee_hub_id:
                            conditions.append(f"os.employee_hub_id = %s")
                            query_params.append(employee_hub_id)
                        
                        # Add office_shift_id condition if we have shift ID
                        if office_shift_ids:
                            shift_placeholders = ','.join(['%s'] * len(office_shift_ids))
                            conditions.append(f"os.office_shift_id IN ({shift_placeholders})")
                            query_params.extend(office_shift_ids)
                        
                        # Combine conditions with OR
                        where_clause = ' OR '.join(conditions)
                        
                        cursor.execute(
                            f"""
                            SELECT os.employee_hub_id, os.office_shift_id, ud.employee_id, os.shift_name,
                                os.monday_in_time, os.monday_out_time,
                                os.tuesday_in_time, os.tuesday_out_time,
                                os.wednesday_in_time, os.wednesday_out_time,
                                os.thursday_in_time, os.thursday_out_time,
                                os.friday_in_time, os.friday_out_time,
                                os.saturday_in_time, os.saturday_out_time,
                                os.sunday_in_time, os.sunday_out_time
                            FROM ci_office_shifts os 
                            LEFT JOIN ci_erp_users_details ud ON os.office_shift_id = ud.office_shift_id
                            WHERE {where_clause}
                            """,
                            query_params
                        )
                        
                        shifts_data = cursor.fetchall()
                        for shift in shifts_data:
                            employee_hub_id_shift = shift[0]
                            office_shift_id = shift[1]
                            employee_id_shift = shift[2]  # This will be None for hub-level shifts
                            shift_name = shift[3]
                            
                            shift_schedule = {
                                'shift_name': shift_name,
                                'monday': {'in': shift[4], 'out': shift[5]},
                                'tuesday': {'in': shift[6], 'out': shift[7]},
                                'wednesday': {'in': shift[8], 'out': shift[9]},
                                'thursday': {'in': shift[10], 'out': shift[11]},
                                'friday': {'in': shift[12], 'out': shift[13]},
                                'saturday': {'in': shift[14], 'out': shift[15]},
                                'sunday': {'in': shift[16], 'out': shift[17]}
                            }
                            
                            # If we have a specific employee_id, map by employee_id
                            if employee_id_shift:
                                office_shifts_map[employee_id_shift] = shift_schedule
                            # Otherwise, map by employee_hub_id for employees without specific shifts
                            elif employee_hub_id_shift:
                                office_shifts_map[employee_hub_id_shift] = shift_schedule
                                
                except Exception as e:
                    # print(f"Error fetching office shifts data: {e}")
                    office_shifts_map = {}

                # 4. Get attendance data for single employee
                try:
                    cursor.execute(
                        f"""
                        SELECT 
                            ud.employee_id,
                            SUM(CASE WHEN bd.status = 'P' THEN 1 ELSE 0 END) AS present_days,
                            SUM(CASE WHEN bd.status = 'H' THEN 1 ELSE 0 END) AS half_days
                        FROM ci_erp_users u
                        LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
                        INNER JOIN ci_biomatric_data bd ON ud.employee_id = bd.emp_id
                        WHERE MONTH(bd.login_date) = %s 
                        AND YEAR(bd.login_date) = %s 
                        AND bd.attendance_status = 'Present'
                        AND bd.state_in_out = 'in'
                        AND ud.employee_id = %s
                        GROUP BY ud.employee_id
                        """,
                        [month, year, emp_id]
                    )
                    
                    attendance_data = cursor.fetchall()
                    present_days_map = {}
                    half_days_map = {}
                    
                    for emp_id_att, present, half in attendance_data:
                        present_days_map[emp_id_att] = present or 0
                        half_days_map[emp_id_att] = half or 0

                        # print(present_days_map[emp_id_att])
                        
                except Exception as e:
                    # print(f"Error fetching attendance data: {e}")
                    present_days_map = {}
                    half_days_map = {}

                # 5. Get approved leaves for single employee
                try:
                    cursor.execute(
                        f"""
                        SELECT employee_id, 
                               SUM(CASE 
                                   WHEN is_half_day = 1 THEN 0.5 
                                   ELSE no_of_days
                               END) AS leave_days
                        FROM ci_leave_applications
                        WHERE status = 1 
                        AND line_manager_status = 1
                        AND employee_id = %s
                        AND ((MONTH(from_date) = %s AND YEAR(from_date) = %s) 
                             OR (MONTH(to_date) = %s AND YEAR(to_date) = %s)
                             OR (from_date <= %s AND to_date >= %s))
                        GROUP BY employee_id
                        """,
                        [
                            emp_id,
                            month, year, month, year,
                            f"{year}-{month:02d}-01",
                            f"{year}-{month:02d}-{days_in_month}",
                        ],
                    )
                    leave_days_map = dict(cursor.fetchall())
                except Exception as e:
                    # print(f"Error fetching leave data: {e}")
                    leave_days_map = {}

                # 6. Get holidays for single employee
                holidays_map = {}

                try:
                    # print("test..")
                    query_params = [
                        month, year, month, year,
                        f"{year}-{month:02d}-01",
                        f"{year}-{month:02d}-{days_in_month}",
                    ]

                    conditions = ["h.is_publish = 1"]

                    if employee_hub_id:
                        conditions.append(f"h.employee_hub = %s")
                        query_params.append(employee_hub_id)

                    if state:
                        conditions.append(f"h.state = %s")
                        query_params.append(state)

                    holiday_where_clause = ' AND ' + ' AND '.join(conditions) if conditions else ''

                    cursor.execute(
                        f"""
                        SELECT h.employee_hub, h.state, COUNT(*) as holiday_days
                        FROM ci_holidays h
                        WHERE ((MONTH(h.start_date) = %s AND YEAR(h.start_date) = %s) 
                            OR (MONTH(h.end_date) = %s AND YEAR(h.end_date) = %s)
                            OR (h.start_date <= %s AND h.end_date >= %s))
                        {holiday_where_clause}
                        GROUP BY h.employee_hub, h.state
                        """,
                        query_params
                    )
                    
                    holidays_data = cursor.fetchall()

                    for employee_hub, state_h, holiday_days in holidays_data:
                        # Convert to consistent string types
                        key = (str(employee_hub) if employee_hub else '', str(state_h) if state_h else '')
                        holidays_map[key] = int(holiday_days) if holiday_days else 0

                except Exception as e:
                    print(f"Error fetching holidays data: {e}")
                    holidays_map = {}

                # 6.1. Get TDS for single employee
                tds_map = {}
                try:
                    from_date = f"{year}-{month:02d}-01"
                    to_date = f"{year}-{month:02d}-{days_in_month}"
                    
                    cursor.execute(
                        f"""
                        SELECT employee_id, tds_amount 
                        FROM ci_employee_tds 
                        WHERE employee_id = %s
                        AND from_date <= %s 
                        AND to_date >= %s
                        """,
                        [emp_id, to_date, from_date]
                    )
                    
                    tds_data = cursor.fetchall()
                    for emp_id_tds, tds_amount in tds_data:
                        tds_map[emp_id_tds] = self.safe_decimal(str(tds_amount or 0))
                        
                except Exception as e:
                    # print(f"Error fetching TDS data: {e}")
                    tds_map = {}

                # 7. Get salary changes for single employee
                try:
                    salary_changes_by_employee = self.get_all_salary_changes_batch(emp_id, year, month)
                except Exception as e:
                    # print(f"Error fetching salary changes: {e}")
                    salary_changes_by_employee = {}

                # 8. Calculate holiday days from office shifts
                try:
                    holiday_days_data = self.calculate_holiday_days_from_shifts(year, month, office_shifts_map, [emp])
                except Exception as e:
                    # print(f"Error calculating holiday days from shifts: {e}")
                    # Fallback to original calculation
                    sundays = self.get_sundays_in_month(year, month)
                    holiday_days_data = {
                        'total_sundays': len(sundays),
                        'holiday_days_by_employee': {}
                    }

                # Prepare data for salary calculation of single employee
                employees_salary_data = None
                payable_days_by_employee = {}
                

                try:
                    (
                        user_id, emp_id, emp_name, dept, desg, gender,
                        gross_salary, employee_hub_id, state, office_shift_id, date_of_joining, location, bank_name,
                        bank_account_number, pf_number, uan_number, esic_number, pan_number
                    ) = emp

                    lookup_key = (
                        str(employee_hub_id) if employee_hub_id else '', 
                        str(state) if state else ''
                    )
                    
                    # Calculate payable days for this employee with safe conversions
                    present_days = self.safe_decimal(present_days_map.get(emp_id, 0))
                    half_days_count = self.safe_decimal(half_days_map.get(emp_id, 0))
                    leave_days = self.safe_decimal(str(leave_days_map.get(emp_id, 0)))

                    # print(f"Looking up holiday key: {lookup_key}")
                    state_holidays = self.safe_decimal(holidays_map.get(lookup_key, 0))

                    half_days_value = half_days_count * self.safe_decimal("0.5")

                    # Get employee-specific holiday days from shifts or fall back to general calculation
                    employee_holiday_data = holiday_days_data['holiday_days_by_employee'].get(
                        emp_id, 
                        {'shift_holidays': holiday_days_data.get('total_sundays', 0)}
                    )
                    shift_holidays = self.safe_decimal(employee_holiday_data.get('shift_holidays', 0))

                    payable_days = (
                        present_days + half_days_value + leave_days + 
                        shift_holidays
                    )
                    
                    payable_days_by_employee[emp_id] = payable_days
                    employees_salary_data = (emp_id, payable_days, gross_salary)
                    
                except Exception as e:
                    # print(f"Error processing employee {emp_id if 'emp_id' in locals() else 'unknown'}: {e}")
                    # Set default values for this employee
                    if 'emp_id' in locals():
                        payable_days_by_employee[emp_id] = self.safe_decimal("0.00")
                        employees_salary_data = (emp_id, self.safe_decimal("0.00"), gross_salary if 'gross_salary' in locals() else 0)

                # 9. Calculate gross earnings for single employee
                try:
                    salary_calculations = self.calculate_gross_earning_with_salary_changes_batch(
                        employees_salary_data, salary_changes_by_employee, year, month, days_in_month
                    )
                except Exception as e:
                    # print(f"Error in salary calculations: {e}")
                    salary_calculations = {}

                # 8. Build final results
                results = []
                
                (
                    user_id, emp_id, emp_name, dept, desg, gender,
                    gross_salary, employee_hub_id, state, office_shift_id, date_of_joining, location, bank_name,
                    bank_account_number, pf_number, uan_number, esic_number, pan_number
                ) = emp

                if gross_salary is None:
                    gross_salary = 0
                
                payable_days = payable_days_by_employee.get(emp_id, self.safe_decimal("0.00"))

                # print("payable_days: ", payable_days)

                salary_calc = salary_calculations.get(emp_id, {
                    'gross_earning': self.safe_decimal("0.00"),
                    'total_monthly_earning': self.safe_decimal(gross_salary or 0)
                })
                
                gross_earning = salary_calc.get('gross_earning', self.safe_decimal("0.00"))
                total_monthly_earning = salary_calc.get('total_monthly_earning', self.safe_decimal(gross_salary or 0))
                
                # if emp_id == 'V1112':
                #     # print("total monthly earnings: ", total_monthly_earning)

                esic_applicable = gross_salary <= self.safe_decimal("21000")  # Monthly limit

                # Get structure percentages
                get = lambda key: salary_structure.get(key, self.safe_decimal("0.00"))

                # Earnings
                basic_da = gross_earning * get("basic_plus_da")
                hra = gross_earning * get("hra")
                medical = gross_earning * (
                    get("medical_allowance_with_esic")
                    if esic_applicable
                    else get("medical_allowance_without_esic")
                )
                conveyance = gross_earning * (
                    get("conveyance_allowance_with_esic")
                    if esic_applicable
                    else get("conveyance_allowance_without_esic")
                )

                total_earnings = basic_da + hra + medical + conveyance

                # Deductions
                pf = min(
                    (gross_earning - hra) * get("pf_employee_contribution"),
                    self.safe_decimal("1800"),
                )

                if pf > 1800:
                    pf = 1800

                esic_emp = gross_earning * get("esic_employee_contribution")  # Static/user-filled
                pt = self.safe_decimal("0")
                if gender == "Male":
                    pt = self.safe_decimal("300") if month == 2 else self.safe_decimal("200")
                elif gender == "Female":
                    if month == 2:
                        pt = (
                            self.safe_decimal("300")
                            if gross_earning > self.safe_decimal("25000")
                            else self.safe_decimal("0")
                        )
                    else:
                        pt = (
                            self.safe_decimal("200")
                            if gross_earning > self.safe_decimal("25000")
                            else self.safe_decimal("0")
                        )

                # Benefits
                pf_employer = min(
                    (gross_earning - hra) * get("pf_employer_contribution"),
                    self.safe_decimal("1800"),
                )
                esic_employer = (
                    gross_earning * get("esic_employer_contribution")
                    if esic_applicable
                    else self.safe_decimal("0.00")
                )

                no_of_employment_year = 0
                # print("date_of_joining ", date_of_joining)
                if date_of_joining:
                    try:
                        if isinstance(date_of_joining, str):
                            date_of_joining = datetime.strptime(date_of_joining, "%d-%m-%Y")
                            # print("date_of_joining: ", date_of_joining)
                        
                        if date_of_joining <= datetime.now():
                            no_of_employment_year = (datetime.now() - date_of_joining).days / 365.25
                            # print("no_of_employment_year: ", no_of_employment_year)
                        else:
                            no_of_employment_year = 0
                    except (TypeError, ValueError, AttributeError) as e:
                        no_of_employment_year = 0

                no_of_employment_year = max(0, no_of_employment_year)
                # print("updated_no_of_employment_year: ", no_of_employment_year)

                try:
                    if no_of_employment_year > 5 and get("basic_plus_da"):
                        gratuity = (get("basic_plus_da") * self.safe_decimal("15") / self.safe_decimal("26")) * self.safe_decimal(str(no_of_employment_year))
                    else:
                        gratuity = self.safe_decimal("0.00")
                except (TypeError, ValueError, ZeroDivisionError):
                    gratuity = self.safe_decimal("0.00")

                if gratuity < 0:
                    gratuity = self.safe_decimal("0.00")


                if month in (6, '6', '06'):
                    mlwf_deduction = get("mlwf_deduction")
                elif month in (12, '12'):
                    mlwf_deduction = 75
                else:
                    mlwf_deduction = 0
                
                tds = tds_map.get(emp_id, self.safe_decimal("0.00"))

                total_deduction = pf + esic_emp + pt + mlwf_deduction + tds
                total_benefit = pf_employer + esic_employer + gratuity
                net_pay = total_earnings - total_deduction
                ctc = total_earnings + total_benefit


                # 8. Build final result for single employee
                result = {
                    "employee_name": emp_name,
                    "month": month,
                    "year": year,
                    "salary_payment_date": "",
                    "employee_id": emp_id,
                    "department_name": dept,
                    "date_of_joining": date_of_joining,
                    "designation_name": desg,
                    "location": location,
                    "payable_days": int(payable_days),
                    "bank_name": bank_name,
                    "bank_account_number": bank_account_number,
                    "pf_number": pf_number,
                    "uan_number": uan_number,
                    "esic_number": esic_number,
                    "pan_number": pan_number,
                    "basic_plus_da": float(round(basic_da, 2)),
                    "hra": float(round(hra, 2)),
                    "medical_allowance": float(round(medical, 2)),
                    "conveyance_allowance": float(round(conveyance, 2)),
                    "arrears": 0.00,
                    "total_earnings": float(round(total_earnings, 2)),
                    "pf": float(round(pf, 2)),
                    "esic": float(round(esic_emp, 2)),
                    "pt": float(round(pt, 2)),
                    "tds": float(round(tds, 2)),
                    "mlwf": mlwf_deduction,
                    "other_deduction": 0.00,
                    "total_deduction": float(round(total_deduction, 2)),
                    "net_pay": float(round(net_pay, 2)),
                }
                
                return Response(
                    {"status": "success", "data": result},
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )