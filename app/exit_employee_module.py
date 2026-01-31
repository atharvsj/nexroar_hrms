
from calendar import monthrange
from datetime import date, datetime, time
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import os
from django.http import Http404
from urllib.parse import quote
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.db import connection, transaction




# Employee Exit Procedure - 28-07-2025

# 17-09-2025

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db import connection

# class CreateExitQuestionnaire(APIView):

#     def get(self, request):
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT ques_id, question, created_date FROM ci_employee_exit_questionnaire")
#                 rows = cursor.fetchall()
#                 data = [
#                     {"ques_id": row[0], "question": row[1], "created_date": row[2].strftime("%Y-%m-%d %H:%M:%S")}
#                     for row in rows
#                 ]
#             return Response(data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def post(self, request):
#         try:
#             question = request.data.get("question")
#             if not question:
#                 return Response({"error": "Question is required."}, status=status.HTTP_400_BAD_REQUEST)

#             with connection.cursor() as cursor:
#                 cursor.execute(
#                     "INSERT INTO ci_employee_exit_questionnaire (question) VALUES (%s)",
#                     [question]
#                 )
#             return Response({"message": "Question added successfully."}, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def put(self, request):
#         try:
#             ques_id = request.data.get("ques_id")
#             question = request.data.get("question")

#             if not ques_id or not question:
#                 return Response({"error": "ques_id and question are required."}, status=status.HTTP_400_BAD_REQUEST)

#             with connection.cursor() as cursor:
#                 cursor.execute(
#                     "UPDATE ci_employee_exit_questionnaire SET question = %s WHERE ques_id = %s",
#                     [question, ques_id]
#                 )
#                 if cursor.rowcount == 0:
#                     return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)

#             return Response({"message": "Question updated successfully."}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def delete(self, request):
#         try:
#             ques_id = request.data.get("ques_id")
#             if not ques_id:
#                 return Response({"error": "ques_id is required."}, status=status.HTTP_400_BAD_REQUEST)

#             with connection.cursor() as cursor:
#                 cursor.execute(
#                     "DELETE FROM ci_employee_exit_questionnaire WHERE ques_id = %s",
#                     [ques_id]
#                 )
#                 if cursor.rowcount == 0:
#                     return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)

#             return Response({"message": "Question deleted successfully."}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # Get Form Data For Questionneair Form 

# from django.db import connection
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# class GetEmployeeExitQuestionneair(APIView):
#     def get(self, request):
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT 
#                         u.id,
#                         ud.employee_id,
#                         CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
#                         dt.department_name,
#                         ds.designation_name,
#                         CASE
#                             WHEN u.gender = 1 THEN 'Male'
#                             WHEN u.gender = 2 THEN 'Female'
#                             ELSE 'Other'
#                         END AS gender,
#                         ud.date_of_joining,
#                         ud.date_of_leaving,
#                         dv.division_name,
#                         CONCAT(mgr.first_name, ' ', mgr.last_name) AS manager_name
#                     FROM ci_erp_users u
#                     LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
#                     INNER JOIN ci_departments dt ON ud.department_id = dt.department_id
#                     INNER JOIN ci_designations ds ON dt.department_id = ds.department_id
#                     INNER JOIN ci_division dv ON ud.division_id = dv.division_id
#                     LEFT JOIN ci_erp_users mgr ON ud.manager = mgr.id
#                     GROUP BY u.id;
#                 """)

#                 columns = [col[0] for col in cursor.description]
#                 data = [dict(zip(columns, row)) for row in cursor.fetchall()]

#             return Response({"status": True, "data": data}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"status": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # Save Feedback Form 

# class SubmitEmployeeFeedbackForm(APIView):
#     def post(self, request):
#         try:
#             employee_id = request.data.get('employee_id')
#             feedback_list = request.data.get('feedback', [])

#             if not employee_id or not feedback_list:
#                 return Response({"error": "employee_id and feedback are required."}, status=status.HTTP_400_BAD_REQUEST)

#             with connection.cursor() as cursor:
#                 for item in feedback_list:
#                     ques_id = item.get('ques_id')
#                     answer = item.get('answer')
#                     brief_answer = item.get('brief_answer', None)

#                     if not ques_id or not answer:
#                         continue  # Skip incomplete entries

#                     cursor.execute("""
#                         INSERT INTO ci_employee_feedback (employee_id, ques_id, answer, brief_answer)
#                         VALUES (%s, %s, %s, %s)
#                     """, [employee_id, ques_id, answer, brief_answer])

#             return Response({"message": "Feedback submitted successfully."}, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class ViewCompletedFeedbackForm(APIView):
#     def get(self, request):
#         try:
#             employee_id = request.GET.get('employee_id')
 
#             if not employee_id:
#                 return Response({"status": False, "error": "employee_id is required"}, status=status.HTTP_400_BAD_REQUEST)
 
#             with connection.cursor() as cursor:
#                 query = """
#                     SELECT *
#                     FROM ci_erp_users_details AS ud
#                     INNER JOIN ci_employee_feedback AS ef
#                         ON ud.employee_id = ef.employee_id
#                     INNER JOIN ci_employee_exit_questionnaire AS eq
#                         ON ef.ques_id = eq.ques_id
#                     WHERE ef.employee_id = %s
#                 """
#                 cursor.execute(query, [employee_id])
#                 columns = [col[0] for col in cursor.description]
#                 results = [dict(zip(columns, row)) for row in cursor.fetchall()]
 
#             return Response({"status": True, "data": results}, status=status.HTTP_200_OK)
 
#         except Exception as e:
#             return Response({"status": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Exit-Employee Exit-Dashboard HR

class ExitQuestionnaireAPIView(APIView):
    def post(self, request):
        try:
            question = request.data.get("question")
            options = request.data.get("options", [])

            if not question or not options:
                return Response({"status": "error", "message": "Question and options are required"}, status=status.HTTP_400_BAD_REQUEST)

            with connection.cursor() as cursor:
                # Insert question
                cursor.execute("""
                    INSERT INTO ci_employee_exit_questionnaire (question, created_date)
                    VALUES (%s, %s)
                   
                """, [question, datetime.now().date()])

                ques_id = cursor.lastrowid

                # Insert options
                for opt in options:
                    cursor.execute("""
                        INSERT INTO ci_employee_exit_option (ques_id, answer_option, created_at)
                        VALUES (%s, %s, %s)
                    """, [ques_id, opt, datetime.now().date()])

            return Response({
                "status": "success",
                "message": "Question and options added successfully",
                "data": {
                    "question": question,
                    "options": options
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT q.ques_id, q.question, o.answer_option
                    FROM ci_employee_exit_questionnaire q
                    LEFT JOIN ci_employee_exit_option o ON q.ques_id = o.ques_id
                    ORDER BY q.ques_id, o.answer_id
                """)
                rows = cursor.fetchall()

            data = {}
            for row in rows:
                ques_id, question, option = row
                if ques_id not in data:
                    data[ques_id] = {
                        "question": question,
                        "options": []   # start with empty list
                    }
                if option:  # add option only if it exists
                    data[ques_id]["options"].append(option)

            return Response({
                "status": "success",
                "data": list(data.values())
            }, status=200)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)


    def patch(self, request, ques_id):
        """
        Update question text or replace options for a given ques_id
        """
        try:
            question = request.data.get("question")
            options = request.data.get("options")  # should be list if provided

            updated_question = False
            updated_options = False

            with connection.cursor() as cursor:
                # Update question text
                if question:
                    rows = cursor.execute("""
                        UPDATE ci_employee_exit_questionnaire
                        SET question = %s
                        WHERE ques_id = %s
                    """, [question, ques_id])
                    if rows > 0:
                        updated_question = True

                # Replace options if provided
                if options is not None:
                    cursor.execute("DELETE FROM ci_employee_exit_option WHERE ques_id = %s", [ques_id])
                    for opt in options:
                        cursor.execute("""
                            INSERT INTO ci_employee_exit_option (ques_id, answer_option, created_at)
                            VALUES (%s, %s, %s)
                        """, [ques_id, opt, datetime.now().date()])
                    updated_options = True

            # Prepare response message
            if updated_question and updated_options:
                message = "Question and/or options updated successfully"
            elif updated_question:
                message = "Question updated successfully"
            elif updated_options:
                message = "Options updated successfully"
            else:
                message = "No changes made. Invalid ques_id or same data."

            return Response({
                "status": "success" if (updated_question or updated_options) else "error",
                "message": message
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    def delete(self, request, ques_id):
        """
        Delete question and its options by ques_id
        """
        try:
            with connection.cursor() as cursor:
                # Delete options first (foreign key dependency)
                cursor.execute("DELETE FROM ci_employee_exit_option WHERE ques_id = %s", [ques_id])
                # Delete question
                cursor.execute("DELETE FROM ci_employee_exit_questionnaire WHERE ques_id = %s", [ques_id])

            return Response({
                "status": "success",
                "message": f"Question {ques_id} and its options deleted successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



##Employee Exit - Employee Panel
# class SubmitEmployeeExitFeedbackForm(APIView):
#     def post(self, request):
#         try:
#             employee_id = request.data.get('employee_id')
#             feedback_list = request.data.get('feedback', [])

#             if not employee_id or not feedback_list:
#                 return Response({"error": "employee_id and feedback are required."}, status=status.HTTP_400_BAD_REQUEST)

#             with connection.cursor() as cursor:
#                 for item in feedback_list:
#                     ques_id = item.get('ques_id')
#                     answer = item.get('answer')
#                     brief_answer = item.get('brief_answer', None)

#                     if not ques_id or not answer:
#                         continue  # Skip incomplete entries

#                     cursor.execute("""
#                         INSERT INTO ci_employee_exit_feedback (employee_id, ques_id, answer, brief_answer)
#                         VALUES (%s, %s, %s, %s)
#                     """, [employee_id, ques_id, answer, brief_answer])

#             return Response({"message": "Exit Interview Questionnaire submitted successfully."}, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class SubmitEmployeeExitFeedbackForm(APIView):
#     def post(self, request):
#         try:
#             employee_id = request.data.get('employee_id')
#             # user_id = request.data.get('user_id')  # 👈 Add user_id
#             feedback_list = request.data.get('feedback', [])

#             if not employee_id or not feedback_list:
#                 return Response(
#                     {"error": "employee_id, user_id and feedback are required."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             with connection.cursor() as cursor:
#                 # Insert feedback list
#                 for item in feedback_list:
#                     ques_id = item.get('ques_id')
#                     answer = item.get('answer')
#                     brief_answer = item.get('brief_answer', None)

#                     if not ques_id or not answer:
#                         continue  # Skip incomplete entries

#                     cursor.execute("""
#                         INSERT INTO ci_employee_exit_feedback (employee_id, ques_id, answer, brief_answer)
#                         VALUES (%s, %s, %s, %s)
#                         ON DUPLICATE KEY UPDATE 
#                             answer = VALUES(answer),
#                             brief_answer = VALUES(brief_answer)
#                     """, [employee_id, ques_id, answer, brief_answer])

#                 # === Check if all questions are answered ===
#                 cursor.execute("SELECT COUNT(*) FROM ci_employee_exit_questionnaire")
#                 total_questions = cursor.fetchone()[0]

#                 cursor.execute("""
#                     SELECT COUNT(DISTINCT ques_id) 
#                     FROM ci_employee_exit_feedback 
#                     WHERE employee_id = %s
#                 """, [employee_id])
#                 answered_questions = cursor.fetchone()[0]

#                 if answered_questions == total_questions and total_questions > 0:
#                     # ✅ Auto-update final table
#                     cursor.execute("""
#                         INSERT INTO ci_employee_exit_final (employee_id, user_id, exit_interview_questionnaire)
#                         VALUES (%s, %s, 'Yes')
#                         ON DUPLICATE KEY UPDATE 
#                             exit_interview_questionnaire = 'Yes',
#                             user_id = VALUES(user_id)
#                     """, [employee_id])

#             return Response(
#                 {"message": "Exit Interview Questionnaire submitted successfully."},
#                 status=status.HTTP_201_CREATED
#             )

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class SubmitEmployeeExitFeedbackForm(APIView):
#     def post(self, request):
#         try:
#             employee_id = request.data.get('employee_id')
#             # user_id = request.data.get('user_id')  # 👈 Add user_id
#             feedback_list = request.data.get('feedback', [])

#             if not employee_id or not feedback_list:
#                 return Response(
#                     {"error": "employee_id, user_id and feedback are required."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             with connection.cursor() as cursor:
#                 # Insert feedback list
#                 for item in feedback_list:
#                     ques_id = item.get('ques_id')
#                     answer = item.get('answer')
#                     brief_answer = item.get('brief_answer', None)

#                     if not ques_id or not answer:
#                         continue  # Skip incomplete entries

#                     cursor.execute("""
#                         INSERT INTO ci_employee_exit_feedback (employee_id, ques_id, answer, brief_answer)
#                         VALUES (%s, %s, %s, %s)
#                         ON DUPLICATE KEY UPDATE 
#                             answer = VALUES(answer),
#                             brief_answer = VALUES(brief_answer)
#                     """, [employee_id, ques_id, answer, brief_answer])

#                     # ✅ Auto-update final table
#                 cursor.execute("""
#                         INSERT INTO ci_employee_exit_final (employee_id, user_id, exit_interview_questionnaire)
#                         VALUES (%s, %s, 'Yes')
#                         ON DUPLICATE KEY UPDATE 
#                             exit_interview_questionnaire = 'Yes',
#                             user_id = VALUES(user_id)
#                     """, [employee_id])

#             return Response(
#                 {"message": "Exit Interview Questionnaire submitted successfully."},
#                 status=status.HTTP_201_CREATED
#             )

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





##======   When the employee submit the form then automatically status updated YES in the final table
class SubmitEmployeeExitFeedbackForm(APIView):
    def post(self, request):
        try:
            employee_id = request.data.get('employee_id')
            feedback_list = request.data.get('feedback', [])
 
            if not employee_id or not feedback_list:
                return Response({"error": "employee_id and feedback are required."}, status=status.HTTP_400_BAD_REQUEST)
 
            with connection.cursor() as cursor:
             
                cursor.execute(
                    """SELECT COUNT(*) FROM ci_employee_exit_feedback WHERE employee_id = %s""",
                    [employee_id]
                )
                already_exists = cursor.fetchone()[0]
 
                if already_exists > 0:
                    return Response(
                        {"message": "You have already answered the questionnaire."},
                        status=status.HTTP_200_OK
                    )
 
             
                for item in feedback_list:
                    ques_id = item.get('ques_id')
                    answer = item.get('answer')
                    brief_answer = item.get('brief_answer', None)
 
                    if not ques_id or not answer:
                        continue
 
                    cursor.execute("""
                        INSERT INTO ci_employee_exit_feedback (employee_id, ques_id, answer, brief_answer)
                        VALUES (%s, %s, %s, %s)
                    """, [employee_id, ques_id, answer, brief_answer])
              
                cursor.execute("SELECT id FROM ci_erp_users WHERE username = %s", [employee_id])
                user_id = cursor.fetchone()[0]
 
                cursor.execute("select employee_exit_final_id from ci_employee_exit_final where employee_id=%s",[employee_id])
                exit_final=cursor.fetchone()
                print(exit_final)
 
                if exit_final:
                    cursor.execute("""
                        UPDATE  ci_employee_exit_final  set exit_interview_questionnaire='Y'
                        WHERE employee_id = %s
                    """, [employee_id])
                else:
                    cursor.execute("""
                        INSERT INTO ci_employee_exit_final (user_id, employee_id, exit_interview_questionnaire)
                        VALUES (%s, %s, 'Y')
                    """, [user_id, employee_id])
                                # ---- Separate Exit Type Logic ----
                exit_type = None

                # 1. Check in ci_employee_exit
                cursor.execute("SELECT exit_type_id FROM ci_employee_exit WHERE employee_id = %s", [employee_id])
                exit_row = cursor.fetchone()
                if exit_row:
                    exit_type = exit_row[0]
                else:
                    # 2. If not found, check ci_resignations
                    cursor.execute("SELECT resignation_id FROM ci_resignations WHERE employee_id = %s", [employee_id])
                    resign_row = cursor.fetchone()
                    if resign_row:
                        exit_type = 177

                # Update exit_type if found
                if exit_type:
                    cursor.execute("""
                        UPDATE ci_employee_exit_final
                        SET exit_type = %s
                        WHERE employee_id = %s
                    """, [exit_type, employee_id])

            return Response({"message": "Feedback submitted successfully."}, status=status.HTTP_201_CREATED)
 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
        

class ViewCompletedFeedbackForm(APIView):
    def get(self, request):
        try:
            employee_id = request.GET.get("employee_id")
            user_id = request.user.id  # logged-in user submitting

            if not employee_id:
                return Response({"status": False, "error": "employee_id is required"}, status=400)

            

            with connection.cursor() as cursor:


                cursor.execute("""SELECT
                    u.id as user_id,
                    d.employee_id,
                    CONCAT(u.first_name, ' ', COALESCE(u.middle_name,''), ' ', u.last_name) as full_name,
                    dept.department_name as department,
                    desg.designation_name as designation,
                    divi.division_name as division,
                    d.date_of_joining,
                    h.location_name as headquarter,
                    -- pick resignation.last_working_day, if null then employee_exit.exit_date
                        COALESCE(r.last_working_day, ee.exit_date) as last_working_day,
                   
                    d.manager_emp_id,
                    
                    CONCAT(mu.first_name, ' ', COALESCE(mu.middle_name,''), ' ', mu.last_name) AS manager_full_name

                    FROM ci_erp_users u
                    JOIN ci_erp_users_details d ON u.id = d.user_id
                 
                    LEFT JOIN ci_departments dept ON d.department_id = dept.department_id
                    LEFT JOIN ci_designations desg ON d.designation_id = desg.designation_id
                    LEFT JOIN ci_division divi ON d.division_id = divi.division_id
                    LEFT JOIN ci_headquarters h ON d.location_id = h.location_id
                    LEFT JOIN ci_resignations r ON d.employee_id = r.employee_id
                    LEFT JOIN ci_employee_exit ee ON d.employee_id = ee.employee_id
                    LEFT JOIN ci_erp_users_details md ON d.manager_emp_id = md.employee_id
                    LEFT JOIN ci_erp_users mu ON md.user_id = mu.id
                    WHERE d.employee_id = %s
                    """,[employee_id])
                emp_data=dictfetchall(cursor)

                # Fetch required fields
                cursor.execute("""
                    SELECT 
                        ef.employee_id,
                        eq.ques_id,
                        eq.question,
                        ef.answer,
                        ef.brief_answer
                    FROM ci_employee_exit_feedback ef
                    INNER JOIN ci_employee_exit_questionnaire eq 
                        ON ef.ques_id = eq.ques_id
                    WHERE ef.employee_id = %s


                """, [employee_id])
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]


            return Response({"status": True, "emp_data":emp_data,"data": results}, status=200)

        except Exception as e:
            return Response({"status": False, "error": str(e)}, status=500)


# class ViewAllCompletedFeedbackForm(APIView):
#     def get(self, request):
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT
#                         u.id as user_id,
#                         d.employee_id,
#                         CONCAT(u.first_name, ' ', COALESCE(u.middle_name,''), ' ', u.last_name) as full_name,
#                         dept.department_name as department,
#                         desg.designation_name as designation,
#                         divi.division_name as division,
#                         d.date_of_joining,
#                         h.location_name as headquarter,
#                         r.last_working_day,
#                         d.manager_emp_id,
#                         CONCAT(mu.first_name, ' ', COALESCE(mu.middle_name,''), ' ', mu.last_name) AS manager_full_name,
#                         eq.ques_id,
#                         eq.question,
#                         ef.answer,
#                         ef.brief_answer
#                     FROM ci_employee_exit_feedback ef
#                     INNER JOIN ci_employee_exit_questionnaire eq 
#                         ON ef.ques_id = eq.ques_id
#                     INNER JOIN ci_erp_users_details d ON ef.employee_id = d.employee_id
#                     INNER JOIN ci_erp_users u ON u.id = d.user_id
#                     LEFT JOIN ci_departments dept ON d.department_id = dept.department_id
#                     LEFT JOIN ci_designations desg ON d.designation_id = desg.designation_id
#                     LEFT JOIN ci_division divi ON d.division_id = divi.division_id
#                     LEFT JOIN ci_headquarters h ON d.location_id = h.location_id
#                     LEFT JOIN ci_resignations r ON d.employee_id = r.employee_id
#                     LEFT JOIN ci_erp_users_details md ON d.manager_emp_id = md.employee_id
#                     LEFT JOIN ci_erp_users mu ON md.user_id = mu.id
#                     ORDER BY d.employee_id, eq.ques_id
#                 """)
#                 columns = [col[0] for col in cursor.description]
#                 results = [dict(zip(columns, row)) for row in cursor.fetchall()]

#             return Response({"status": True, "data": results}, status=200)

#         except Exception as e:
#             return Response({"status": False, "error": str(e)}, status=500)



class ViewAllCompletedFeedbackForm(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        u.id as user_id,
                        d.employee_id,
                        CONCAT(u.first_name, ' ', COALESCE(u.middle_name,''), ' ', u.last_name) as full_name,
                        dept.department_name as department,
                        desg.designation_name as designation,
                        divi.division_name as division,
                        d.date_of_joining,
                        h.location_name as headquarter,
                               
                         -- pick resignation.last_working_day, if null then employee_exit.exit_date
                        COALESCE(r.last_working_day, ee.exit_date) as last_working_day,
                               
                        d.manager_emp_id,
                        CONCAT(mu.first_name, ' ', COALESCE(mu.middle_name,''), ' ', mu.last_name) AS manager_full_name,
                               
                        eq.ques_id,
                        eq.question,
                        ef.answer,
                        ef.brief_answer
                    FROM ci_employee_exit_feedback ef
                    INNER JOIN ci_employee_exit_questionnaire eq 
                        ON ef.ques_id = eq.ques_id
                    INNER JOIN ci_erp_users_details d ON ef.employee_id = d.employee_id
                    INNER JOIN ci_erp_users u ON u.id = d.user_id
                    LEFT JOIN ci_departments dept ON d.department_id = dept.department_id
                    LEFT JOIN ci_designations desg ON d.designation_id = desg.designation_id
                    LEFT JOIN ci_division divi ON d.division_id = divi.division_id
                    LEFT JOIN ci_headquarters h ON d.location_id = h.location_id
                    LEFT JOIN ci_resignations r ON d.employee_id = r.employee_id
                    LEFT JOIN ci_employee_exit ee ON d.employee_id = ee.employee_id
                    LEFT JOIN ci_erp_users_details md ON d.manager_emp_id = md.employee_id
                    LEFT JOIN ci_erp_users mu ON md.user_id = mu.id
                    ORDER BY d.employee_id, eq.ques_id
                """)
                columns = [col[0] for col in cursor.description]
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # ================= Group Data by Employee =================
            employees = {}
            for row in rows:
                emp_id = row["employee_id"]

                # --- Safe date formatting helper ---
                def format_date(value):
                    if isinstance(value, (datetime, date)):
                        return value.strftime("%d-%m-%Y")
                    return value  # keep string/None as is

                # Prepare emp_data (only once per employee)
                if emp_id not in employees:
                    emp_data = {
                        "user_id": row["user_id"],
                        "employee_id": row["employee_id"],
                        "full_name": row["full_name"],
                        "department": row["department"],
                        "designation": row["designation"],
                        "division": row["division"],
                        "date_of_joining": format_date(row["date_of_joining"]),
                        "headquarter": row["headquarter"],
                        "last_working_day": format_date(row["last_working_day"]),
                        "manager_emp_id": row["manager_emp_id"],
                        "manager_full_name": row["manager_full_name"],
                    }
                    employees[emp_id] = {"emp_data": emp_data, "data": []}

                # Append feedback
                employees[emp_id]["data"].append({
                    "ques_id": row["ques_id"],
                    "question": row["question"],
                    "answer": row["answer"],
                    "brief_answer": row["brief_answer"]
                })

            return Response({
                "status": True,
                "employees": list(employees.values())
            }, status=200)

        except Exception as e:
            return Response({"status": False, "error": str(e)}, status=500)




class HRAssetsDashboard(APIView):
    def get(self,request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("select constants_id,category_name from ci_erp_constants where type='assets_category';")
                assets_list=dictfetchall(cursor)


                # List of assets and their status as per employees whose last working day is present .
                cursor.execute("""
                       SELECT 
                            e.username AS employee_id,
                            CONCAT(e.first_name,' ',e.last_name) AS name,
                            a.id AS asset_id,
                            a.assets_category_id,
                            c.category_name AS Asset_name,
                            a.employee_confirmation,
                            CASE 
                                WHEN a.return_request_status = "2" THEN 'returned'
                                WHEN a.return_request_status = "1" THEN 'return_request'
                                ELSE 'pending' 
                            END AS return_status
                        FROM ci_resignations r
                        JOIN ci_erp_users e 
                            ON TRIM(r.employee_id) = TRIM(e.username)
                        JOIN ci_assets a 
                            ON e.username = a.employee_id
                        JOIN ci_erp_constants c 
                            ON a.assets_category_id = c.constants_id
                        WHERE r.last_working_day IS NOT NULL
                        ORDER BY e.id, a.id;
                        
                    """)

                assets_status=dictfetchall(cursor)
                return Response({"assets_list":assets_list,"assets_status":assets_status},status=200)
        except Exception as e:
            return Response({"error":str(e)},status=500)



class HRAssetsApprovalDashboard(APIView):
    def patch(self, request, pk):
        action = request.data.get("action", "").strip().lower()
 
       
        if action == "return_yes":
           
                with connection.cursor() as cursor:
                    #  Get brand_id for this asset
                    cursor.execute("""
                        SELECT brand_id , quantity
                        FROM ci_assets
                        WHERE id = %s
                    """, [pk])
                    row = cursor.fetchone()
                    if not row:
                        return Response({"error": "Asset not found."}, status=status.HTTP_404_NOT_FOUND)
   
                    # brand_id = row[0]
                    brand_id, quantity = row
   
                    #  Update asset return status
                    cursor.execute("""
                        UPDATE ci_assets
                        SET returned = 'Y', return_request_status = '2'
                        WHERE id = %s
                    """, [pk])
   
                    #  Update stock back in ci_erp_constants (increment by 1)
                    cursor.execute("""
                        UPDATE ci_erp_constants
                        SET field_one = COALESCE(field_one, 0) + %s
                        WHERE constants_id = %s
                    """, [quantity, brand_id])

                    # Update ci_employee_exit_final if all assets returned

                    # cursor.execute("select employee_id from ci_assets where id=%s",[pk])
                    # emp_id=cursor.fetchone()[0]

                    # cursor.execute("""select count(id) as accepted_count from ci_assets where employee_id=%s and employee_confirmation="accepted";""",[emp_id])

                    # accepted_count=cursor.fetchone()[0]


                    # cursor.execute("""select count(id) as returned_count from ci_assets where employee_id=%s and employee_confirmation="accepted" and return_request_status='2';""",[emp_id])

                    # returned_count=cursor.fetchone()[0]


                    # if accepted_count==returned_count:
                    #     cursor.execute("update ci_employee_exit_final set return_asset='Y' where employee_id=%s",[emp_id])
                    #     transaction.commit()

                return Response({
                    "message": "Return confirmed. Asset marked as returned and notifications sent."
                }, status=status.HTTP_200_OK)

        elif action == "return_no":
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE ci_assets
                        SET return_request_status = '0'
                        WHERE id = %s
                    """, [pk])
                return Response({"message": "Return request denied. Asset remains allocated."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    



class GetExitDate(APIView):
    def get(self, request, employee_id):
        try:
            with connection.cursor() as cursor:
                # Check both tables for exit date
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN r.last_working_day IS NOT NULL THEN DATE(r.last_working_day)
                            WHEN ee.exit_date IS NOT NULL THEN DATE(ee.exit_date)
                            ELSE 'NA'
                        END as last_working_day,
                        CASE 
                            WHEN r.last_working_day IS NOT NULL THEN 'ci_resignations'
                            WHEN ee.exit_date IS NOT NULL THEN 'ci_employee_exit'
                            ELSE 'none'
                        END as source_table
                    FROM (SELECT %s as employee_id) as emp
                    LEFT JOIN ci_resignations r ON emp.employee_id = r.employee_id
                    LEFT JOIN ci_employee_exit ee ON emp.employee_id = ee.employee_id
                """, [employee_id])
                
                result = cursor.fetchone()
                
                if result and result[0] != 'NA':
                    return Response({
                        "last_working_day": result[0],
                        "source_table": result[1]
                    }, status=200)
                else:
                    return Response({
                        "last_working_day": 'NA',
                        "source_table": 'none'
                    }, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
 



# class ResignedEmployeesDropdownAPIView(APIView):
#     """
#     API to fetch employees whose last_working_day is in the past
#     for showing in a dropdown.
#     """

#     def get(self, request):
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                    SELECT 
#                         u.id AS user_id,
#                         r.employee_id,
# 						CONCAT(u.first_name,' ',u.last_name) AS employee_name,
#                         r.last_working_day
#                     FROM ci_resignations r
#                     INNER JOIN ci_erp_users u ON r.employee_id = u.username
#                     WHERE r.last_working_day < CURRENT_DATE
#                     ORDER BY u.username ASC
#                 """)
#                 rows = cursor.fetchall()

#             data = [
#                 {
#                     "user_id": row[0],
#                     "employee_id": row[1],
#                     "employee_name": row[2],
#                     "last_working_day": row[3].strftime("%Y-%m-%d"),
#                 }
#                 for row in rows
#             ]

#             return Response(data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResignedEmployeesDropdownAPIView(APIView):
    """
    API to fetch employees:
    - Resignations: status=2 and last_working_day is in the past
    - Exit: exit_date is in the past and F&F is not completed
    """

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                # 🔹 Fetch resigned employees (status=2 and last_working_day < current date)
                cursor.execute("""
                    SELECT 
                        u.id AS user_id,
                        r.employee_id,
                        CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                        r.last_working_day AS date
                    FROM ci_resignations r
                    INNER JOIN ci_erp_users u ON r.employee_id = u.username
                    WHERE r.status = 2
                      AND r.last_working_day < CURRENT_DATE
                      -- Exclude employees already terminated
                      AND r.employee_id NOT IN (
                            SELECT employee_id FROM ci_terminations
                      )
                    ORDER BY u.username ASC
                """)
                resigned_rows = cursor.fetchall()

                # 🔹 Fetch exit employees (not completed F&F process)
                cursor.execute("""
                    SELECT 
                        u.id AS user_id,
                        e.employee_id,
                        CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                        e.exit_date AS date
                    FROM ci_employee_exit e
                    INNER JOIN ci_erp_users u ON e.employee_id = u.username
                    WHERE e.exit_date < CURRENT_DATE
                      -- Exclude employees already terminated
                      AND e.employee_id NOT IN (
                            SELECT employee_id FROM ci_terminations
                      )
                      -- Exclude employees whose F&F is completed
                      AND e.employee_id NOT IN (
                            SELECT employee_id
                            FROM ci_employee_exit_final
                            WHERE `f&f` = 'Y'
                      )
                    ORDER BY u.username ASC
                """)
                exit_rows = cursor.fetchall()

                # fetch inactive users in system
                cursor.execute("""
                    SELECT 
                        u.id AS user_id,
                        u.username AS employee_id,
                        CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                        NULL AS date,
                        'Inactive' AS type
                    FROM ci_erp_users u
                    WHERE u.is_active = 0
                    AND u.username NOT IN (SELECT employee_id FROM ci_terminations)
                    AND u.username NOT IN (
                            SELECT employee_id
                            FROM ci_employee_exit_final
                            WHERE `f&f` = 'Y')

                    ORDER BY u.username ASC
                """)
                inactive_user_rows = cursor.fetchall()

            # 🔹 Format resigned employees
            resigned_data = [
                {
                    "user_id": row[0],
                    "employee_id": row[1],
                    "employee_name": row[2],
                    "date": row[3].strftime("%Y-%m-%d") if row[3] else None,
                    "type": "Resigned",
                }
                for row in resigned_rows
            ]

            # 🔹 Format exit employees
            exit_data = [
                {
                    "user_id": row[0],
                    "employee_id": row[1],
                    "employee_name": row[2],
                    "date": row[3].strftime("%Y-%m-%d") if row[3] else None,
                    "type": "Exit",
                }
                for row in exit_rows
            ]

            inactive_user_data = [
                {
                    "user_id": row[0],
                    "employee_id": row[1],
                    "employee_name": row[2],
                    "date": row[3],  #already none
                    "type": "Inactive",
                }
                for row in inactive_user_rows
            ]


            # 🔹 Combine both lists
            combined_data = resigned_data + exit_data + inactive_user_data

            # 🔹 Sort by employee_id
            combined_data.sort(key=lambda x: x["employee_id"])

            return Response(combined_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ConfirmationEmployeesDropdownAPIView(APIView):
    """
    API to fetch employees whose probation is Y
    for showing in a dropdown.
    """

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                   SELECT 
                        u.id AS user_id,
                        ud.employee_id,
						CONCAT(u.first_name,' ',u.last_name) AS employee_name,
                        ud.probation
                    FROM ci_erp_users_details ud
                    INNER JOIN ci_erp_users u ON ud.employee_id = u.username
                    WHERE ud.probation = 'Y'
                    ORDER BY u.username ASC
                """)
                rows = cursor.fetchall()

            data = [
                {
                    "user_id": row[0],
                    "employee_id": row[1],
                    "employee_name": row[2],
                    "probation": row[3],
                }
                for row in rows
            ]

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ] 


class getletters(APIView):
    def post(self,request,employee_id):
        relieving_letter=request.data.get('relieving_letter')
        experience_letter=request.data.get('experience_letter')

        if not relieving_letter and not experience_letter:
            return Response({"error": "No files uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        upload_dir = os.path.join(settings.MEDIA_ROOT, "employee_letters")
        os.makedirs(upload_dir, exist_ok=True)

        # Domain 
        base_url = "https://tdtlworld.com/hrms-backend/media/employee_letters/"
        # base_url = "http://127.0.0.1:8000/media/employee_letters/"

        relieving_path = None
        experience_path = None

        # Save relieving letter
        if relieving_letter:
            filename = f"{employee_id}_relieving_letter{os.path.splitext(relieving_letter.name)[1]}"
            filepath = os.path.join(upload_dir, filename)
            with default_storage.open(filepath, "wb+") as dest:
                for chunk in relieving_letter.chunks():
                    dest.write(chunk)
            relieving_path = base_url + filename

        # Save experience letter
        if experience_letter:
            filename = f"{employee_id}_experience_letter{os.path.splitext(experience_letter.name)[1]}"
            filepath = os.path.join(upload_dir, filename)
            with default_storage.open(filepath, "wb+") as dest:
                for chunk in experience_letter.chunks():
                    dest.write(chunk)
            experience_path = base_url + filename

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_forms (employee_id, relieving_letter, experience_letter)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    relieving_letter = VALUES(relieving_letter),
                    experience_letter = VALUES(experience_letter)
            """, [employee_id, relieving_path, experience_path])

        return Response({
            "message": "Letters uploaded successfully",
            "relieving_letter": relieving_path,
            "experience_letter": experience_path
        }, status=status.HTTP_200_OK)
    
    def get(self,request):
        with connection.cursor() as cursor:
            cursor.execute("select * from ci_forms")
            rows=dictfetchall(cursor)
        return Response(rows,status=status.HTTP_200_OK)



class CheckAssetStatus(APIView):
    def get(self, request, employee_id):
        with connection.cursor() as cursor:
            cursor.execute("select id from ci_erp_users where username=%s",[employee_id])
            user_id=cursor.fetchone()

            cursor.execute("""select count(id) as accepted_count from ci_assets where employee_id=%s and employee_confirmation="accepted";""",[employee_id])
            accepted_count=cursor.fetchone()[0]

            cursor.execute("""select count(id) as returned_count from ci_assets where employee_id=%s and employee_confirmation="accepted" and return_request_status='2';""",[employee_id])
            returned_count=cursor.fetchone()[0]

            if accepted_count==returned_count:
                cursor.execute("select employee_exit_final_id from ci_employee_exit_final where employee_id=%s",[employee_id])
                exit_final=cursor.fetchone()
                if exit_final:
                    cursor.execute("update ci_employee_exit_final set return_asset='Y' where employee_id=%s",[employee_id])
                    message = "Record updated"
                else:
                    cursor.execute("""insert into ci_employee_exit_final(user_id,employee_id,return_asset) values(%s,%s,'Y')""",[user_id[0],employee_id])
                    message = "Record inserted"

                # ---- New Exit Type Logic ----
                exit_type = None

                # 1. Check in ci_employee_exit
                cursor.execute("SELECT exit_type_id FROM ci_employee_exit WHERE employee_id = %s", [employee_id])
                exit_row = cursor.fetchone()
                if exit_row:
                    exit_type = exit_row[0]
                else:
                    # 2. If not found, check ci_resignations
                    cursor.execute("SELECT resignation_id FROM ci_resignations WHERE employee_id = %s", [employee_id])
                    resign_row = cursor.fetchone()
                    if resign_row:
                        exit_type = 177

                # Update exit_type if found
                if exit_type:
                    cursor.execute("""
                        UPDATE ci_employee_exit_final
                        SET exit_type = %s
                        WHERE employee_id = %s
                    """, [exit_type, employee_id])

                return Response({"status":"Y","message":message})

            return Response({"status":"N","message":"Assets not fully returned"})



class TerminationDashboard(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        t.termination_id,
                        CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                        c.category_name AS exit_type,
                        t.date_of_termination,
                        t.reason_of_termination,
                        CASE 
                            WHEN t.mail_status = 0 THEN 'Pending'
                            WHEN t.mail_status = 1 THEN 'Send'
                        END AS mail_status,
                        t.created_at
                    FROM ci_terminations t
                    LEFT JOIN ci_erp_users u ON t.employee_id = u.username
                    LEFT JOIN ci_erp_constants c ON t.exit_type = c.constants_id
                """)

                rows = cursor.fetchall()

                if not rows:
                    return Response({"message": "No termination records found"}, status=status.HTTP_404_NOT_FOUND)

                # Safely get column names
                columns = [col[0] for col in cursor.description] if cursor.description else []
                result = [dict(zip(columns, row)) for row in rows]

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


    def post(self, request):
        data = request.data
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                        INSERT INTO ci_terminations 
                                (employee_id, exit_type, date_of_termination, reason_of_termination, created_at, mail_status)
                        VALUES
                                (%s, %s, %s, %s, %s, 0)
                    """, [
                        data["employee_id"],
                        data["exit_type"],
                        data["date_of_termination"],
                        data["reason_of_termination"],
                        datetime.now()
                    ])
            return Response({"message": "Termination created successfully."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
    # def patch(self, request, pk):
    #     action = request.data.get("action", "").strip().lower()

    #     if action == "send":
    #         try:
    #             with connection.cursor() as cursor:
    #                 cursor.execute("""
    #                     UPDATE ci_terminations 
    #                     SET mail_status = '1'
    #                     WHERE termination_id = %s
    #                     """, [pk])

    #             if cursor.rowcount == 0:
    #                     return Response({"error": "Termination not found"}, status=status.HTTP_404_NOT_FOUND)

    #             return Response({"message": "Mail status updated successfully."}, status=status.HTTP_200_OK)

    #         except Exception as e:
    #             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    #     return Response({"error": "Invalid action. Use 'send'."}, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk):
        action = request.data.get("action", "").strip().lower()

        if action == "send":
            try:
                with connection.cursor() as cursor:
                    # 1. Update mail_status in ci_terminations
                    cursor.execute("""
                        UPDATE ci_terminations 
                        SET mail_status = '1'
                        WHERE termination_id = %s
                    """, [pk])

                    if cursor.rowcount == 0:
                        return Response({"error": "Termination not found"}, status=status.HTTP_404_NOT_FOUND)

                    # 2. Get employee_id from ci_terminations
                    cursor.execute("""
                        SELECT employee_id
                        FROM ci_terminations
                        WHERE termination_id = %s
                    """, [pk])
                    employee = cursor.fetchone()

                    if not employee:
                        return Response({"error": "Employee not found for this termination"}, status=status.HTTP_404_NOT_FOUND)

                    employee_id = employee[0]

                    # 3. Deactivate employee in ci_erp_users by matching username with employee_id
                    cursor.execute("""
                        UPDATE ci_erp_users
                        SET is_active = 0
                        WHERE username = %s
                    """, [employee_id])

                    if cursor.rowcount == 0:
                        return Response({"error": "No matching user found in ci_erp_users"}, status=status.HTTP_404_NOT_FOUND)

                return Response({"message": "Mail status updated and employee deactivated successfully."},
                                status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Invalid action. Use 'send'."}, status=status.HTTP_400_BAD_REQUEST)



class PendingTerminationList(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        t.termination_id,
                        CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                        c.category_name AS exit_type,
                        t.date_of_termination,
                        t.reason_of_termination,
                        'Pending' AS mail_status,
                        t.created_at
                    FROM ci_terminations t
                    LEFT JOIN ci_erp_users u ON t.employee_id = u.username
                    LEFT JOIN ci_erp_constants c ON t.exit_type = c.constants_id
                    WHERE t.mail_status = 0
                """)

                rows = cursor.fetchall()
                if not rows:
                    return Response({"message": "No pending terminations found"}, status=status.HTTP_404_NOT_FOUND)

                columns = [col[0] for col in cursor.description] if cursor.description else []
                result = [dict(zip(columns, row)) for row in rows]

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendTerminationList(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        t.termination_id,
                        CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                        c.category_name AS exit_type,
                        t.date_of_termination,
                        t.reason_of_termination,
                        'Sent' AS mail_status,
                        t.created_at
                    FROM ci_terminations t
                    LEFT JOIN ci_erp_users u ON t.employee_id = u.username
                    LEFT JOIN ci_erp_constants c ON t.exit_type = c.constants_id
                    WHERE t.mail_status = 1
                """)

                rows = cursor.fetchall()
                if not rows:
                    return Response({"message": "No send terminations found"}, status=status.HTTP_404_NOT_FOUND)

                columns = [col[0] for col in cursor.description] if cursor.description else []
                result = [dict(zip(columns, row)) for row in rows]

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ExitEmployeeTable1(APIView):
    def get(self,request):
        with connection.cursor() as cursor:
            cursor.execute("""select f.employee_id,
                concat(u.first_name,' ',u.last_name) as employee_name,
                c.category_name as exit_type,
                f.return_asset,
                f.exit_interview_questionnaire,
                f.employee_clearance_form,
                    f.`f&f`
            from ci_employee_exit_final f
            left join ci_erp_users u on f.employee_id=u.username
            left join ci_erp_constants c on f.exit_type=c.constants_id;""")
            data=dictfetchall(cursor)
            return Response(data,status=200)
   
    def patch(self,request,employee_id):
        employee_clearance_form=request.data.get('employee_clearance_form')
        f_and_f=request.data.get('f_and_f')
        if not employee_clearance_form and not f_and_f:
            return Response({"error":"No fields to update"},status=400)
        with connection.cursor() as cursor:
            cursor.execute("select employee_exit_final_id from ci_employee_exit_final where employee_id=%s",[employee_id])
            exit_final=cursor.fetchone()
            if not exit_final:
                return Response({"error":"Employee not found in exit final table"},status=404)
            cursor.execute("""update ci_employee_exit_final set employee_clearance_form=%s,`f&f`=%s where employee_id=%s""",[employee_clearance_form,f_and_f,employee_id])
            return Response({"message":"Employee exit details updated successfully"},status=200)
       
from django.core.mail import EmailMessage  
class ExitEmployeeTable2(APIView):
    def get(self,request):
        with connection.cursor() as cursor:
            cursor.execute("""select f.employee_id,
                concat(u.first_name,' ',u.last_name) as employee_name,
                c.category_name as exit_type,
                f.return_asset,
                f.exit_interview_questionnaire,
                f.employee_clearance_form,
                    f.`f&f`,
                    f.relieving_letter
            from ci_employee_exit_final f
            left join ci_erp_users u on f.employee_id=u.username
            left join ci_erp_constants c on f.exit_type=c.constants_id
            where f.`f&f`='Y';""")
            data=dictfetchall(cursor)
            return Response(data,status=200)
 
    def patch(self, request, employee_id):
        relieving_letter = request.data.get('relieving_letter')
 
        if not relieving_letter:
            return Response({"error": "No fields to update"}, status=400)
       
        with connection.cursor() as cursor:
            cursor.execute("select employee_exit_final_id from ci_employee_exit_final where employee_id=%s", [employee_id])
            exit_final = cursor.fetchone()
            if not exit_final:
                return Response({"error": "Employee not found in exit final table"}, status=404)
       
        upload_dir = os.path.join(settings.MEDIA_ROOT, "employee_letters")
        os.makedirs(upload_dir, exist_ok=True)
        # base_url = "http://127.0.0.1:8000/media/employee_letters/"
        base_url = "https://tdtlworld.com/hrms-backend/media/employee_letters/"
 
 
        relieving_path = None
        if relieving_letter:
            filename = f"{employee_id}_relieving_letter{os.path.splitext(relieving_letter.name)[1]}"
            filepath = os.path.join(upload_dir, filename)
            with default_storage.open(filepath, "wb+") as dest:
                for chunk in relieving_letter.chunks():
                    dest.write(chunk)
            relieving_path = base_url + filename
           
            with connection.cursor() as cursor:
                cursor.execute("""update ci_employee_exit_final set relieving_letter=%s where employee_id=%s""", [relieving_path, employee_id])
           
            with connection.cursor() as cursor:
                cursor.execute("""update ci_erp_users set is_active=0 where username=%s""", [employee_id])
 
        # NEW LOGIC: Send email with PDF attachment (EXACT same format as assets API)
        try:
            # Get employee email and name
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT first_name, last_name, email
                    FROM ci_erp_users
                    WHERE username = %s
                """, [employee_id])
                employee_data = cursor.fetchone()
           
            if employee_data:
                first_name, last_name, email = employee_data
                employee_name = f"{first_name} {last_name}"
               
                # Exact same format as assets API
                subject = f"Relieving Letter - {employee_name}"
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2>Relieving Letter</h2>
                    <p>Dear <b>{employee_name}</b>,</p>
                   
                    <p>Please find your relieving letter attached with this email.</p>
                   
                    <div style="margin: 15px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
                        <p><b>Employee ID:</b> {employee_id}</p>
                        <p><b>Document:</b> Relieving Letter</p>
                    </div>
                   
                    <p style="color: #3794ff; font-weight: bold;">
                        This document is important for your future employment references.
                    </p>
                   
                    <p>If you have any questions, kindly contact the HR department.</p>
                   
                    <p>Best regards,</p>
                    <div style="margin: 10px 0;">
                        <img src="cid:company_logo" alt="Vetrina Logo" style="width:150px; height:auto;">
                    </div>
                    <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
                    <div style="margin-top:20px; font-size:12px; color:#b380ff; text-align:center;">
                        © 2025 Vetrina Healthcare Pvt. Ltd. All rights reserved.
                    </div>
                </body>
                </html>
                """
               
                # EXACT same email sending logic as assets API
                from django.core.mail import EmailMultiAlternatives
                from email.mime.image import MIMEImage
               
                msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [email])
                msg.attach_alternative(html_content, "text/html")
 
                # Attach logo inline (EXACT same as assets API)
                logo_path = os.path.join(settings.MEDIA_ROOT, "logo", "vetrina_logo.png")
                if os.path.exists(logo_path):
                    with open(logo_path, 'rb') as f:
                        logo_data = f.read()
                    image = MIMEImage(logo_data)
                    image.add_header('Content-ID', '<company_logo>')
                    image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
                    msg.attach(image)
 
                # Attach PDF file
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as pdf_file:
                        msg.attach(
                            filename=filename,
                            content=pdf_file.read(),
                            mimetype='application/pdf'
                        )
 
                msg.send(fail_silently=False)
               
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
 
        return Response({
            "message": "Employee exit details updated successfully",
            "relieving_letter": relieving_path
        }, status=200)
 
class ExitEmployeeTable3(APIView):
    def get(self,request):
        with connection.cursor() as cursor:
            cursor.execute("""select f.employee_id,
                concat(u.first_name,' ',u.last_name) as employee_name,
                c.category_name as exit_type,
                f.return_asset,
                f.exit_interview_questionnaire,
                f.employee_clearance_form,
                    f.`f&f`,
                    f.relieving_letter,
                    f.experience_letter
            from ci_employee_exit_final f
            left join ci_erp_users u on f.employee_id=u.username
            left join ci_erp_constants c on f.exit_type=c.constants_id
            where f.relieving_letter is not null;""")
            data=dictfetchall(cursor)
            return Response(data,status=200)
 
    def patch(self, request, employee_id):
        experience_letter = request.data.get('experience_letter')
 
        if not experience_letter:
            return Response({"error": "No fields to update"}, status=400)
       
        with connection.cursor() as cursor:
            cursor.execute("select employee_exit_final_id from ci_employee_exit_final where employee_id=%s", [employee_id])
            exit_final = cursor.fetchone()
            if not exit_final:
                return Response({"error": "Employee not found in exit final table"}, status=404)
       
        upload_dir = os.path.join(settings.MEDIA_ROOT, "employee_letters")
        os.makedirs(upload_dir, exist_ok=True)
        base_url = "https://tdtlworld.com/hrms-backend/media/employee_letters/"
        # base_url = "http://127.0.0.1:8000/media/employee_letters/"
 
 
        experience_path = None
        if experience_letter:
            filename = f"{employee_id}_experience_letter{os.path.splitext(experience_letter.name)[1]}"
            filepath = os.path.join(upload_dir, filename)
            with default_storage.open(filepath, "wb+") as dest:
                for chunk in experience_letter.chunks():
                    dest.write(chunk)
            experience_path = base_url + filename
           
            with connection.cursor() as cursor:
                cursor.execute("""update ci_employee_exit_final set experience_letter=%s where employee_id=%s""", [experience_path, employee_id])
 
        # NEW LOGIC: Send email with PDF attachment (EXACT same format as assets API)
        try:
            # Get employee email and name
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT first_name, last_name, email
                    FROM ci_erp_users
                    WHERE username = %s
                """, [employee_id])
                employee_data = cursor.fetchone()
           
            if employee_data:
                first_name, last_name, email = employee_data
                employee_name = f"{first_name} {last_name}"
               
                # Exact same format as assets API
                subject = f"Experience Letter - {employee_name}"
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2>Experience Letter</h2>
                    <p>Dear <b>{employee_name}</b>,</p>
                   
                    <p>Please find your experience letter attached with this email.</p>
                   
                    <div style="margin: 15px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
                        <p><b>Employee ID:</b> {employee_id}</p>
                        <p><b>Document:</b> Experience Letter</p>
                    </div>
                   
                    <p style="color: #3794ff; font-weight: bold;">
                        This document is important for your future employment references.
                    </p>
                   
                    <p>If you have any questions, kindly contact the HR department.</p>
                   
                    <p>Best regards,</p>
                    <div style="margin: 10px 0;">
                        <img src="cid:company_logo" alt="Vetrina Logo" style="width:150px; height:auto;">
                    </div>
                    <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
                    <div style="margin-top:20px; font-size:12px; color:#b380ff; text-align:center;">
                        © 2025 Vetrina Healthcare Pvt. Ltd. All rights reserved.
                    </div>
                </body>
                </html>
                """
               
                # EXACT same email sending logic as assets API
                from django.core.mail import EmailMultiAlternatives
                from email.mime.image import MIMEImage
               
                msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [email])
                msg.attach_alternative(html_content, "text/html")
 
                # Attach logo inline (EXACT same as assets API)
                logo_path = os.path.join(settings.MEDIA_ROOT, "logo", "vetrina_logo.png")
                if os.path.exists(logo_path):
                    with open(logo_path, 'rb') as f:
                        logo_data = f.read()
                    image = MIMEImage(logo_data)
                    image.add_header('Content-ID', '<company_logo>')
                    image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
                    msg.attach(image)
 
                # Attach PDF file
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as pdf_file:
                        msg.attach(
                            filename=filename,
                            content=pdf_file.read(),
                            mimetype='application/pdf'
                        )
 
                msg.send(fail_silently=False)
               
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
 
        return Response({
            "message": "Employee exit details updated successfully",
            "experience_letter": experience_path
        }, status=200)
 
 

class ExitEmployeeDashboardFinalTable(APIView):
    def get(self,request):
        with connection.cursor() as cursor:
            cursor.execute("""select f.employee_id,
                concat(u.first_name,' ',u.last_name) as employee_name,
                c.category_name as exit_type,
                f.return_asset,
                f.exit_interview_questionnaire,
                f.employee_clearance_form,
                    f.`f&f`,
                    f.relieving_letter,
                    f.experience_letter,
                    f.clearance_form
            from ci_employee_exit_final f
            left join ci_erp_users u on f.employee_id=u.username
            left join ci_erp_constants c on f.exit_type=c.constants_id
            where f.experience_letter is not null;""")
            data=dictfetchall(cursor)
            return Response(data,status=200)
 


class HRExitEmployee(APIView):
    def post(self, request):
            data = request.data
            required_fields = [
                "employee_id","employee_name", "exit_date", "exit_type_id",
                "reason",
            
            ]

            # Check for missing required fields
            missing = [field for field in required_fields if not data.get(field)]
            if missing:
                return Response({"error": f"Missing fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

            company_id = 2  # Default
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_employee_exit (
                        company_id, employee_id, employee_name, exit_date, exit_type_id,
                        reason, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [
                    company_id,
                    data["employee_id"],
                    data["employee_name"],
                    data["exit_date"],
                    data["exit_type_id"],
                    data["reason"],
                    created_at
                ])

            return Response({"message": "Employee exit record created successfully."}, status=status.HTTP_201_CREATED)


class UploadClearanceForm(APIView):

    def patch(self, request, employee_id):
        clearance_form = request.data.get('clearance_form')
 
        if not clearance_form:
            return Response({"error": "No fields to update"}, status=400)
       
        with connection.cursor() as cursor:
            cursor.execute("select employee_exit_final_id from ci_employee_exit_final where employee_id=%s", [employee_id])
            exit_final = cursor.fetchone()
            if not exit_final:
                return Response({"error": "Employee not found in exit final table"}, status=404)
       
        upload_dir = os.path.join(settings.MEDIA_ROOT, "employee_letters")
        os.makedirs(upload_dir, exist_ok=True)
        base_url = "https://tdtlworld.com/hrms-backend/media/employee_letters/"
        # base_url = "http://127.0.0.1:8000/media/employee_letters/"
 
 
        clearance_path = None
        if clearance_form:
            filename = f"{employee_id}_clearance_form{os.path.splitext(clearance_form.name)[1]}"
            filepath = os.path.join(upload_dir, filename)
            with default_storage.open(filepath, "wb+") as dest:
                for chunk in clearance_form.chunks():
                    dest.write(chunk)
            clearance_path = base_url + filename
           
            with connection.cursor() as cursor:
                cursor.execute("""update ci_employee_exit_final set clearance_form=%s where employee_id=%s""", [clearance_path, employee_id])
 
        return Response({
            "message": "Employee exit details updated successfully",
            "clearance_form": clearance_path
        }, status=200) 




# class UploadHRSignAPIView(APIView):

#     def patch(self, request, employee_id):
#         # Get the sign file from the request
#         sign_file = request.data.get('sign')

#         if not sign_file:
#             return Response({"error": "No sign file provided."}, status=status.HTTP_400_BAD_REQUEST)


#         # Create folder for sign if it doesn't exist
#         upload_dir = os.path.join(settings.MEDIA_ROOT, "sign")
#         os.makedirs(upload_dir, exist_ok=True)

#         # Set the base URL for accessing the file
#         base_url = "https://tdtlworld.com/hrms-backend/media/sign/"
#         # base_url = "http://127.0.0.1:8000/media/sign/"

#         # Save the file
#         filename = f"{employee_id}_sign{os.path.splitext(sign_file.name)[1]}"
#         filepath = os.path.join(upload_dir, filename)

#         with default_storage.open(filepath, "wb+") as dest:
#             for chunk in sign_file.chunks():
#                 dest.write(chunk)

#         # Full path to be stored in DB
#         sign_path = base_url + filename

#         # Update the sign column in ci_erp_users_details
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 UPDATE ci_erp_users_details
#                 SET sign = %s
#                 WHERE employee_id = %s
#             """, [sign_path, employee_id])

#         return Response({
#             "message": "HR sign uploaded successfully.",
#             "sign": sign_path
#         }, status=status.HTTP_200_OK)
    
class UploadHRSignAPIView(APIView):


    def get(self, request, employee_id):
        """
        Fetch HR sign for the given employee_id
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT sign
                    FROM ci_erp_users_details
                    WHERE employee_id = %s
                """, [employee_id])
                row = cursor.fetchone()

            if not row or not row[0]:
                return Response(
                    {"error": "Sign not found for this employee."},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {"employee_id": employee_id, "sign": row[0]},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, employee_id):
        # Get the sign file from the request
        sign_file = request.data.get('sign')

        if not sign_file:
            return Response({"error": "No sign file provided."}, status=status.HTTP_400_BAD_REQUEST)


        # Create folder for sign if it doesn't exist
        upload_dir = os.path.join(settings.MEDIA_ROOT, "sign")
        os.makedirs(upload_dir, exist_ok=True)

        # Set the base URL for accessing the file
        base_url = "https://tdtlworld.com/hrms-backend/media/sign/"
        # base_url = "http://127.0.0.1:8000/media/sign/"

        # Save the file
        filename = f"{employee_id}_sign{os.path.splitext(sign_file.name)[1]}"
        filepath = os.path.join(upload_dir, filename)

        with default_storage.open(filepath, "wb+") as dest:
            for chunk in sign_file.chunks():
                dest.write(chunk)

        # Full path to be stored in DB
        sign_path = base_url + filename

        # Update the sign column in ci_erp_users_details
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE ci_erp_users_details
                SET sign = %s
                WHERE employee_id = %s
            """, [sign_path, employee_id])

        return Response({
            "message": "HR sign uploaded successfully.",
            "sign": sign_path
        }, status=status.HTTP_200_OK)
 

class UploadCompanyStampAPIView(APIView):

    def patch(self, request, company_detail_id):
        # Get the stamp file from the request
        stamp_file = request.data.get('stamp')

        if not stamp_file:
            return Response({"error": "No stamp file provided."}, status=status.HTTP_400_BAD_REQUEST)

       
        # Create folder for sign if it doesn't exist
        upload_dir = os.path.join(settings.MEDIA_ROOT, "stamp")
        os.makedirs(upload_dir, exist_ok=True)

        # Set the base URL for accessing the file
        base_url = "https://tdtlworld.com/hrms-backend/media/stamp/"
        # base_url = "http://127.0.0.1:8000/media/stamp/"

        # Save the file
        filename = f"{company_detail_id}_stamp{os.path.splitext(stamp_file.name)[1]}"
        filepath = os.path.join(upload_dir, filename)

        with default_storage.open(filepath, "wb+") as dest:
            for chunk in stamp_file.chunks():
                dest.write(chunk)

        # Full path to be stored in DB
        stamp_path = base_url + filename

        # Update the stamp column in ci_company_details
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE ci_company_details
                SET company_stamp = %s
                WHERE company_detail_id = %s
            """, [stamp_path, company_detail_id])

        return Response({
            "message": "Stamp uploaded successfully.",
            "stamp": stamp_path
        }, status=status.HTTP_200_OK)


def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dicts"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def dictfetchone(cursor):
    """Return a single row from a cursor as a dict"""
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))

class DataForLetterAPIView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, employee_id):
        # hr_user_id=self.request.GET.get('user_id')
        hr_user_id=request.user.id
        print("hr_id",hr_user_id)
        with connection.cursor() as cursor:
            cursor.execute(""" 
                select 
                    u.id, 
                    CASE 
                        WHEN u.gender = 1 THEN 'Male'
                        WHEN u.gender = 2 THEN 'Female'
                        ELSE 'Other'
                    END AS gender, 
                    concat(u.first_name,' ',u.last_name) as hr_name ,
                    cd.designation_name ,
                    d.sign 
                from ci_erp_users u 
                left join ci_erp_users_details d on u.id=d.user_id 
                left join ci_designations cd on d.designation_id=cd.designation_id
                where u.id=%s
            """,[hr_user_id])
            hr_data=dictfetchone(cursor)

            cursor.execute("""select c.company_stamp from ci_company_details c """)
            company_stamp=dictfetchone(cursor)

            cursor.execute("""
                select 
                    d.employee_id, 
                    concat(u.first_name,' ',u.last_name) as employee_name ,
                    cd.designation_name ,
                    u.email, 
                    CASE 
                        WHEN u.gender = 1 THEN 'Male'
                        WHEN u.gender = 2 THEN 'Female'
                        ELSE 'Other'
                    END AS gender,
                    d.date_of_joining ,
                    u.address_1 
                from ci_erp_users u
                left join ci_erp_users_details d on u.id = d.user_id 
                left join ci_designations cd on d.designation_id=cd.designation_id
                where u.username=%s
            """,[employee_id])
            emp_data=dictfetchone(cursor)



            cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN r.last_working_day IS NOT NULL THEN DATE(r.last_working_day)
                            WHEN ee.exit_date IS NOT NULL THEN DATE(ee.exit_date)
                            ELSE 'NA'
                        END as last_working_day,
                        CASE 
                            WHEN r.last_working_day IS NOT NULL THEN 'ci_resignations'
                            WHEN ee.exit_date IS NOT NULL THEN 'ci_employee_exit'
                            ELSE 'none'
                        END as source_table
                    FROM (SELECT %s as employee_id) as emp
                    LEFT JOIN ci_resignations r ON emp.employee_id = r.employee_id
                    LEFT JOIN ci_employee_exit ee ON emp.employee_id = ee.employee_id
                """, [employee_id])
                
            last_working_date = cursor.fetchone()

            return Response({"hr_data":hr_data,"company_stamp":company_stamp,"emp_data":emp_data,"last_working_date":last_working_date})



##=====fetch all employee in the exit process
class GetEmployeeExitView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # -------------------- GET --------------------
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    e.exit_id, 
                    e.company_id, 
                    e.employee_id,
                    e.employee_name ,
                    e.exit_date, 
                    e.exit_type_id,
                    c.category_name AS exit_type_name,
                    e.sub_exit_type_id,
                    e.reason, 
                    e.created_at
                FROM 
                    ci_employee_exit e
                LEFT JOIN 
                    ci_erp_users u ON u.id = e.employee_id
                LEFT JOIN 
                    ci_erp_constants c ON c.constants_id = e.exit_type_id AND c.type = 'exit_type'
                ORDER BY 
                    STR_TO_DATE(e.created_at, '%Y-%m-%d %H:%i:%s') DESC
            """)
            rows = cursor.fetchall()

        columns = [
            "exit_id", "company_id", "employee_id", "employee_name",
            "exit_date", "exit_type_id", "exit_type_name", "sub_exit_type_id",
            "reason", "created_at"
        ]

        data = [dict(zip(columns, row)) for row in rows]

        return Response(data, status=status.HTTP_200_OK)



##===add new employee in exit process
class AddEmployeeExitView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        required_fields = [
            "employee_id", "employee_name", "exit_date", "exit_type_id", "reason"
        ]

        # Check for missing required fields
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return Response({"error": f"Missing fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

        company_id = 2  # Default company
        sub_exit_type_id = data.get("sub_exit_type_id")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_employee_exit (
                    company_id, employee_id, employee_name, exit_date, exit_type_id,
                    sub_exit_type_id, reason, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                company_id,
                data["employee_id"],
                data["employee_name"],
                data["exit_date"],
                data["exit_type_id"],
                sub_exit_type_id,
                data["reason"],
                created_at
            ])

        return Response({"message": "Employee exit record created successfully."}, status=status.HTTP_201_CREATED)


##====update and delete exit employee
class UpdateEmployeeExitView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, exit_id):
        data = request.data
        allowed_fields = [
            "employee_id", "exit_date", "exit_type_id",
            "sub_exit_type_id", "reason"
        ]

        fields = []
        values = []

        for field in allowed_fields:
            if field in data:
                fields.append(f"{field} = %s")
                values.append(data[field])

        if not fields:
            return Response({"error": "No valid fields provided for update."}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            # Check if the record exists
            cursor.execute("SELECT COUNT(*) FROM ci_employee_exit WHERE exit_id = %s", [exit_id])
            if cursor.fetchone()[0] == 0:
                return Response({"error": "Exit record not found."}, status=status.HTTP_404_NOT_FOUND)

            # Perform the update
            query = f"UPDATE ci_employee_exit SET {', '.join(fields)} WHERE exit_id = %s"
            values.append(exit_id)
            cursor.execute(query, values)

        return Response({"message": "Employee exit record updated successfully."}, status=status.HTTP_200_OK)

    # -------------------- DELETE --------------------
    def delete(self, request, exit_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ci_employee_exit WHERE exit_id = %s", [exit_id])
            if cursor.fetchone()[0] == 0:
                return Response({"error": "Exit record not found"}, status=status.HTTP_404_NOT_FOUND)

            cursor.execute("DELETE FROM ci_employee_exit WHERE exit_id = %s", [exit_id])
        return Response({"message": "Exit record deleted successfully."}, status=status.HTTP_200_OK)


################  FORGOT PASSWORD

import random
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.db import connection # Import for raw SQL
from django.utils.timezone import now, make_aware, get_current_timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Import the bcrypt helper functions
import bcrypt

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user_exists = False
        with connection.cursor() as cursor:
            # Check ci_erp_users table
            cursor.execute("SELECT email FROM ci_erp_users WHERE email = %s LIMIT 1", [email])
            if cursor.fetchone():
                user_exists = True

            # # Check ci_erp_user_details table (if applicable for users without direct email in main table)
            # if not user_exists:
            #     cursor.execute("SELECT email FROM ci_erp_users_details WHERE email = %s LIMIT 1", [email])
            #     if cursor.fetchone():
            #         user_exists = True

        if not user_exists:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a random OTP
        otp = str(random.randint(100000, 999999))  # Generate 6-digit OTP

        # Set expiration time for OTP (e.g., 10 minutes)
        # MySQL DATETIME columns typically store naive datetimes.
        # Django's timezone.now() will respect USE_TZ setting.
        # If USE_TZ=True, Django will convert it to the default timezone for saving.
        expires_at = now() + timedelta(minutes=10)
        created_at = now()

        # Store the OTP in the database (assuming a 'password_reset_tokens' table exists)
        # MySQL table creation example below.
        with connection.cursor() as cursor:
            # For MySQL, use %s placeholders, same as PostgreSQL
            cursor.execute(
                "INSERT INTO ci_password_reset_tokens (email, otp, expires_at, created_at) VALUES (%s, %s, %s, %s)",
                [email, otp, expires_at, created_at]
            )

        # Send the OTP to the user
        try:
            send_mail(
                'Password Reset OTP',
                f'Your OTP to reset your password is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error if email sending fails
            print(f"Error sending email: {e}")
            return Response({'error': 'Failed to send OTP email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'OTP sent to email.'}, status=status.HTTP_200_OK)


from datetime import datetime
from django.utils.timezone import make_aware, get_current_timezone, now

class ResetPasswordConfirmView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp, new_password]):
            return Response({'error': 'Email, OTP, and new password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        valid_token_found = False
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT expires_at FROM ci_password_reset_tokens WHERE email = %s AND otp = %s ORDER BY expires_at DESC LIMIT 1",
                [email, otp]
            )
            token_record = cursor.fetchone()

            if token_record:
                naive_expires_at = token_record[0]

                # ✅ Convert string to datetime if necessary
                if isinstance(naive_expires_at, str):
                    try:
                        naive_expires_at = datetime.strptime(naive_expires_at, "%Y-%m-%d %H:%M")
                    except ValueError:
                        # Handle MySQL microsecond format
                        naive_expires_at = datetime.strptime(naive_expires_at, "%Y-%m-%d %H:%M")

                # ✅ Make it timezone-aware
                aware_expires_at = make_aware(naive_expires_at, get_current_timezone())

                if now() < aware_expires_at:
                    valid_token_found = True
                    cursor.execute(
                        "DELETE FROM ci_password_reset_tokens WHERE email = %s AND otp = %s",
                        [email, otp]
                    )
            else:
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        if not valid_token_found:
            return Response({'error': 'OTP expired or invalid.'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Hash the new password properly
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        update_successful = False
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE ci_erp_users SET password = %s WHERE email = %s",
                [hashed_password, email]
            )
            if cursor.rowcount > 0:
                update_successful = True
            else:
                cursor.execute(
                    "UPDATE ci_erp_user_details SET password = %s WHERE email = %s",
                    [hashed_password, email]
                )
                if cursor.rowcount > 0:
                    update_successful = True

        if not update_successful:
            return Response({'error': 'Failed to update password. User not found or no change.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)
 