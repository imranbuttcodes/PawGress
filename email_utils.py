import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from config import APP_NAME, APP_TAGLINE
import os

load_dotenv()

GMAIL_EMAIL        = os.getenv("GMAIL_EMAIL") or ""
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD") or ""


# ----------------------------------------
# OTP GENERATOR
# ----------------------------------------

def generate_otp():
    """
    Generates a random 6-digit OTP.

    Returns:
        str: 6-digit OTP code
    """
    return str(random.randint(100000, 999999))


# ----------------------------------------
# EMAIL SENDER
# ----------------------------------------

def send_reset_otp_email(to_email, otp):
    """
    Sends password reset OTP email via Gmail SMTP.

    Args:
        to_email (str): Recipient email address
        otp (str): 6-digit OTP code

    Returns:
        dict: {"success": True} or {"success": False, "error": str}
    """
    # Check credentials exist
    if not GMAIL_EMAIL or not GMAIL_APP_PASSWORD:
        return {"success": False, "error": "Email credentials not configured"}

    try:
        # Create email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{APP_NAME} - Password Reset Code"
        msg["From"]    = f"{APP_NAME} <{GMAIL_EMAIL}>"
        msg["To"]      = to_email

        # Email body
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto;">

            <h2 style="color: #1a1a2e; text-align: center;">
                🐾 {APP_NAME}
            </h2>

            <p>Hey there!</p>

            <p>We received a request to reset your 
            <strong>{APP_NAME}</strong> account password.</p>

            <p>Use the code below to reset your password:</p>

            <div style="
                background: #1a1a2e;
                color: #40c463;
                padding: 20px 40px;
                text-align: center;
                border-radius: 12px;
                letter-spacing: 10px;
                font-size: 32px;
                font-weight: bold;
                margin: 24px 0;
                font-family: monospace;">
                {otp}
            </div>

            <p>⏰ This code expires in <strong>10 minutes</strong>.</p>

            <p style="color: gray; font-size: 13px;">
                If you didn't request a password reset,
                you can safely ignore this email.
            </p>

            <br>
            <p>Best regards,<br>
            <strong>The {APP_NAME} Team</strong> 🐾</p>

            <hr style="border: none; border-top: 1px solid #eee; margin-top: 20px;">

            <p style="color: gray; font-size: 12px; text-align: center;">
                🐾 {APP_NAME} - {APP_TAGLINE}<br>
                <span style="font-size: 11px;">
                    This is an automated email. Please do not reply.
                </span>
            </p>

        </div>
        """

        msg.attach(MIMEText(html, "html"))

        # Send via Gmail SMTP with timeout
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
            server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}
    


def send_welcome_email(to_email, username):
    """
    Sends a professional welcome email after successful account creation.

    Args:
        to_email (str): User's email
        username (str): User's username

    Returns:
        dict: {"success": True} or {"success": False, "error": str}
    """
    if not GMAIL_EMAIL or not GMAIL_APP_PASSWORD:
        return {"success": False, "error": "Email credentials not configured"}

    try:
        msg            = MIMEMultipart("alternative")
        msg["Subject"] = f"Welcome to {APP_NAME}"
        msg["From"]    = f"{APP_NAME} <{GMAIL_EMAIL}>"
        msg["To"]      = to_email

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin:0; padding:0; background-color:#f4f4f7;
                     font-family:Arial, sans-serif;">

            <table width="100%" cellpadding="0" cellspacing="0"
                   style="background-color:#f4f4f7; padding:40px 0;">
                <tr>
                    <td align="center">

                        <!-- Main Card -->
                        <table width="520" cellpadding="0" cellspacing="0"
                               style="background:#ffffff; border-radius:16px;
                                      overflow:hidden;
                                      box-shadow:0 4px 24px rgba(0,0,0,0.08);">

                            <!-- Header -->
                            <tr>
                                <td style="background:#1a1a2e; padding:36px 40px;
                                           text-align:center;">
                                    <p style="margin:0; font-size:32px;
                                              font-weight:800;
                                              letter-spacing:2px;">
                                        <span style="color:#40c463;">Paw</span><span style="color:#c9a227;">Gress</span>
                                    </p>
                                    <p style="margin:8px 0 0; font-size:13px;
                                              color:#888888; letter-spacing:1px;">
                                        {APP_TAGLINE}
                                    </p>
                                </td>
                            </tr>

                            <!-- Body -->
                            <tr>
                                <td style="padding:40px 40px 20px;">

                                    <p style="margin:0 0 8px; font-size:22px;
                                              font-weight:700; color:#1a1a2e;">
                                        Welcome, {username}.
                                    </p>
                                    <p style="margin:0 0 28px; font-size:15px;
                                              color:#555555; line-height:1.7;">
                                        Your account has been created successfully.
                                        You are ready to begin your productivity
                                        journey with PawGress.
                                    </p>

                                    <!-- Divider -->
                                    <hr style="border:none;
                                               border-top:1px solid #eeeeee;
                                               margin:0 0 28px;">

                                    <!-- Section Label -->
                                    <p style="margin:0 0 16px; font-size:12px;
                                              font-weight:700; color:#aaaaaa;
                                              text-transform:uppercase;
                                              letter-spacing:1.5px;">
                                        Getting started
                                    </p>

                                    <!-- Feature List -->
                                    <table width="100%" cellpadding="0"
                                           cellspacing="0">

                                        <tr>
                                            <td style="padding:12px 0;
                                                       border-bottom:1px solid #f4f4f4;">
                                                <table cellpadding="0" cellspacing="0">
                                                    <tr>
                                                        <td style="width:4px;
                                                                   background:#40c463;
                                                                   border-radius:2px;">
                                                        </td>
                                                        <td style="padding-left:16px;">
                                                            <p style="margin:0;
                                                                      font-size:14px;
                                                                      font-weight:600;
                                                                      color:#1a1a2e;">
                                                                Log daily tasks
                                                            </p>
                                                            <p style="margin:3px 0 0;
                                                                      font-size:12px;
                                                                      color:#888888;">
                                                                Complete tasks to
                                                                earn XP and coins
                                                            </p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>

                                        <tr>
                                            <td style="padding:12px 0;
                                                       border-bottom:1px solid #f4f4f4;">
                                                <table cellpadding="0" cellspacing="0">
                                                    <tr>
                                                        <td style="width:4px;
                                                                   background:#40c463;
                                                                   border-radius:2px;">
                                                        </td>
                                                        <td style="padding-left:16px;">
                                                            <p style="margin:0;
                                                                      font-size:14px;
                                                                      font-weight:600;
                                                                      color:#1a1a2e;">
                                                                Build a daily streak
                                                            </p>
                                                            <p style="margin:3px 0 0;
                                                                      font-size:12px;
                                                                      color:#888888;">
                                                                Log at least one task
                                                                every day to maintain
                                                                your streak
                                                            </p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>

                                        <tr>
                                            <td style="padding:12px 0;
                                                       border-bottom:1px solid #f4f4f4;">
                                                <table cellpadding="0" cellspacing="0">
                                                    <tr>
                                                        <td style="width:4px;
                                                                   background:#40c463;
                                                                   border-radius:2px;">
                                                        </td>
                                                        <td style="padding-left:16px;">
                                                            <p style="margin:0;
                                                                      font-size:14px;
                                                                      font-weight:600;
                                                                      color:#1a1a2e;">
                                                                Evolve your pet
                                                            </p>
                                                            <p style="margin:3px 0 0;
                                                                      font-size:12px;
                                                                      color:#888888;">
                                                                Your pet grows from
                                                                Egg to Adult as you
                                                                accumulate XP
                                                            </p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>

                                        <tr>
                                            <td style="padding:12px 0;">
                                                <table cellpadding="0" cellspacing="0">
                                                    <tr>
                                                        <td style="width:4px;
                                                                   background:#40c463;
                                                                   border-radius:2px;">
                                                        </td>
                                                        <td style="padding-left:16px;">
                                                            <p style="margin:0;
                                                                      font-size:14px;
                                                                      font-weight:600;
                                                                      color:#1a1a2e;">
                                                                Unlock achievements
                                                            </p>
                                                            <p style="margin:3px 0 0;
                                                                      font-size:12px;
                                                                      color:#888888;">
                                                                Earn badges by
                                                                reaching milestones
                                                                and completing
                                                                challenges
                                                            </p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>

                                    </table>

                                    <!-- Divider -->
                                    <hr style="border:none;
                                               border-top:1px solid #eeeeee;
                                               margin:28px 0;">

                                    <!-- Closing -->
                                    <p style="margin:0 0 6px; font-size:14px;
                                              color:#555555; line-height:1.7;">
                                        Start by naming your pet and logging
                                        your first task. Every great habit
                                        begins with a single step.
                                    </p>
                                    <p style="margin:0; font-size:14px;
                                              color:#555555; line-height:1.7;">
                                        The {APP_NAME} Team
                                    </p>

                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td style="background:#f8f8f8; padding:24px 40px;
                                           border-top:1px solid #eeeeee;">
                                    <p style="margin:0; font-size:12px;
                                              color:#aaaaaa; text-align:center;
                                              line-height:1.7;">
                                        You received this email because you
                                        created a {APP_NAME} account.<br>
                                        This is an automated message —
                                        please do not reply.
                                    </p>
                                    <p style="margin:10px 0 0; font-size:12px;
                                              color:#cccccc; text-align:center;">
                                        &copy; 2026 {APP_NAME}. All rights reserved.
                                    </p>
                                </td>
                            </tr>

                        </table>

                    </td>
                </tr>
            </table>

        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}



def send_deletion_confirmation_email(to_email, username):
    """
    Sends a confirmation email after an account is deleted.
    """
    if not GMAIL_EMAIL or not GMAIL_APP_PASSWORD:
        return {"success": False, "error": "Email credentials not configured"}

    try:
        msg            = MIMEMultipart("alternative")
        msg["Subject"] = f"Account Deleted - {APP_NAME}"
        msg["From"]    = f"{APP_NAME} <{GMAIL_EMAIL}>"
        msg["To"]      = to_email

        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 12px;">
            <h2 style="color: #1a1a2e; text-align: center;">🐾 {APP_NAME}</h2>
            <p>Hello <strong>{username}</strong>,</p>
            <p>This email confirms that your {APP_NAME} account has been permanently deleted as per your request.</p>
            <p>All your data, including your pet's progress, task history, and achievements, has been erased from our systems.</p>
            <div style="background: #fff4f4; border-left: 4px solid #ff4b4b; padding: 15px; margin: 20px 0;">
                <p style="margin: 0; color: #d32f2f; font-weight: bold;">Account Permanently Removed</p>
                <p style="margin: 5px 0 0; font-size: 13px; color: #666;">If you did not request this deletion, please contact our support team immediately.</p>
            </div>
            <p>We're sorry to see you go, but we hope PawGress helped you build some great habits while you were here.</p>
            <br>
            <p>Best regards,<br><strong>The {APP_NAME} Team</strong></p>
        </div>
        """
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}