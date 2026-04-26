import streamlit as st
import re
from database import (sign_up, 
                    sign_in, verify_otp,
                    is_username_taken,
                    resend_otp,
                    get_email_by_username,
                    is_email_taken,
                    update_password  
                    )

from config import APP_TAGLINE, APP_LOGO, OTP_EXPIRY_SECONDS
import time
from email_utils import generate_otp, send_reset_otp_email

# ----------------------------------------
# VALIDATION FUNCTIONS
# ----------------------------------------

def validate_email(email):
    """
    Validates email format using regex.
    Accepts formats like: user@domain.com, example@ucp.edu.pk

    Args:
        email (str): Email to validate

    Returns:
        str: Error message or None if valid
    """
    if not email:
        return "Email is required"
    if not re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", email):
        return "Please enter a valid email address"
    return None


def validate_password(password):
    """
    Validates password strength using regex.
    Must be 8+ chars, contain at least one letter and one digit.

    Args:
        password (str): Password to validate

    Returns:
        str: Error message or None if valid
    """
    if not password:
        return "Password is required"
    if len(password) < 8:
        return "Password must be at least 8 characters"
    pattern = r"^(?=.*[a-zA-Z])(?=.*\d).{8,}$"
    if not re.match(pattern, password):
        return "Password must contain at least one letter and one number"
    return None


def validate_username(username):
    """
    Validates username format.
    Must be 3-20 chars, only letters, numbers, underscores.

    Args:
        username (str): Username to validate

    Returns:
        str: Error message or None if valid
    """
    if not username:
        return "Username is required"
    if len(username) < 3:
        return "Username must be at least 3 characters"
    if len(username) > 20:
        return "Username must be under 20 characters"
    if not re.match("^[a-zA-Z0-9_]+$", username):
        return "Username can only contain letters, numbers, underscores"
    return None

def validate_full_name(full_name):
    """
    Validates full name input.
    Must be 2-50 chars, only letters and spaces allowed.

    Args:
        full_name (str): Full name to validate

    Returns:
        str: Error message or None if valid
    """
    if not full_name or not full_name.strip():
        return "Full name is required"
    if len(full_name.strip()) < 2:
        return "Full name must be at least 2 characters"
    if len(full_name.strip()) > 50:
        return "Full name must be under 50 characters"
    if not re.match("^[a-zA-Z ]+$", full_name.strip()):
        return "Full name can only contain letters and spaces"
    return None

def mask_email(email):
    """
    Masks email for privacy display.
    imranbuttcodes@gmail.com → imr***********@gmail.com

    Args:
        email (str): Full email address

    Returns:
        str: Masked email
    """
    parts = email.split("@")
    username = parts[0]
    domain   = parts[1]

    # Show first 3 chars + stars + domain
    visible  = username[:3]
    masked   = "*" * (len(username) - 3)

    return f"{visible}{masked}@{domain}"


# ---------------------------------------------------
# HELPER FUNCTION TO SHOW HEADER TO REDUCE REDUNDENCY
# ---------------------------------------------------

def show_brand_header(tagline=None):
    """
    Shows PawGress logo + animated brand name + tagline.
    Called at top of every auth screen.
    """
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.image(APP_LOGO, width=100)

    tagline_text = tagline or APP_TAGLINE

    st.markdown(f"""
        <style>
        @keyframes shimmer {{
            0%   {{ background-position: -200% center; }}
            100% {{ background-position: 200% center; }}
        }}
        @keyframes glow {{
            0%, 100% {{ text-shadow: 0 0 10px #c9a227; }}
            50%       {{ text-shadow: 0 0 25px #c9a227, 0 0 50px #c9a227; }}
        }}
        .paw {{
            color: #40c463;
            font-size: 42px;
            font-weight: 800;
            text-shadow: 0 0 10px rgba(64,196,99,0.5);
        }}
        .gress {{
            color: #c9a227;
            font-size: 42px;
            font-weight: 800;
            animation: glow 2s infinite;
        }}
        .tagline {{
            text-align: center;
            font-size: 17px;
            font-weight: 600;
            background: linear-gradient(90deg, #40c463, #c9a227, #40c463);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 3s linear infinite;
        }}
        </style>
        <p style='text-align:center; margin:0'>
            <span class='paw'>Paw</span><span class='gress'>Gress</span>
        </p>
        <p class='tagline'>{tagline_text}</p>
    """, unsafe_allow_html=True)
    st.markdown("")

# ----------------------------------------
# LOGIN SCREEN
# ----------------------------------------

def show_login():
    """
    Displays the login screen.
    On success stores user in st.session_state.user
    and redirects to home screen via st.rerun()
    """

    show_brand_header()


    st.subheader("Login")

    if st.session_state.pop("pw_reset_success", False):
       st.success("🔒 Password securely updated! Please log in with your new credentials.")

    # Input fields
    username    = st.text_input("Username",    placeholder="Enter your username")
    password = st.text_input("Password", placeholder="Enter your password", type="password")
    
    st.markdown("")
    col1, col2 = st.columns([2, 1])
    with col2:
        if st.button("Forgot Password?", key="forgot_pwd_btn", use_container_width=True):
            st.session_state.auth_screen = "forgot_password"
            st.rerun()

    # Login button
    if st.button("Login →", use_container_width=True, key="login_btn"):
        
        # Validate inputs
        username_error = validate_username(username)
        password_error = validate_password(password)
    
        if username_error:
            st.error(username_error)
        elif password_error:
            st.error(password_error)
        else: 
            email = get_email_by_username(username)
            if not email:
                st.error("Username not found!")
            else:
                # Call sign_in from database.py
                with st.spinner("Logging in..."):
                    result = sign_in(email, password)

                if result["success"]:
                    # Store user in session state
                    st.session_state.user    = result["user"]
                    st.session_state.user_id = result["user"].id
                    st.success("Welcome back!")
    
                    st.rerun()
                else:
                    st.error(f"Login failed: {result['error']}")

    # Switch to signup
    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Don't have an account? Sign Up", use_container_width=True, key="goto_signup_btn"):
            st.session_state.auth_screen = "signup"
            st.rerun()


# ----------------------------------------
# SIGNUP SCREEN
# ----------------------------------------

def show_signup():
    """
    Displays the signup screen.
    On success sends OTP and switches to OTP screen.
    """

    show_brand_header("Create your account")
    
    
    st.subheader("Sign Up")

    # Input fields
    full_name = st.text_input("Full Name", placeholder="e.g. Imran Butt")
    username = st.text_input("Username", placeholder="e.g. imranbuttcodes")
    email    = st.text_input("Email",    placeholder="Enter your email")
    password = st.text_input("Password", placeholder="Min 8 chars, letters + numbers", type="password")

    # Signup button
    if st.button("Create Account", use_container_width=True, key="signup_btn"):

        # Validate all inputs
        full_name_error = validate_full_name(full_name)
        username_error = validate_username(username)
        email_error    = validate_email(email)
        password_error = validate_password(password)
        if full_name_error:
            st.error(full_name_error)
        elif username_error:
            st.error(username_error)
        elif email_error:
            st.error(email_error)
        elif password_error:
            st.error(password_error)
        else:
            # Check username uniqueness
            with st.spinner("Checking username..."):
                taken = is_username_taken(username)
            if taken:
                st.error("Username already taken — try another one!")
            else:
                with st.spinner("Checking email..."):
                    email_taken = is_email_taken(email)
                if email_taken:
                    st.error("Email already registered — please login instead!")
                else:
                    # Call sign_up from database.py
                    with st.spinner("Creating account..."):
                        result = sign_up(email, password)

                    if result["success"]:
                        # Save email + username for OTP screen
                        st.session_state.pending_full_name = full_name  
                        st.session_state.pending_email    = email
                        st.session_state.pending_username = username
                        st.session_state.auth_screen      = "otp"
                        st.success("OTP sent to your email! 📧")
                        st.rerun()
                    else:
                        st.error(f"Signup failed: {result['error']}")

    # Switch back to login
    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Already have an account? Login", use_container_width=True, key="goto_login_btn"):
            st.session_state.auth_screen = "login"
            st.rerun()

# ----------------------------------------
# FORGOT PASSWORD SCREEN
# ----------------------------------------

def show_forgot_password():
    """
    3-step password reset flow using Python OTP:
    Step 1 - Enter username
    Step 2 - Enter OTP sent via Gmail
    Step 3 - Set new password
    """

    show_brand_header("Reset your password")
    

    # Initialize reset step
    if "reset_step" not in st.session_state:
        st.session_state.reset_step  = 1
    if "reset_email" not in st.session_state:
        st.session_state.reset_email = None
    if "reset_otp" not in st.session_state:
        st.session_state.reset_otp   = None
    if "otp_expiry" not in st.session_state:
        st.session_state.otp_expiry  = None

    # ─────────────────────────────────────
    # STEP 1 — Enter Username
    # ─────────────────────────────────────
    if st.session_state.reset_step == 1:

        st.subheader("Enter Username")
        st.info("Enter your username and we'll send an OTP to your email.")

        username = st.text_input("Username", placeholder="Enter your username")

        if st.button("Send OTP", use_container_width=True, key="reset_send_otp_btn"):
            username_error = validate_username(username)
            if username_error:
                st.error(username_error)
            else:
                with st.spinner("Looking up account..."):
                    email = get_email_by_username(username)

                if not email:
                    st.error("Username not found!")
                else:
                    # Generate OTP
                    otp = generate_otp()

                    # Send OTP email
                    with st.spinner("Sending OTP..."):
                        result = send_reset_otp_email(email, otp)

                    if result["success"]:
                        # Store in session state
                        st.session_state.reset_email  = email
                        st.session_state.reset_otp    = otp
                        st.session_state.otp_expiry   = time.time() + OTP_EXPIRY_SECONDS  
                        st.session_state.reset_step   = 2
                        masked = mask_email(email)
                        st.success(f"Verification Code sent to {masked}")
                        st.rerun()
                    else:
                        st.error(f"Failed to send OTP: {result['error']}")

    # ─────────────────────────────────────
    # STEP 2 — Enter OTP
    # ─────────────────────────────────────
    elif st.session_state.reset_step == 2:

        masked = mask_email(st.session_state.reset_email)
        st.subheader("Verification")
        st.info(f"Enter the 6-digit code sent to **{masked}**")

        otp_code = st.text_input("OTP Code", placeholder="Enter 6-digit code", max_chars=6)

        if st.button("Verify code", use_container_width=True, key="reset_verify_btn"):
            if not otp_code:
                st.error("Please enter the OTP code!")
            elif len(otp_code) != 6:
                st.error("OTP must be exactly 6 digits!")
            # Check expiry
            elif time.time() > st.session_state.otp_expiry:
                st.error("OTP expired! Please request a new one.")
                st.session_state.reset_step = 1
                st.rerun()
            # Check OTP match
            elif otp_code != st.session_state.reset_otp:
                st.error("Invalid OTP! Please try again.")
            else:
                st.session_state.reset_step = 3
                st.success("OTP verified!")
                st.rerun()

        # Resend OTP
        st.markdown("")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Resend OTP 🔄", use_container_width=True, key="reset_resend_btn"):
                otp = generate_otp()
                with st.spinner("Resending..."):
                    result = send_reset_otp_email(st.session_state.reset_email, otp)
                if result["success"]:
                    st.session_state.reset_otp   = otp
                    st.session_state.otp_expiry  = time.time() + OTP_EXPIRY_SECONDS
                    st.success("OTP resent!")
                else:
                    st.error(f"Failed: {result['error']}")

    # ─────────────────────────────────────
    # STEP 3 — Set New Password
    # ─────────────────────────────────────
    elif st.session_state.reset_step == 3:

        st.subheader("Set New Password 🔒")
        st.info("Choose a strong new password.")

        new_password     = st.text_input("New Password",     placeholder="Min 8 chars, letters + numbers", type="password")
        confirm_password = st.text_input("Confirm Password", placeholder="Re-enter new password",          type="password")

        if st.button("Update Password", use_container_width=True, key="reset_update_btn"):
            password_error = validate_password(new_password)
            if password_error:
                st.error(password_error)
            elif new_password != confirm_password:
                st.error("Passwords don't match!")
            else:
                with st.spinner("Updating password..."):
                    result = update_password(
                        st.session_state.reset_email,
                        new_password
                    )

                if result["success"]:
                    # Clear all reset state
                    del st.session_state.reset_step
                    del st.session_state.reset_email
                    del st.session_state.reset_otp
                    del st.session_state.otp_expiry
                    st.session_state.auth_screen = "login"
                    st.balloons()
                    st.success("Password updated successfully!")
                    st.info("Please login with your new password.")
                    if st.button("Go to Login", use_container_width=True, key="reset_goto_login"):
                        st.rerun()
                else:
                    st.error(f"Failed: {result['error']}")

    # Back to login
    st.markdown("")
    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Back to Login", use_container_width=True, key="back_to_login_btn"):
            # Clear reset state
            for key in ["reset_step", "reset_email", "reset_otp", "otp_expiry"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.auth_screen = "login"
            st.rerun()
        
# ----------------------------------------
# OTP SCREEN
# ----------------------------------------

def show_otp():
    """
    Displays the OTP verification screen.
    Called after successful signup.
    On success redirects to login screen.
    """
    # Safety check — if session expired redirect to signup
    if "pending_email" not in st.session_state:
        st.warning("Session expired. Please sign up again.")
        st.session_state.auth_screen = "signup"
        st.rerun()
        return

    # Header

    show_brand_header(f"OTP sent to {st.session_state.pending_email}")

    
    st.subheader("Enter OTP")
    st.info("Check your email for a 6-digit verification code")

    # OTP input
    otp_code = st.text_input("OTP Code", placeholder="Enter 6-digit code", max_chars=6)

    # Verify button
    if st.button("Verify", use_container_width=True, key="verify_btn"):
        if not otp_code:
            st.error("Please enter the OTP code")
        elif len(otp_code) != 6:
            st.error("OTP must be exactly 6 digits")
        else:
            with st.spinner("Verifying..."):
                result = verify_otp(
                    st.session_state.pending_email,
                    otp_code,
                    st.session_state.pending_username,
                    st.session_state.pending_full_name
                )

            if result["success"]:
                success_email = st.session_state.pending_email
                success_username = st.session_state.pending_username
                # Clear pending signup data
                del st.session_state.pending_email
                del st.session_state.pending_username
                del st.session_state.pending_full_name
                # Redirect to login — don't auto login
                st.session_state.auth_screen = "login"
                st.balloons()
                st.success("Account verified successfully!")
                st.info("Please login to continue")
                from email_utils import send_welcome_email

                send_welcome_email(success_email, success_username)
                
                if st.button("Go to Login →", use_container_width=True, key="goto_login_after_verify"):
                    st.rerun()
            else:
                st.error(f"Invalid OTP: {result['error']}")

    # Resend OTP — always visible outside if/else
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Resend OTP 🔄", use_container_width=True, key="resend_btn"):
            with st.spinner("Resending OTP..."):
                result = resend_otp(st.session_state.pending_email)
            if result["success"]:
                st.success("OTP resent! Check your email 📧")
            else:
                st.error(f"Failed to resend: {result['error']}")



# ----------------------------------------
# MAIN AUTH CONTROLLER
# ----------------------------------------

def show_auth():
    """
    Main auth controller.
    Called from app.py when user is not logged in.
    Routes to correct screen based on auth_screen session state.
    """
    # Initialize auth screen if not set
    if "auth_screen" not in st.session_state:
        st.session_state.auth_screen = "login"

    # Route to correct screen
    if st.session_state.auth_screen == "login":
        show_login()
    elif st.session_state.auth_screen == "signup":
        show_signup()
    elif st.session_state.auth_screen == "otp":
        show_otp()
    elif st.session_state.auth_screen == "forgot_password":
        show_forgot_password()