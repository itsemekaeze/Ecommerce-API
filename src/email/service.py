from dotenv import dotenv_values
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid

config = dotenv_values(".env")

def create_verification_token() -> str:
    return str(uuid.uuid4())

def send_verification_email(email: str, token: str) -> dict:
    
    verification_link = f"http://localhost:8000/api/auth/verify-email?token={token}"
    
    if not config["EMAIL_ENABLED"]:
        return {
            "success": False,
            "message": "Email sending is disabled. Use the verification link directly.",
            "verification_link": verification_link,
            "token": token
        }
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = config["EMAIL"]
        msg['To'] = email
        msg['Subject'] = "Verify Your Email - E-Commerce Platform"
        
        text_body = f"""
        Welcome to E-Commerce Platform!
        
        Please verify your email address by clicking the link below:
        {verification_link}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #888; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to E-Commerce!</h1>
                </div>
                <div class="content">
                    <h2>Verify Your Email Address</h2>
                    <p>Thank you for registering! Please click the button below to verify your email address:</p>
                    <p style="text-align: center;">
                        <a href="{verification_link}" class="button">Verify Email</a>
                    </p>
                    <p>Or copy and paste this link in your browser:</p>
                    <p style="word-break: break-all; color: #667eea;">{verification_link}</p>
                    <p><strong>This link will expire in 24 hours.</strong></p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 E-Commerce Platform. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP(config["MAIL_SERVER"], int(config["MAIL_PORT"]), timeout=int(config["EMAIL_TIMEOUT"]))
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(config["EMAIL"], config["PASSWORD"])
        server.send_message(msg)
        server.quit()
        

        return {"success": True, "message": "Verification email sent successfully"}
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        return {"success": False, "message": "Email authentication failed.", "verification_link": verification_link, "token": token}
    except smtplib.SMTPConnectError as e:
        print(f"SMTP Connection Error: {e}")
        return {"success": False, "message": "Could not connect to email server.", "verification_link": verification_link, "token": token}
    except TimeoutError as e:
        print(f"Email Timeout Error: {e}")
        return {"success": False, "message": "Email server connection timed out.", "verification_link": verification_link, "token": token}
    except Exception as e:
        print(f"Error sending email: {e}")
        return {"success": False, "message": f"Failed to send email: {str(e)}", "verification_link": verification_link, "token": token}
