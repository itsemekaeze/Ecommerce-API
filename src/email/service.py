from fastapi import BackgroundTasks
from dotenv import dotenv_values
from datetime import timedelta
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from src.auth.service import create_access_token
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

config = dotenv_values(".env")

fastmail_available = False
conf = None

try:
        
    email = config.get("EMAIL")
    password = config.get("PASSWORD")
    
    
    conf = ConnectionConfig(
        MAIL_USERNAME=email,
        MAIL_PASSWORD=password,
        MAIL_FROM=email,
        MAIL_PORT=int(config.get("MAIL_PORT", 587)),
        MAIL_SERVER=config.get("MAIL_SERVER", "smtp.gmail.com"),
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )
    
    fastmail_available = True
    print("FastMail configured successfully")

except Exception as e:
    print(f"FastMail configuration warning: {e}")
    print("  Will fall back to SMTP if needed")


async def send_verification_email(user, background_tasks: BackgroundTasks):
 
    if fastmail_available and conf:
        await send_email_fastmail(user, background_tasks)
    else:
        background_tasks.add_task(send_email_smtp, user)


async def send_email_fastmail(user, background_tasks: BackgroundTasks):
    try:
        
        
        token_data = {
            "id": user.id,
            "username": user.username
        }
        token = create_access_token(token_data, expires_delta=timedelta(hours=24))
        
        frontend_url = config.get("FRONTEND_URL", "http://localhost:8000")
        verification_url = f"{frontend_url}/verification?token={token}"
        
        html_content = create_email_html(user.username, verification_url)
        
        message = MessageSchema(
            subject="EasyShopas - Verify Your Email Address",
            recipients=[user.email],
            body=html_content,
            subtype=MessageType.html
        )
        
        fm = FastMail(conf)
        background_tasks.add_task(fm.send_message, message)
        
        print(f"Verification email scheduled for {user.email}")
        
    except Exception as e:
        print(f"FastMail error: {e}")
        
        background_tasks.add_task(send_email_smtp, user)


def send_email_smtp(user):

    
    
    try:
        token_data = {"id": user.id}
        token = create_access_token(token_data, expires_delta=timedelta(hours=24))
        
        verification_url = f"{config.get('FRONTEND_URL', 'http://localhost:8000')}/verification?token={token}"
        
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Ecommerce - Verify Your Email Address'
        msg['From'] = config["EMAIL"]
        msg['To'] = user.email
        
        
        html = create_email_html(user.username, verification_url)
        msg.attach(MIMEText(html, 'html'))
        
        
        mail_server = config.get("MAIL_SERVER", "smtp.gmail.com")
        mail_port = int(config.get("MAIL_PORT", 587))
        
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()
            server.login(config["EMAIL"], config["PASSWORD"])
            server.send_message(msg)
        
        print(f"Email sent successfully to {user.email}")
        
    except smtplib.SMTPAuthenticationError:
        print(f" SMTP Authentication failed. Check your EMAIL and PASSWORD in .env")
        print(f"For Gmail, use an App Password: https://myaccount.google.com/apppasswords")
    except Exception as e:
        print(f"Email sending failed: {e}")


def create_email_html(username: str, verification_url: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #007bff; margin: 0;">Ecommerce</h1>
                </div>
                
                <h2 style="color: #333; text-align: center;">Verify Your Email Address</h2>
                
                <p style="color: #555; line-height: 1.6;">
                    Hello <strong>{username}</strong>,
                </p>
                
                <p style="color: #555; line-height: 1.6;">
                    Thank you for registering with Ecommerce Website! To complete your registration and start enjoying exclusive discounts, please verify your email address by clicking the button below.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="display: inline-block; padding: 15px 40px; background-color: #007bff; 
                              color: white; text-decoration: none; border-radius: 5px; font-weight: bold;
                              font-size: 16px;">
                        Verify Email Address
                    </a>
                </div>
                
                <p style="color: #777; font-size: 14px; line-height: 1.6;">
                    Or copy and paste this link into your browser:
                </p>
                <p style="color: #007bff; font-size: 12px; word-break: break-all;">
                    {verification_url}
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 13px; line-height: 1.6;">
                    <strong>Security Note:</strong> This verification link will expire in 24 hours.
                </p>
                
                <p style="color: #999; font-size: 13px; line-height: 1.6;">
                    If you didn't create an account with Ecommerce, please ignore this email. Your email address will not be used.
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px; text-align: center; margin: 0;">
                    © 2025 Ecommerce. All rights reserved.
                </p>
            </div>
        </body>
    </html>
    """
