import streamlit as st
from database import update_profile, sign_out, update_password, sign_in, delete_account
from auth import validate_full_name, validate_password
from email_utils import send_deletion_confirmation_email
import os
from dotenv import load_dotenv

load_dotenv()

SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL")

def show_profile():
    profile = st.session_state.profile

    st.markdown(
        "<h2 style='text-align:center'>Profile Settings</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center; color:gray'>"
        "Manage your account and pet preferences"
        "</p>",
        unsafe_allow_html=True
    )

    # ── Account Details ───────────────────
    with st.container(border=True):
        st.markdown("### 👤 Account Details")

        st.text_input(
            "Email",
            value=profile.get("email", ""),
            disabled=True
        )
        st.text_input(
            "Username",
            value=profile.get("username", ""),
            disabled=True
        )

        new_full_name = st.text_input(
            "Full Name",
            value=profile.get("full_name", "")
        )

        if st.button(
            "Save Account Details",
            use_container_width=True,
            key="save_profile"
        ):
            if new_full_name.strip() == profile.get("full_name", ""):
                st.info("No changes made.")
            else:
                error = validate_full_name(new_full_name)
                if error:
                    st.error(error)
                else:
                    update_profile(
                        st.session_state.user_id,
                        {"full_name": new_full_name.strip()}
                    )
                    st.session_state.profile["full_name"] = new_full_name.strip()
                    st.success("Profile updated successfully!")

    # ── Pet Preferences ───────────────────
    with st.container(border=True):
        st.markdown("### 🐾 Pet Preferences")

        pet_name     = profile.get("pet_name", "My Pet")
        new_pet_name = st.text_input("Pet Name", value=pet_name)

        if st.button(
            "Rename Pet",
            use_container_width=True,
            key="save_pet_name"
        ):
            if not new_pet_name.strip():
                st.error("Pet name cannot be empty!")
            elif new_pet_name.strip() == pet_name:
                st.info("No changes made.")
            else:
                update_profile(
                    st.session_state.user_id,
                    {"pet_name": new_pet_name.strip()}
                )
                st.session_state.profile["pet_name"] = new_pet_name.strip()
                st.success(f"Pet renamed to {new_pet_name.strip()}!")

    # ── Change Password ───────────────────
    with st.container(border=True):
        st.markdown("### 🔒 Change Password")
        st.markdown(
            "<p style='font-size:14px; color:gray;'>"
            "Verify your current password to securely update your login password."
            "</p>",
            unsafe_allow_html=True
        )

        current_password = st.text_input(
            "Current Password",
            type="password",
            placeholder="Enter current password",
            key="profile_current_password"
        )
        new_password     = st.text_input(
            "New Password",
            type="password",
            placeholder="Min 8 chars, letters + numbers",
            key="profile_new_password"
        )
        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter new password",
            key="profile_confirm_password"
        )

        if st.button(
            "Update Password",
            use_container_width=True,
            key="profile_update_password"
        ):
            if not current_password or not new_password or not confirm_password:
                st.error("Please fill out all password fields!")
            elif current_password == new_password:
               st.warning("New password cannot be the same as your current password!")
            else:
                password_error = validate_password(new_password)
                if password_error:
                    st.error(password_error)
                elif new_password != confirm_password:
                    st.error("Passwords don't match!")
                else:
                    with st.spinner("Authenticating..."):
                        # Step 1: Verify they know the old password!
                        auth_check = sign_in(profile.get("email"), current_password)
                        
                        if not auth_check.get("success"):
                            st.error("Incorrect current password! Authorization denied.")
                        else:
                            # Step 2: Override the password safely
                            result = update_password(
                                profile["email"],
                                new_password
                            )
                            if result["success"]:
                                sign_out()
                                for key in list(st.session_state.keys()):
                                    del st.session_state[key]
                                st.session_state["pw_reset_success"] = True
                                st.rerun()
                            else:
                                st.error(f"Failed: {result['error']}")

    # ── Help & Support ────────────────────
    with st.container(border=True):
        st.markdown("### Help & Support")
        st.markdown(
            "<p style='font-size:14px; color:gray;'>"
            "Need help? Reach out to our support team."
            "</p>",
            unsafe_allow_html=True
        )
        st.markdown(
            f'<a href="mailto:{SUPPORT_EMAIL}'
            f'?subject=PawGress Support - {profile.get("username", "")}" '
            f'style="display:block; background:#40c463; color:white; '
            f'text-align:center; padding:10px; border-radius:12px; '
            f'font-weight:600; text-decoration:none; margin-top:4px;">'
            f'Contact Support</a>',
            unsafe_allow_html=True
        )


    # ── Danger Zone ───────────────────────
    with st.container(border=True):
        st.markdown("### 🛑 Danger Zone")
        st.markdown(
            "<p style='font-size:14px; color:gray;'>"
            "Signing out will end your current session."
            "</p>",
            unsafe_allow_html=True
        )
        if st.button(
            "Sign Out",
            use_container_width=True,
            key="profile_sign_out"
        ):
            sign_out()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("---")
        
        # Delete Account
        st.markdown("<p style='font-size:14px; font-weight:600; color:#ff4b4b; margin-bottom:0;'>Delete Account</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:13px; color:gray;'>Permanently delete your account and all progress. This action requires password verification.</p>", unsafe_allow_html=True)
        
        # 1. Password Verification
        delete_password = st.text_input(
            "Enter your password to verify",
            type="password",
            placeholder="Current password",
            key="delete_password_verify"
        )
        
        # 2. Safety confirmation checkbox (Instant reactive UI)
        confirm_delete = st.checkbox(
            "I understand that this action is permanent and irreversible.",
            key="delete_confirm_checkbox"
        )
        
        if st.button(
            "Permanently Delete My Account",
            use_container_width=True,
            type="primary",
            disabled=(not confirm_delete or not delete_password),
            key="profile_delete_account"
        ):
            
            with st.spinner("Deleting your data..."):
                # First, verify the password!
                auth_check = sign_in(profile.get("email"), delete_password)
                
                if not auth_check.get("success"):
                    st.error("Incorrect password! Account deletion denied.")
                else:
                    # Capturing email/username BEFORE deletion wipes them
                    user_email = profile.get("email")
                    username   = profile.get("username")
                    
                    # Proceed with deletion
                    result = delete_account(st.session_state.user_id)
                    
                    if result["success"]:
                        # Send confirmation email
                        send_deletion_confirmation_email(user_email, username)
                        
                        # Log them out and clear everything
                        sign_out()
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.success("Your account has been deleted. We're sorry to see you go!")
                        st.rerun()
                    else:
                        st.error(f"Error deleting account: {result['error']}")