
import json
from django.db import connection
from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView

# Helper function to convert cursor results to a list of dictionaries
def dictfetchall(cursor):
    """
    Return all rows from a cursor as a list of dictionaries.
    This is very useful for building API responses.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]



class AnnouncementApiView(APIView):

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to fetch all announcements.
        """
        # We use a raw SQL query to get exactly what we want.
        # Joining with the department table to get the department name.
        # Using aliases (a, d) makes the query cleaner.
        sql_query = """
            SELECT
                ci.announcement_id,
                ci.department_id,   -- <<<  ADD THIS LINE TO GET THE ID
                ci.title,
                d.department_name,
                ci.start_date,
                ci.end_date,
                ci.summary,
                ci.description
            FROM
                ci_announcements AS ci
            LEFT JOIN
                ci_departments AS d ON ci.department_id = d.department_id
            ORDER BY
                ci.start_date ;
        """

        # The 'with' statement ensures the cursor is closed automatically
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            
            # Use the helper function to get a list of dictionaries
            announcements_list = dictfetchall(cursor)

        # Return the data as a JSON response.
        # safe=False is required when you are returning a list object.
        return JsonResponse(announcements_list, safe=False, json_dumps_params={'indent': 2})



     # --- NEW POST METHOD to Add an Announcement ---
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new announcement.
        """
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)

        title = data.get('title')
        department_id = data.get('department_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        summary = data.get('summary')
        description = data.get('description', '')

        if not all([title, department_id, start_date, end_date, summary]):
            return JsonResponse({'error': 'Missing required fields: title, department_id, start_date, end_date, summary'}, status=400)
        
        company_id = 2
        published_by = request.user.id if request.user.is_authenticated else 1

        # --- THE FIX IS IN THESE NEXT TWO BLOCKS ---

        # 1. Add `created_at` to the list of columns
        sql_query = """
            INSERT INTO ci_announcements
            (company_id, title, department_id, start_date, end_date, summary, description, published_by, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        
        # 2. Add the corresponding value for `created_at` to the params list
        params = [
            company_id,
            title,
            department_id,
            start_date,
            end_date,
            summary,
            description,
            published_by,
            1,
            datetime.now()  # Provide the current date and time
        ]

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, params)
                new_announcement_id = cursor.lastrowid
        except Exception as e:
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
        
        return JsonResponse({
            'message': 'Announcement created successfully!',
            'announcement_id': new_announcement_id,
            'title': title
        }, status=201)




from datetime import date, datetime


def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dictionaries."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

# Helper function for a SINGLE row (for your detail view)
def dictfetchone(cursor):
    """
    Return one row from a cursor as a dictionary.
    Returns None if no row is found.
    """
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


# Your view for getting a single announcement's details
class AnnouncementDetailApiView(View):

    def get(self, request, announcement_id, *args, **kwargs):
        """
        Handles GET requests to fetch the details of a SINGLE announcement
        based on the announcement_id provided in the URL.
        """
        sql_query = """
            SELECT
                ci.announcement_id,
                ci.title,
                ci.start_date,
                ci.end_date,
                ci.created_at,
                ci.summary,
                ci.description,
                d.department_name
            FROM
                ci_announcements AS ci
            LEFT JOIN
                ci_departments AS d ON ci.department_id = d.department_id
            WHERE
                ci.announcement_id = %s;
        """

        with connection.cursor() as cursor:
            cursor.execute(sql_query, [announcement_id])
            
            # This line will now work because dictfetchone is defined above
            announcement = dictfetchone(cursor)

        if announcement is None:
            return JsonResponse({'error': 'Announcement not found'}, status=404)

        for key, value in announcement.items():
            if isinstance(value, (date, datetime)):
                announcement[key] = value.strftime('%d-%m-%Y')

        return JsonResponse(announcement, json_dumps_params={'indent': 2})
    




    # PUT: Update an existing announcement
    def put(self, request, announcement_id, *args, **kwargs):
        """
        Handles PUT requests to update an existing announcement.
        """
        try:
            # Load the incoming JSON data from the request body
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Extract data from the JSON, matching your form fields
        title = data.get('title')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        department_id = data.get('department_id')
        summary = data.get('summary')
        description = data.get('description')

        # Basic validation to ensure required fields are present
        if not all([title, start_date, end_date, department_id, summary]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        sql_query = """
            UPDATE ci_announcements
            SET
                title = %s,
                start_date = %s,
                end_date = %s,
                department_id = %s,
                summary = %s,
                description = %s
            WHERE
                announcement_id = %s;
        """
        
        params = [title, start_date, end_date, department_id, summary, description, announcement_id]

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            # Check if any row was actually updated
            if cursor.rowcount == 0:
                return JsonResponse({'error': 'Announcement not found or no changes made'}, status=404)

        return JsonResponse({'message': 'Announcement updated successfully', 'announcement_id': announcement_id})




    # DELETE: Delete an existing announcement
    def delete(self, request, announcement_id, *args, **kwargs):
        """
        Handles DELETE requests to remove an announcement.
        """
        sql_query = "DELETE FROM ci_announcements WHERE announcement_id = %s;"
        
        with connection.cursor() as cursor:
            cursor.execute(sql_query, [announcement_id])
            # Check if a row was actually deleted
            if cursor.rowcount == 0:
                return JsonResponse({'error': 'Announcement not found'}, status=404)

        # A 204 No Content response is standard for successful deletions
        return JsonResponse({'message': 'Announcement deleted successfully'}, status=200) # or status=204



########################   policy





# your_app/views.py

import json
from django.db import connection
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from datetime import date, datetime
from django.core.files.storage import default_storage
from rest_framework.views import APIView

# --- Helper functions (You already have these) ---
def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dictionaries."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dictfetchone(cursor):
    """Return one row from a cursor as a dictionary."""
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))

# --- API View for getting the LIST of all policies ---
class PolicyListApiView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to fetch a list of all policies.
        """
        # The title is formatted here to match your UI ("001 - TITLE")
        sql_query = """
            SELECT
                policy_id,
                -- Use LPAD to add leading zeros and CONCAT for formatting
                CONCAT(LPAD(policy_id, 3, '0'), ' - ', title) as formatted_title,
                created_at
            FROM
                ci_policies
            ORDER BY
                policy_id ASC;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            policies_list = dictfetchall(cursor)

        # Convert date objects to strings for clean JSON output
        for policy in policies_list:
            if policy.get('created_at') and isinstance(policy['created_at'], (date, datetime)):
                policy['created_at'] = policy['created_at'].strftime('%d-%m-%Y')

        return JsonResponse(policies_list, safe=False)
    



################    added policies

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new policy with a file upload.
        """
        title = request.POST.get('title')
        description = request.POST.get('description')
        attachment_file = request.FILES.get('attachment')

        if not all([title, description, attachment_file]):
            return JsonResponse({'error': 'Title, Description, and Attachment are required.'}, status=400)

        file_path = f"policies/{attachment_file.name}"
        saved_path = default_storage.save(file_path, attachment_file)

        # SQL query is correct, no changes needed here
        sql_query = """
            INSERT INTO ci_policies
            (company_id, title, description, attachment, created_at, added_by)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        
        # --- THIS IS THE CORRECTED PART ---
        # The order of values now matches the order of columns
        params = [
            2,                # company_id
            title,            # title
            description,      # description
            saved_path,       # attachment
            datetime.now(),   # created_at
            2                 # added_by (assuming user ID is 2 for now)
        ]

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, params)
                new_policy_id = cursor.lastrowid
        except Exception as e:
            if default_storage.exists(saved_path):
                default_storage.delete(saved_path)
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)
        
        return JsonResponse({
            'message': 'Policy created successfully!',
            'policy_id': new_policy_id,
            'title': title,
            'attachment_path': saved_path
        }, status=201)



class PolicyDetailApiView(View):
    def get(self, request, policy_id, *args, **kwargs):
        """
        Handles GET requests to fetch all details of a single policy.
        """
        sql_query = """
            SELECT
                p.policy_id,
                CONCAT(LPAD(p.policy_id, 3, '0'), ' - ', p.title) as formatted_title,
                p.title,
                p.description,
                p.attachment, -- This will be the raw path from the DB
                p.created_at,
                d.department_name
            FROM
                ci_policies AS p
            LEFT JOIN
                ci_departments AS d ON p.company_id = d.department_id
            WHERE
                p.policy_id = %s;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(sql_query, [policy_id])
            policy = dictfetchone(cursor)

        if policy is None:
            return JsonResponse({'error': 'Policy not found'}, status=404)

        # --- IMPORTANT: Build the full attachment URL ---
        if policy.get('attachment'):
            # This combines your domain, media url, and file path into a full, clickable URL
            # e.g., "http://127.0.0.1:8000/media/policies/document.pdf"
            policy['attachment_url'] = request.build_absolute_uri(f"{settings.MEDIA_URL}{policy['attachment']}")
        else:
            policy['attachment_url'] = None
        
        # Format dates
        if policy.get('created_at') and isinstance(policy['created_at'], (date, datetime)):
            policy['created_at'] = policy['created_at'].strftime('%d-%m-%Y')

        return JsonResponse(policy)
    












# your_app/views.py

import json
from django.db import connection
from django.http import JsonResponse
from django.views import View
from datetime import date, datetime
from collections import defaultdict


# --- Helper function to convert cursor results to a list of dictionaries ---
def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dictionaries."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

# --- API View for getting the LIST of all policy acknowledgements ---
class PolicyAcknowledgeListView(View):

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to fetch all policy acknowledgement records.
        """
        # This query joins the three tables to get meaningful data.
        # Aliases (pa, p, u) are used to keep the query clean.
        sql_query = """
            SELECT
                pa.policies_acknow_id,
                pa.policy_id,
                p.title AS policy_title,
                pa.userid,
                -- We assume your users table has first_name and last_name columns.
                -- If not, you can change this to u.username or another field.
                CONCAT(u.first_name, ' ', u.last_name) AS user_name,
                pa.emp_id,
                pa.acknowledge,
                pa.is_policy_view,
                pa.created_date
            FROM
                ci_policies_acknowledge AS pa
            LEFT JOIN
                ci_policies AS p ON pa.policy_id = p.policy_id
            LEFT JOIN
                ci_erp_users AS u ON pa.userid = u.id -- Assuming the user PK is 'id'
            ORDER BY
                pa.created_date ;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            acknowledgement_list = dictfetchall(cursor)

        # Convert datetime objects to a standard string format for JSON
        for ack in acknowledgement_list:
            if ack.get('created_date') and isinstance(ack['created_date'], datetime):
                ack['created_date'] = ack['created_date'].strftime('%Y-%m-%d %H:%M:%S')

        # safe=False is required because we are returning a list
        return JsonResponse(acknowledgement_list, safe=False, json_dumps_params={'indent': 2})










#######################    policies dashboard

def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dictionaries."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

# --- Helper function for fancy date formatting ---
def format_acknowledge_date(dt_obj):
    """Formats a datetime object to match '24th December 2024 10:32 am'."""
    if not isinstance(dt_obj, datetime):
        return dt_obj
        
    day = dt_obj.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    
    # Format: 24th December 2024 10:32 am
    return dt_obj.strftime(f'{day}{suffix} %B %Y %I:%M %p').lower()


# --- View to get the acknowledgement list for a specific policy ---
class AnnouncementAcknowledgeView(View):
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to fetch pending acknowledgment policies
        grouped by employee.
        """

        sql_query = """
            SELECT
                CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                pa.emp_id AS employee_id,
                p.policy_id,
                SUBSTRING_INDEX(p.title, ' -', 1) AS policy_title,
                pa.acknowledge,
                pa.created_date AS acknowledge_date
            FROM
                ci_erp_users AS u
            LEFT JOIN
                ci_erp_users_details AS ud ON u.id = ud.user_id
            LEFT JOIN
                ci_policies_acknowledge AS pa ON ud.employee_id = pa.emp_id
            LEFT JOIN
                ci_policies AS p ON pa.policy_id = p.policy_id
            WHERE
                pa.acknowledge = 'N'
                AND p.policy_id IN (117, 118, 119)
            ORDER BY
                pa.created_date DESC;
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                acknowledge_list = dictfetchall(cursor)
        except Exception as e:
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)

        # Format the acknowledge date
        for item in acknowledge_list:
            item['acknowledge_date'] = format_acknowledge_date(item['acknowledge_date'])

        # Group by employee
        grouped = defaultdict(lambda: {
            "employee_name": "",
            "employee_id": "",
            "pending_policies": []
        })

        for item in acknowledge_list:
            emp_id = item["employee_id"]
            grouped[emp_id]["employee_name"] = item["employee_name"]
            grouped[emp_id]["employee_id"] = emp_id
            grouped[emp_id]["pending_policies"].append({
                # "policy_id": item["policy_id"],
                "policy_title": item["policy_title"],
                # "acknowledge_date": item["acknowledge_date"]
            })

        response_data = list(grouped.values())
        return JsonResponse(response_data, safe=False, json_dumps_params={"indent": 2})
    








#######################   help desk

class CreateTicketView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)

        subject = data.get('subject')
        department_id = data.get('department_id')
        ticket_priority = data.get('ticket_priority')
        description = data.get('description')
        employee_id = data.get('employee_id')

        if not all([subject, department_id, ticket_priority, description, employee_id]):
            return JsonResponse({'error': 'Missing required fields: subject, department_id, ticket_priority, description, employee_id'}, status=400)

        company_id = 2
        created_by = employee_id
        ticket_status = 1

        try:
            with connection.cursor() as cursor:
                # Step 1: Generate next ticket code
                cursor.execute("""
                    SELECT ticket_code FROM ci_support_tickets 
                    WHERE ticket_code IS NOT NULL AND ticket_code REGEXP '^TC[0-9]+$'
                    ORDER BY CAST(SUBSTRING(ticket_code, 3) AS UNSIGNED) DESC 
                    LIMIT 1;
                """)
                row = cursor.fetchone()
                if row and row[0]:
                    last_number = int(row[0][2:])  # strip 'TC' and convert to int
                    next_number = last_number + 1
                else:
                    next_number = 1000

                ticket_code = f"TC{next_number}"

                # Step 2: Insert the new ticket
                insert_query = """
                    INSERT INTO ci_support_tickets
                    (company_id, subject, employee_id, ticket_priority, department_id, description, ticket_status, created_by, created_at, ticket_code)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = [
                    company_id, subject, employee_id, ticket_priority, department_id,
                    description, ticket_status, created_by, datetime.now(), ticket_code
                ]
                cursor.execute(insert_query, params)
                new_ticket_id = cursor.lastrowid

        except Exception as e:
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)

        return JsonResponse({
            'message': 'Support ticket created successfully!',
            'ticket_id': new_ticket_id,
            'ticket_code': ticket_code
        }, status=201)
    


    # put method
    def put(self, request, *args, **kwargs):
        """
        Handles PUT requests to update an existing support ticket.
        The ticket_id is expected in the request body (payload).
        """
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)

        # --- THE FIX IS HERE ---
        # 1. Get ticket_id from the JSON payload
        ticket_id = data.get('ticket_id') 
        subject = data.get('subject')
        ticket_priority = data.get('ticket_priority')

        # 2. Add ticket_id to the validation
        if not all([ticket_id, subject, ticket_priority]):
            return JsonResponse({'error': 'Missing required fields: ticket_id, subject, ticket_priority'}, status=400)

        update_query = """
            UPDATE ci_support_tickets SET
                subject = %s,
                ticket_priority = %s
            WHERE
                ticket_id = %s;
        """
        
        # 3. Add the ticket_id from the payload to the params list
        params = [
            subject,
            ticket_priority,
            ticket_id 
        ]

        try:
            with connection.cursor() as cursor:
                cursor.execute(update_query, params)
                if cursor.rowcount == 0:
                    return JsonResponse({'error': 'Ticket not found or no changes made'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)

        return JsonResponse({
            'message': 'Ticket information updated successfully!',
            'ticket_id': ticket_id
        })






##########################  ticket view 


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

def dictfetchone(cursor):
    """Return one row from a cursor as a dictionary."""
    row = cursor.fetchone()
    if row is None: return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))

# --- View to Handle Ticket Details and Status Updates ---
@method_decorator(csrf_exempt, name='dispatch')
class TicketDetailView(View):
    
    def get(self, request, ticket_id, *args, **kwargs):
        """
        Handles GET requests to fetch all details of a single support ticket.
        """
        # --- THE FIX IS IN THIS SQL QUERY ---
        # Double up the percent signs in the DATE_FORMAT function
        sql_query = """
            SELECT
                t.ticket_id,
                t.ticket_code,
                t.subject,
                CONCAT(creator.first_name, ' ', creator.last_name) AS employee_name,
                t.ticket_priority,
                d.department_name,
                CONCAT(assignee.first_name, ' ', assignee.last_name) AS assigned_to,
                DATE_FORMAT(t.created_at, '%%d-%%m-%%Y') AS created_at,
                t.ticket_status
            FROM
                ci_support_tickets AS t
			LEFT JOIN ci_support_ticket_reply tr ON t.ticket_id = tr.ticket_id
            LEFT JOIN ci_erp_users AS creator ON t.employee_id = creator.id
            -- vvv THIS LINE HAS BEEN CORRECTED vvv
            LEFT JOIN ci_erp_users AS assignee ON tr.assign_to = assignee.id
            LEFT JOIN ci_departments AS d ON t.department_id = d.department_id
            WHERE t.ticket_id = %s;
        """
        with connection.cursor() as cursor:
            # The cursor.execute call remains the same
            cursor.execute(sql_query, [ticket_id])
            ticket_details = dictfetchone(cursor)

        if not ticket_details:
            return JsonResponse({'error': 'Ticket not found'}, status=404)
        
        return JsonResponse(ticket_details)
    


    def post(self, request, ticket_id, *args, **kwargs):
        """
        Handles POST requests to update a ticket's status and add a remark.
        Authentication is not required. User ID must be sent in the request body.
        """
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        new_status = data.get('status')
        remarks = data.get('remarks')
        employee_id = data.get('employee_id')  # Get user_id directly from payload

        # --- Validation ---
        if not all([new_status, remarks, employee_id]):
            return JsonResponse({'error': 'Missing required fields: status, remarks, and employee_id'}, status=400)

        try:
            with connection.cursor() as cursor:
                # 1. Update the status in the main tickets table
                update_query = "UPDATE ci_support_tickets SET ticket_status = %s, ticket_remarks = %s WHERE ticket_id = %s and employee_id = %s;"
                cursor.execute(update_query, [new_status, remarks, ticket_id, employee_id])

                # 2. Insert the remark into the reply/log table
                # reply_query = """
                #     INSERT INTO ci_support_ticket_reply
                #     (company_id, ticket_id, sent_by, reply_text, created_at) 
                #     VALUES (%s, %s, %s, %s, %s);
                # """
                # cursor.execute(reply_query, [2, ticket_id, employee_id, remarks, datetime.now()])

        except Exception as e:
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)

        return JsonResponse({
            'message': 'Ticket status updated and remark added successfully!',
            'ticket_id': ticket_id,
            'new_status': new_status
        }, status=200)




    def delete(self, request, ticket_id, *args, **kwargs):
        """
        Handles DELETE requests to delete a support ticket by ticket_id.
        """
        try:
            with connection.cursor() as cursor:
                delete_query = "DELETE FROM ci_support_tickets WHERE ticket_id = %s;"
                cursor.execute(delete_query, [ticket_id])

        except Exception as e:
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)

        return JsonResponse({
            'message': f'Ticket with ID {ticket_id} deleted successfully.'
        }, status=200)



















#################  department wise employee

from django.http import JsonResponse
from django.views import View
from django.db import connection

class DepartmentEmployeeListView(View):
    def get(self, request, *args, **kwargs):
        department_id = request.GET.get('department_id')

        if not department_id:
            return JsonResponse({'error': 'Missing department_id parameter'}, status=400)

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        ud.employee_id,
                        CONCAT(u.first_name, ' ', u.last_name) AS employee_name
                    FROM
                        ci_erp_users_details AS ud
                    INNER JOIN
                        ci_erp_users AS u ON ud.user_id = u.id
                    WHERE
                        ud.department_id = %s
                    ORDER BY
                        employee_name ASC
                """, [department_id])

                rows = cursor.fetchall()
                employee_list = [
                    {'employee_id': row[0], 'employee_name': row[1]}
                    for row in rows
                ]

        except Exception as e:
            return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)

        return JsonResponse(employee_list, safe=False, json_dumps_params={'indent': 2})
