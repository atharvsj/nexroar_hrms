import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')  # Change 'your_project_name' to your actual project name
django.setup()

from django.core.mail import EmailMessage, send_mail
from django.conf import settings

def test_simple_email():
    """Test 1: Simple email without attachment"""
    print("=" * 50)
    print("Test 1: Sending simple email...")
    print("=" * 50)
    
    try:
        send_mail(
            subject='Test Email from Django',
            message='This is a test email to verify email configuration is working.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['atharva.jadhav@tdtl.world'],  # Change this to your email
            fail_silently=False,
        )
        print("✓ Simple email sent successfully!")
        return True
    except Exception as e:
        print(f"✗ Error sending simple email: {str(e)}")
        return False

def test_email_with_html():
    """Test 2: Email with HTML content"""
    print("\n" + "=" * 50)
    print("Test 2: Sending HTML email...")
    print("=" * 50)
    
    try:
        html_message = """
        <html>
            <body>
                <h2>Test Email</h2>
                <p>This is a <strong>test email</strong> with HTML content.</p>
                <p>If you can see this formatted, HTML emails are working!</p>
            </body>
        </html>
        """
        
        email = EmailMessage(
            subject='Test HTML Email from Django',
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['your_email@example.com'],  # Change this to your email
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)
        
        print("✓ HTML email sent successfully!")
        return True
    except Exception as e:
        print(f"✗ Error sending HTML email: {str(e)}")
        return False

def test_email_with_attachment():
    """Test 3: Email with text file attachment"""
    print("\n" + "=" * 50)
    print("Test 3: Sending email with attachment...")
    print("=" * 50)
    
    try:
        email = EmailMessage(
            subject='Test Email with Attachment',
            body='This email has a text file attachment.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['your_email@example.com'],  # Change this to your email
        )
        
        # Create a simple text file attachment
        email.attach('test_file.txt', 'This is a test attachment file.', 'text/plain')
        
        email.send(fail_silently=False)
        
        print("✓ Email with attachment sent successfully!")
        return True
    except Exception as e:
        print(f"✗ Error sending email with attachment: {str(e)}")
        return False

def print_email_settings():
    """Display current email settings"""
    print("\n" + "=" * 50)
    print("Current Email Settings:")
    print("=" * 50)
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD)}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print("=" * 50)

if __name__ == "__main__":
    print("\n🔧 Django Email Configuration Test")
    print_email_settings()
    
    # Run tests
    test1_result = test_simple_email()
    test2_result = test_email_with_html()
    test3_result = test_email_with_attachment()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print("=" * 50)
    print(f"Simple Email: {'✓ PASSED' if test1_result else '✗ FAILED'}")
    print(f"HTML Email: {'✓ PASSED' if test2_result else '✗ FAILED'}")
    print(f"Email with Attachment: {'✓ PASSED' if test3_result else '✗ FAILED'}")
    print("=" * 50)
    
    if all([test1_result, test2_result, test3_result]):
        print("\n🎉 All tests passed! Your email configuration is working perfectly.")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")