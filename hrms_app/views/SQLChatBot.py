from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.middleware.csrf import get_token
import json
import os
from openai import OpenAI
import pymysql
import uuid
import re
import speech_recognition as sr
from gtts import gTTS
# import google.generativeai as genai
from google import genai

from django.shortcuts import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.http import FileResponse
from django.views.static import serve
from django.utils.safestring import mark_safe
from django.middleware.csrf import get_token
from django.http import HttpResponse
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.http import HttpResponse
from django.http import JsonResponse
 
from google import genai

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Configure API keys
# genai.configure(api_key="AIzaSyCld94ergv55o8ZqL2zJnSy180tav5qD0M")
 
# Enable CORS
from django.middleware.csrf import get_token
from django.http import JsonResponse
 
def csrf_token_view(request):
    return JsonResponse({'csrfToken': get_token(request)})
 
 
# Database Connection Function
def connect_db():
    try:
        connection = pymysql.connect(
            host="ls-f8259bafe38561c18d0d411f37aefbfabc0ff7bf.citdgny2wnek.ap-south-1.rds.amazonaws.com",
            user="dbmasteruser",
            password="database9014",
            database="new_hrms",
            cursorclass=pymysql.cursors.DictCursor  
        )
        return connection
    except pymysql.MySQLError as e:
        return {"error": f"Database connection error: {e}"}
 
# Retrieve Database Schema
def get_db_schema():
    try:
        connection = connect_db()
        if isinstance(connection, dict):
            return connection
 
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
 
            schema = {}
            for table in tables:
                table_name = table["Tables_in_new_hrms"]
                cursor.execute(f"SHOW COLUMNS FROM {table_name};")
                columns = cursor.fetchall()
                schema[table_name] = [column["Field"] for column in columns]
 
        connection.close()
        return schema
    except pymysql.MySQLError as e:
        return {"error": f"Database schema retrieval error: {e}"}
 
# # Generate SQL Query using AI
# def get_gemini_response(question, schema):
#     schema_info = "\n".join([f"Table: {table}, Columns: {', '.join(columns)}" for table, columns in schema.items()])
#     prompt = f"""
#     You are an SQL expert. Translate user questions into SQL queries using the schema:
#     {schema_info}
#     Respond with only the SQL query, enclosed in "```sql ... ```".
#     """
#     try:
#         model = genai.GenerativeModel('gemini-1.5-flash')
#         response = model.generate_content([prompt, question])
#         return response.text.strip("```sql").strip("```")
#     except Exception as e:
#         return {"error": f"Generative AI error: {e}"}
 

# def execute_sql(sql):
#     try:
#         sql = re.sub(r"```sql|```", "", sql).strip()
 
#         connection = connect_db()
#         if isinstance(connection, dict):  
#             return connection, None  
 
#         with connection.cursor() as cursor:
#             cursor.execute(sql)
#             rows = cursor.fetchall()
#             description = cursor.description  
 
#         connection.close()
#         return rows, description
#     except pymysql.MySQLError as e:
#         return {"error": f"SQL execution error: {e}"}, None
   
 
# # Convert Text to Speech
# def text_to_speech(text):
#     tts = gTTS(text)
#     file_name = f"output_{uuid.uuid4().hex}.mp3"
#     tts.save(os.path.join(settings.MEDIA_ROOT, file_name))
#     return file_name
 
 
 

# @method_decorator(csrf_exempt, name="dispatch")
# class SQLChatbotView(View):
#     def post(self, request):
#         try:
#             data = json.loads(request.body)
#             input_type = data.get("input_type", "text")
#             user_query = data.get("user_query", "").strip()
#             output_format = data.get("output_format", "text_to_text")
 
#             if input_type == "speech":
#                 transcription = self.transcribe_speech()
#                 if not transcription:
#                     return JsonResponse({"error": "Speech transcription failed."}, status=400)
#                 user_query = transcription
 
#             schema = get_db_schema()
#             if "error" in schema:
#                 return JsonResponse({"error": schema["error"]}, status=500)
 
#             sql_query = get_gemini_response(user_query, schema)
#             if "error" in sql_query:
#                 return JsonResponse({"error": sql_query["error"]}, status=500)
 
#             sql_query = sql_query.strip("```sql").strip("```")
#             query_result, description = execute_sql(sql_query)
#             if isinstance(query_result, dict) and "error" in query_result:
#                 return JsonResponse({"error": query_result["error"]}, status=500)
 
#             # result = [dict(zip([col[0] for col in description], row)) for row in query_result]
#             result = query_result
 
#             if output_format == "text_to_speech":
#                 audio_file = text_to_speech(str(result))
#                 return JsonResponse({"audio_file": f"/media/{audio_file}"})
 
#             elif output_format == "text_to_text":
#                 return JsonResponse({"sql_query": sql_query, "query_result": result})
 
#             return JsonResponse({"error": "Invalid output format."}, status=400)
 
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)


import json
import os
import re
import uuid
import pymysql

from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from gtts import gTTS

from google import genai

# --------------------------------------------------
# Gemini Client Initialization
# --------------------------------------------------
client = genai.Client(api_key=settings.GEMINI_API_KEY)


# --------------------------------------------------
# Generate SQL Query using Gemini AI
# --------------------------------------------------
def get_gemini_response(question, schema):
    schema_info = "\n".join(
        [f"Table: {table}, Columns: {', '.join(columns)}" for table, columns in schema.items()]
    )

    prompt = f"""
You are an expert MySQL query writer.

Convert the user question into a valid SQL query using ONLY the schema below.

Schema:
{schema_info}

Rules:
- Return ONLY the SQL query
- Do NOT explain anything
- Do NOT add markdown or backticks
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{prompt}\nUser Question: {question}"
        )

        return response.text.strip()

    except Exception as e:
        return {"error": f"Generative AI error: {e}"}


# --------------------------------------------------
# Execute SQL Query
# --------------------------------------------------
def execute_sql(sql):
    try:
        sql = re.sub(r"```sql|```", "", sql).strip()

        connection = connect_db()
        if isinstance(connection, dict):
            return connection, None

        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            description = cursor.description

        connection.close()
        return rows, description

    except pymysql.MySQLError as e:
        return {"error": f"SQL execution error: {e}"}, None


# --------------------------------------------------
# Convert Text to Speech
# --------------------------------------------------
def text_to_speech(text):
    tts = gTTS(text)
    file_name = f"output_{uuid.uuid4().hex}.mp3"
    tts.save(os.path.join(settings.MEDIA_ROOT, file_name))
    return file_name


# --------------------------------------------------
# SQL Chatbot API View
# --------------------------------------------------
@method_decorator(csrf_exempt, name="dispatch")
class SQLChatbotView(View):

    def post(self, request):
        try:
            data = json.loads(request.body)

            input_type = data.get("input_type", "text")
            user_query = data.get("user_query", "").strip()
            output_format = data.get("output_format", "text_to_text")

            # ---------------- Speech Input ----------------
            if input_type == "speech":
                transcription = self.transcribe_speech()
                if not transcription:
                    return JsonResponse(
                        {"error": "Speech transcription failed."},
                        status=400
                    )
                user_query = transcription

            # ---------------- DB Schema ----------------
            schema = get_db_schema()
            if isinstance(schema, dict) and "error" in schema:
                return JsonResponse({"error": schema["error"]}, status=500)

            # ---------------- Gemini SQL ----------------
            sql_query = get_gemini_response(user_query, schema)
            if isinstance(sql_query, dict) and "error" in sql_query:
                return JsonResponse({"error": sql_query["error"]}, status=500)

            # ---------------- Execute SQL ----------------
            query_result, description = execute_sql(sql_query)
            if isinstance(query_result, dict) and "error" in query_result:
                return JsonResponse({"error": query_result["error"]}, status=500)

            result = query_result

            # ---------------- Output Formats ----------------
            if output_format == "text_to_speech":
                audio_file = text_to_speech(str(result))
                return JsonResponse({"audio_file": f"/media/{audio_file}"})

            elif output_format == "text_to_text":
                return JsonResponse({
                    "sql_query": sql_query,
                    "query_result": result
                })

            return JsonResponse({"error": "Invalid output format."}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)



    def transcribe_speech(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
 
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
 
            try:
                audio = recognizer.listen(source)
                return recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                return None
            except sr.RequestError:
                return None