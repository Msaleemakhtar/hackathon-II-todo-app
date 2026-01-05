#!/usr/bin/env python3
"""Direct SMTP test to verify Gmail configuration."""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Gmail SMTP settings
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "saleemakhtar864@gmail.com"
SMTP_PASSWORD = "eutiaqkbrftbcdim"  # App password
FROM_EMAIL = "saleemakhtar864@gmail.com"
TO_EMAIL = "saleemakhtar864@gmail.com"

print("=" * 80)
print("SMTP DIRECT TEST - Gmail Configuration")
print("=" * 80)
print(f"SMTP Host: {SMTP_HOST}")
print(f"SMTP Port: {SMTP_PORT}")
print(f"From: {FROM_EMAIL}")
print(f"To: {TO_EMAIL}")
print("=" * 80)

# Create message
message = MIMEMultipart("alternative")
message["Subject"] = "✅ Test Email from Todo App - Phase V Event-Driven Architecture"
message["From"] = FROM_EMAIL
message["To"] = TO_EMAIL

# Email body
text_body = """
Hello!

This is a test email from the Todo App Phase V event-driven architecture.

If you receive this email, it confirms that:
✅ Gmail SMTP configuration is correct
✅ App password is valid
✅ Email delivery service can send emails

Event-Driven Architecture Status: OPERATIONAL 🚀

Best regards,
Todo App Email Delivery Service
"""

html_body = """
<html>
  <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
      <h2 style="color: #2563eb;">✅ Test Email from Todo App</h2>
      <p>Hello!</p>
      <p>This is a test email from the <strong>Todo App Phase V event-driven architecture</strong>.</p>
      <div style="background-color: #dbeafe; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3 style="margin-top: 0; color: #1e40af;">If you receive this email, it confirms that:</h3>
        <ul style="margin-bottom: 0;">
          <li>✅ Gmail SMTP configuration is correct</li>
          <li>✅ App password is valid</li>
          <li>✅ Email delivery service can send emails</li>
        </ul>
      </div>
      <p style="font-size: 18px; color: #16a34a; font-weight: bold;">Event-Driven Architecture Status: OPERATIONAL 🚀</p>
      <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
      <p style="color: #6b7280; font-size: 12px;">
        Best regards,<br>
        Todo App Email Delivery Service
      </p>
    </div>
  </body>
</html>
"""

part1 = MIMEText(text_body, "plain")
part2 = MIMEText(html_body, "html")
message.attach(part1)
message.attach(part2)

print("\n📧 Attempting to send test email...")
print("-" * 80)

try:
    # Create secure SSL context
    context = ssl.create_default_context()

    # Connect to Gmail SMTP server
    print("1. Connecting to Gmail SMTP server...")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        print("   ✅ Connected")

        # Start TLS encryption
        print("2. Starting TLS encryption...")
        server.starttls(context=context)
        print("   ✅ TLS started")

        # Login
        print("3. Authenticating...")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        print("   ✅ Authenticated successfully")

        # Send email
        print("4. Sending email...")
        server.sendmail(FROM_EMAIL, TO_EMAIL, message.as_string())
        print("   ✅ Email sent successfully!")

    print("-" * 80)
    print("🎉 SUCCESS! Email has been sent to:", TO_EMAIL)
    print("=" * 80)
    print("\nPlease check your inbox (and spam folder) for the test email.")
    print("Subject: ✅ Test Email from Todo App - Phase V Event-Driven Architecture")

except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ Authentication failed: {e}")
    print("Check that the app password is correct and hasn't expired.")
except smtplib.SMTPException as e:
    print(f"\n❌ SMTP error: {e}")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
