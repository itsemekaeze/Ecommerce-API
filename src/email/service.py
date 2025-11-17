from dotenv import dotenv_values
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid

config = dotenv_values(".env")

def create_verification_token() -> str:
    return str(uuid.uuid4())

# Email utility
def send_verification_email(email: str, username: str, token: str) -> bool:
    try:
        # Create verification link
        verification_link = f"http://localhost:8000/api/auth/verify-email?token={token}"
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Verify Your E-Commerce Account"
        message["From"] = config["EMAIL"]
        message["To"] = email
        
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
              <h2 style="color: #4CAF50; text-align: center;">Welcome to Our E-Commerce Platform!</h2>
              <p>Hello <strong>{username}</strong>,</p>
              <p>Thank you for registering with us. Please verify your email address to activate your account.</p>
              <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_link}" 
                   style="background-color: #4CAF50; color: white; padding: 14px 28px; text-decoration: none; 
                          border-radius: 5px; display: inline-block; font-size: 16px;">
                  Verify Email Address
                </a>
              </div>
              <p>Or copy and paste this link into your browser:</p>
              <p style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; word-break: break-all;">
                {verification_link}
              </p>
              <p style="margin-top: 30px; font-size: 12px; color: #666;">
                If you didn't create this account, please ignore this email.
              </p>
              <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
              <p style="text-align: center; font-size: 12px; color: #999;">
                © 2024 E-Commerce Platform. All rights reserved.
              </p>
            </div>
          </body>
        </html>
        """
        
        part = MIMEText(html, "html")
        message.attach(part)
        
        # Send email
        with smtplib.SMTP(config["MAIL_SERVER"], config["MAIL_PORT"]) as server:
            server.starttls()
            server.login(config["EMAIL"], config["PASSWORD"])
            server.sendmail(config["EMAIL"], email, message.as_string())
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False