from datetime import datetime
from django.db import connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from decimal import Decimal


class HRDashboardMetrics(APIView):
    """
    API to fetch HR Dashboard metrics:
    - Total Number of Employees
    - Last Month Total Revenue
    - Per Employee Contribution
    - Monthly Total Salary
    - Monthly Expenses
    - Total Employee Cost
    - Per Employee Cost
    - Per Employee Revenue
    
    Data Sources:
    - ci_save_revenue_expense: total_revenue, total_expense (monthly_expenses)
    - ci_erp_users_details: gross_salary (to calculate monthly_total_salary)
    - ci_erp_users: total active employees count
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Get current month and year, and calculate last month
            today = datetime.now()
            current_month = today.month
            current_year = today.year
            
            # Calculate last month
            if current_month == 1:
                last_month = 12
                last_month_year = current_year - 1
            else:
                last_month = current_month - 1
                last_month_year = current_year


            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT total_revenue, monthly_total_salary, monthly_expenses, total_employee_cost, per_employee_cost, employee_contribution, per_revenue
                    FROM ci_revenue
                    WHERE month = %s AND year = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """, [last_month, last_month_year])
                row = cursor.fetchone()
                if row:
                    total_revenue = Decimal(row[0]) if row[0] else Decimal(0)
                    monthly_total_salary = Decimal(row[1]) if row[1] else Decimal(0)
                    monthly_expenses = Decimal(row[2]) if row[2] else Decimal(0)
                    total_employee_cost = Decimal(row[3]) if row[3] else Decimal(0)
                    per_employee_cost = Decimal(row[4]) if row[4] else Decimal(0)
                    per_employee_contribution = Decimal(row[5]) if row[5] else Decimal(0)
                    per_employee_revenue = Decimal(row[6]) if row[6] else Decimal(0)
                else:
                    total_revenue = monthly_total_salary = monthly_expenses = total_employee_cost = per_employee_cost = per_employee_contribution = per_employee_revenue = Decimal(0)

            # Get total number of active employees
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM ci_erp_users WHERE is_active=1")
                total_employees = cursor.fetchone()[0] or 0

            # Prepare response
            response_data = {
                "status": True,
                "message": "HR Dashboard metrics fetched successfully",
                "data": {
                    "period": {
                        "month": last_month,
                        "year": last_month_year,
                        "month_name": datetime(last_month_year, last_month, 1).strftime('%B')
                    },
                    "total_number_of_employees": total_employees,
                    "last_month_total_revenue": float(total_revenue),
                    "per_employee_contribution": round(float(per_employee_contribution), 2),
                    "monthly_total_salary": float(monthly_total_salary),
                    "monthly_expenses": float(monthly_expenses),
                    "total_employee_cost": float(total_employee_cost),
                    "per_employee_cost": round(float(per_employee_cost), 2),
                    "per_employee_revenue": round(float(per_employee_revenue), 2)
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"status": False, "message": f"Error fetching HR Dashboard metrics: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HRDashboardMetricsByMonth(APIView):
    """
    API to fetch HR Dashboard metrics for a specific month and year.
    Query params: month (1-12), year (e.g., 2025)
    
    Data Sources:
    - ci_save_revenue_expense: total_revenue, total_expense (monthly_expenses)
    - ci_erp_users_details: gross_salary (to calculate monthly_total_salary)
    - ci_erp_users: total active employees count
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get month and year from query params
            month = request.query_params.get('month')
            year = request.query_params.get('year')

            if not month or not year:
                return Response(
                    {"status": False, "message": "Month and year are required query parameters"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                month = int(month)
                year = int(year)
                
                if month < 1 or month > 12:
                    return Response(
                        {"status": False, "message": "Month must be between 1 and 12"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"status": False, "message": "Month and year must be valid integers"},
                    status=status.HTTP_400_BAD_REQUEST
                )


            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT total_revenue, monthly_total_salary, monthly_expenses, total_employee_cost, per_employee_cost, employee_contribution, per_revenue
                    FROM ci_revenue
                    WHERE month = %s AND year = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """, [month, year])
                row = cursor.fetchone()
                if row:
                    total_revenue = Decimal(row[0]) if row[0] else Decimal(0)
                    monthly_total_salary = Decimal(row[1]) if row[1] else Decimal(0)
                    monthly_expenses = Decimal(row[2]) if row[2] else Decimal(0)
                    total_employee_cost = Decimal(row[3]) if row[3] else Decimal(0)
                    per_employee_cost = Decimal(row[4]) if row[4] else Decimal(0)
                    per_employee_contribution = Decimal(row[5]) if row[5] else Decimal(0)
                    per_employee_revenue = Decimal(row[6]) if row[6] else Decimal(0)
                else:
                    total_revenue = monthly_total_salary = monthly_expenses = total_employee_cost = per_employee_cost = per_employee_contribution = per_employee_revenue = Decimal(0)

            # Get total number of active employees
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM ci_erp_users WHERE is_active=1")
                total_employees = cursor.fetchone()[0] or 0

            # Prepare response
            response_data = {
                "status": True,
                "message": "HR Dashboard metrics fetched successfully",
                "data": {
                    "period": {
                        "month": month,
                        "year": year,
                        "month_name": datetime(year, month, 1).strftime('%B')
                    },
                    "total_number_of_employees": total_employees,
                    "total_revenue": float(total_revenue),
                    "per_employee_contribution": round(float(per_employee_contribution), 2),
                    "monthly_total_salary": float(monthly_total_salary),
                    "monthly_expenses": float(monthly_expenses),
                    "total_employee_cost": float(total_employee_cost),
                    "per_employee_cost": round(float(per_employee_cost), 2),
                    "per_employee_revenue": round(float(per_employee_revenue), 2)
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"status": False, "message": f"Error fetching HR Dashboard metrics: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
