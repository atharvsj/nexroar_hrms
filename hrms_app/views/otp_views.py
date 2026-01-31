import random
import string
from datetime import datetime, timedelta
from django.db import connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import bcrypt


class SendOTP(APIView):
    """
    API to send OTP to user's email for password reset
    """
    permission_classes = [AllowAny]

    def generate_otp(self, length=6):
        """Generate a random numeric OTP"""
        return ''.join(random.choices(string.digits, k=length))

    def post(self, request):
        try:
            email_id = request.data.get('email_id')

            if not email_id:
                return Response(
                    {"status": False, "message": "Email ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if user exists with this email
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, first_name, last_name FROM ci_erp_users WHERE email = %s",
                    [email_id]
                )
                user = cursor.fetchone()

                if not user:
                    return Response(
                        {"status": False, "message": "User with this email does not exist"},
                        status=status.HTTP_404_NOT_FOUND
                    )

                user_id = user[0]
                full_name = f"{user[1] or ''} {user[2] or ''}".strip() or "User"

            # Generate OTP
            otp = self.generate_otp()
            otp_expiry = datetime.now() + timedelta(minutes=10)

            # Store OTP in database (create table if not exists and insert/update OTP)
            with connection.cursor() as cursor:
                # Create OTP table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ci_otp_verification (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        otp VARCHAR(10) NOT NULL,
                        otp_expiry DATETIME NOT NULL,
                        is_verified TINYINT DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)

                # Check if OTP entry exists for this email
                cursor.execute(
                    "SELECT id FROM ci_otp_verification WHERE email = %s",
                    [email_id]
                )
                existing_entry = cursor.fetchone()

                if existing_entry:
                    # Update existing OTP
                    cursor.execute(
                        """UPDATE ci_otp_verification 
                           SET otp = %s, otp_expiry = %s, is_verified = 0, updated_at = NOW() 
                           WHERE email = %s""",
                        [otp, otp_expiry, email_id]
                    )
                else:
                    # Insert new OTP entry
                    cursor.execute(
                        """INSERT INTO ci_otp_verification (user_id, email, otp, otp_expiry, is_verified) 
                           VALUES (%s, %s, %s, %s, 0)""",
                        [user_id, email_id, otp, otp_expiry]
                    )

            # Send OTP via email
            subject = 'Email Verification - OTP Code'
            
            html_message = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Email Verification</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 50px auto;
                        background-color: #ffffff;
                        border-radius: 10px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: #ffffff;
                        text-align: center;
                        padding: 30px 20px;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                    }}
                    .content {{
                        padding: 40px 30px;
                        text-align: center;
                    }}
                    .content h2 {{
                        color: #333333;
                        margin-bottom: 20px;
                    }}
                    .content p {{
                        color: #666666;
                        line-height: 1.6;
                        margin-bottom: 30px;
                    }}
                    .otp-box {{
                        background-color: #f8f9fa;
                        border: 2px dashed #667eea;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 30px 0;
                    }}
                    .otp-code {{
                        font-size: 36px;
                        font-weight: bold;
                        color: #667eea;
                        letter-spacing: 8px;
                        margin: 10px 0;
                    }}
                    .expiry-text {{
                        color: #e74c3c;
                        font-size: 14px;
                        margin-top: 15px;
                    }}
                    .footer {{
                        background-color: #f8f9fa;
                        text-align: center;
                        padding: 20px;
                        color: #999999;
                        font-size: 12px;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border-left: 4px solid #ffc107;
                        padding: 15px;
                        margin: 20px 0;
                        text-align: left;
                    }}
                    .warning p {{
                        margin: 5px 0;
                        color: #856404;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Email Verification</h1>
                    </div>
                    <div class="content">
                        <h2>Hello {full_name}!</h2>
                        <p>We received a request to reset your password. Please use the OTP code below to verify your identity and proceed with resetting your password:</p>
                        
                        <div class="otp-box">
                            <p style="margin: 0; color: #666;">Your OTP Code</p>
                            <div class="otp-code">{otp}</div>
                            <p class="expiry-text">⏰ This code will expire in 10 minutes</p>
                        </div>
                        
                        <p>Enter this code in the verification page to reset your password.</p>
                        
                        <div class="warning">
                            <p><strong>⚠️ Security Notice:</strong></p>
                            <p>• Never share this OTP with anyone</p>
                            <p>• Our team will never ask for your OTP</p>
                            <p>• If you didn't request this code, please ignore this email</p>
                        </div>
                    </div>
                    <div class="footer">
                        <p>This is an automated email. Please do not reply to this message.</p>
                        <p>&copy; 2025 The Data Tech Labs. All rights reserved.</p>
                        <p>Need help? Contact us at support@thedatatechlabs.com</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Send email
            email = EmailMultiAlternatives(
                subject=subject,
                body=f"Your OTP code is: {otp}. This code will expire in 10 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email_id]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

            return Response(
                {
                    "status": True,
                    "message": "OTP sent successfully to your email",
                    "email": email_id
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": False, "message": f"Error sending OTP: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyOTP(APIView):
    """
    API to verify OTP sent to user's email
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email_id = request.data.get('email_id')
            otp = request.data.get('otp')

            if not email_id or not otp:
                return Response(
                    {"status": False, "message": "Email ID and OTP are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with connection.cursor() as cursor:
                # Fetch OTP details for the email
                cursor.execute(
                    """SELECT otp, otp_expiry, is_verified 
                       FROM ci_otp_verification 
                       WHERE email = %s 
                       ORDER BY created_at DESC 
                       LIMIT 1""",
                    [email_id]
                )
                otp_record = cursor.fetchone()

                if not otp_record:
                    return Response(
                        {"status": False, "message": "No OTP found for this email. Please request a new OTP."},
                        status=status.HTTP_404_NOT_FOUND
                    )

                stored_otp = otp_record[0]
                otp_expiry = otp_record[1]
                is_verified = otp_record[2]

                # Check if OTP is already verified
                if is_verified:
                    return Response(
                        {"status": False, "message": "OTP has already been verified. Please request a new OTP."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Check if OTP has expired
                if datetime.now() > otp_expiry:
                    return Response(
                        {"status": False, "message": "OTP has expired. Please request a new OTP."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Verify OTP
                if str(otp) != str(stored_otp):
                    return Response(
                        {"status": False, "message": "Invalid OTP. Please try again."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Mark OTP as verified
                cursor.execute(
                    """UPDATE ci_otp_verification 
                       SET is_verified = 1, updated_at = NOW() 
                       WHERE email = %s""",
                    [email_id]
                )

            return Response(
                {
                    "status": True,
                    "message": "OTP verified successfully",
                    "email": email_id
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": False, "message": f"Error verifying OTP: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResetPassword(APIView):
    """
    API to reset user's password after OTP verification
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email_id = request.data.get('email_id')
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')

            if not email_id or not new_password:
                return Response(
                    {"status": False, "message": "Email ID and new password are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if confirm_password and new_password != confirm_password:
                return Response(
                    {"status": False, "message": "Passwords do not match"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate password strength (optional)
            if len(new_password) < 6:
                return Response(
                    {"status": False, "message": "Password must be at least 6 characters long"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with connection.cursor() as cursor:
                # Check if OTP was verified for this email
                cursor.execute(
                    """SELECT is_verified FROM ci_otp_verification 
                       WHERE email = %s 
                       ORDER BY created_at DESC 
                       LIMIT 1""",
                    [email_id]
                )
                otp_record = cursor.fetchone()

                if not otp_record:
                    return Response(
                        {"status": False, "message": "Please verify OTP first before resetting password"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if not otp_record[0]:  # is_verified is 0 or False
                    return Response(
                        {"status": False, "message": "OTP not verified. Please verify OTP first."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Check if user exists and get current password
                cursor.execute(
                    "SELECT id, password FROM ci_erp_users WHERE email = %s",
                    [email_id]
                )
                user = cursor.fetchone()

                if not user:
                    return Response(
                        {"status": False, "message": "User with this email does not exist"},
                        status=status.HTTP_404_NOT_FOUND
                    )

                # Check if new password is same as existing password
                existing_password = user[1]
                if existing_password:
                    try:
                        # Handle both string and bytes for existing password
                        if isinstance(existing_password, str):
                            existing_password = existing_password.encode('utf-8')
                        
                        if bcrypt.checkpw(new_password.encode('utf-8'), existing_password):
                            return Response(
                                {"status": False, "message": "New password cannot be the same as your current password. Please choose a different password."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    except Exception:
                        # If password comparison fails (e.g., different hash format), proceed with update
                        pass

                # Hash the new password using bcrypt (format: $2b$12$...)
                hashed_password = bcrypt.hashpw(
                    new_password.encode('utf-8'),
                    bcrypt.gensalt(rounds=12)
                ).decode('utf-8')

                # Update password in ci_erp_users table
                cursor.execute(
                    "UPDATE ci_erp_users SET password = %s WHERE email = %s",
                    [hashed_password, email_id]
                )

                # Invalidate the OTP record after password reset
                cursor.execute(
                    """DELETE FROM ci_otp_verification WHERE email = %s""",
                    [email_id]
                )

            return Response(
                {
                    "status": True,
                    "message": "Password reset successfully",
                    "email": email_id
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": False, "message": f"Error resetting password: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
