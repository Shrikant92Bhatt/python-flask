"""
=============================================================================
Authentication Module for FlaskCraft
Demonstrating real-world Login, Logout, Session Management, and
Flash Messages rendered as floating Toast notifications.
=============================================================================
"""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

# Blueprint for Authentication routes
auth_bp = Blueprint("auth", __name__)

# Mock user database for authentication demonstration
# Username -> Password
DEMO_USERS = {
    "admin": "flask123",
    "shrikant": "python123",
    "developer": "craft2026",
}


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user login authentication.
    - If already logged in, flashes an info message and redirects to home.
    - On POST: validates credentials, saves user in session, and flashes success or error.
    """
    # Redirect if session is already active
    if "user" in session:
        flash(f"You are already logged in as '{session['user']}'.", "info")
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # 1. Validation check
        if not username or not password:
            flash("Please enter both username and password.", "warning")
            return render_template("login.html", username=username, demo_users=DEMO_USERS)

        # 2. Credential verification
        normalized_username = username.lower()
        if normalized_username in DEMO_USERS and DEMO_USERS[normalized_username] == password:
            # Save user identity in secure encrypted session cookie
            session["user"] = normalized_username
            
            # Flash success message (survives redirect and displays as Toast)
            flash(f"Welcome back, {normalized_username.title()}! You have successfully logged in.", "success")
            
            print("=" * 40)
            print(f"Auth Success: User '{normalized_username}' logged in.")
            print("=" * 40)

            # Redirect to home (PRG pattern)
            return redirect(url_for("home"))
        else:
            # Flash error toast
            flash("Invalid credentials! Please check your username and password.", "danger")
            
            print("=" * 40)
            print(f"Auth Failed: Attempt with username '{username}'.")
            print("=" * 40)
            
            return render_template("login.html", username=username, demo_users=DEMO_USERS)

    return render_template("login.html", demo_users=DEMO_USERS)


@auth_bp.route("/logout")
def logout():
    """
    Logs out the user by removing their identity from the session cookie.
    Flashes a toast confirmation and redirects to the login screen.
    """
    user = session.pop("user", None)
    if user:
        flash(f"Goodbye, {user.title()}! You have been safely logged out.", "info")
        print("=" * 40)
        print(f"Auth Logout: User '{user}' logged out.")
        print("=" * 40)
    else:
        flash("You are not currently logged in.", "warning")

    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
def dashboard():
    """
    Protected route: Requires user to be logged in.
    If not logged in, flashes a warning and redirects to login.
    """
    if "user" not in session:
        flash("Access restricted! Please log in first to view your dashboard.", "warning")
        return redirect(url_for("auth.login"))

    return render_template("dashboard.html", user=session["user"])
