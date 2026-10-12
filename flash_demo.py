"""
=============================================================================
Flash Messaging Module for FlaskCraft
Demonstrating Flask's `flash()` function, categories (success, warning,
danger, info), session storage requirement (`secret_key`), and the
standard Post/Redirect/Get (PRG) design pattern.
=============================================================================
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for

# Blueprint for Flash Messages demo
flash_bp = Blueprint("flash_demo", __name__)

# Predefined educational sample flash messages for quick testing
SAMPLE_MESSAGES = {
    "success": "Action completed successfully! Your settings have been saved.",
    "warning": "Heads up: Your account has 2 days remaining on the trial period.",
    "danger": "Error: Database connection timed out. Please retry your request.",
    "info": "Pro Tip: You can filter services dynamically with the ?tier= query parameter.",
}


@flash_bp.route("/flash-demo", methods=["GET"])
def flash_page():
    """
    Renders the interactive Flash Messages playground page.
    When this page renders, Jinja calls `get_flashed_messages()`,
    which consumes and automatically clears any queued messages from the session.
    """
    return render_template(
        "flash_demo.html",
        sample_messages=SAMPLE_MESSAGES,
    )


@flash_bp.route("/flash-demo/trigger", methods=["POST"])
def trigger_flash():
    """
    Handles form submission to flash a custom message.
    Demonstrates:
    1. `request.form.get()` to read input
    2. `flash(message, category)` to store message into session cookie
    3. `redirect()` to perform the Post/Redirect/Get pattern
    """
    message = request.form.get("message", "").strip()
    category = request.form.get("category", "info").strip().lower()

    # Fallback to defaults if message is empty
    if not message:
        message = SAMPLE_MESSAGES.get(category, "This is a default flashed notification.")

    # Validate category to standard alert names
    if category not in ["success", "warning", "danger", "info"]:
        category = "info"

    # Store message in session flash queue
    flash(message, category)

    print("=" * 40)
    print("Flask Flash Message Triggered:")
    print(f"  Category: {category}")
    print(f"  Message:  {message}")
    print("=" * 40)

    # Post/Redirect/Get: redirect back so browser doesn't prompt for form re-submission
    return redirect(url_for("flash_demo.flash_page"))


@flash_bp.route("/flash-demo/quick/<category>", methods=["GET", "POST"])
def quick_flash(category):
    """
    One-click shortcut endpoint to trigger a preset flash message
    for any category: /flash-demo/quick/success, /flash-demo/quick/danger, etc.
    """
    category = category.lower()
    msg = SAMPLE_MESSAGES.get(
        category,
        f"Custom {category.upper()} notification triggered successfully!"
    )

    flash(msg, category)
    return redirect(url_for("flash_demo.flash_page"))
