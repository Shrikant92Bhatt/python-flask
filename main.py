from flask import Flask, render_template, request, session, flash, redirect, url_for
from api import api_bp
from flash_demo import flash_bp
from auth import auth_bp

app = Flask(__name__, template_folder="template")
# Secret key is required for secure signed session cookies (used by flash messages and auth sessions)
app.secret_key = "flaskcraft-dev-secret-key-2026"

# Register modular blueprints from separate files
app.register_blueprint(api_bp)
app.register_blueprint(flash_bp)
app.register_blueprint(auth_bp)

@app.route("/")
def home():
    return render_template("home.html")


# Dynamic options passed into Jinja template
inquiry_options = [
    {"id": "project", "label": "New Project Proposal"},
    {"id": "development", "label": "Full-Stack Development"},
    {"id": "consulting", "label": "Architecture Consulting"},
    {"id": "general", "label": "General Question"},
]

# In-memory list to demonstrate Jinja loops with submission history
submissions = []

@app.route("/contact", methods=["GET", "POST"])
def contact():
    submission = None
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        submission = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
        }
        submissions.append(submission)

        print("=" * 40)
        print("Contact Form Submission Received:")
        print(f"  Name:    {name}")
        print(f"  Email:   {email}")
        print(f"  Subject: {subject}")
        print(f"  Message: {message}")
        print("=" * 40)

        return render_template(
            "contact.html",
            success=True,
            submission=submission,
            inquiry_options=inquiry_options,
            submissions=submissions,
        )

    return render_template(
        "contact.html",
        inquiry_options=inquiry_options,
        submissions=submissions,
    )


@app.route("/about")
def about():
    # 1. Simple variables
    company_name = "FlaskCraft Technologies"
    founded_year = 2024
    is_hiring = True

    # 2. List of dictionaries for Jinja loop & conditional demonstration
    team = [
        {"name": "Alice Johnson", "role": "Lead Architect", "is_lead": True, "experience": 8},
        {"name": "Bob Smith", "role": "Frontend Specialist", "is_lead": False, "experience": 5},
        {"name": "Charlie Davis", "role": "DevOps Engineer", "is_lead": False, "experience": 3},
        {"name": "Diana Prince", "role": "UI/UX Designer", "is_lead": False, "experience": 2},
    ]

    # 3. Milestones data for timeline loop & if/else check
    milestones = [
        {"year": 2024, "title": "Foundation & Core Routing", "desc": "Initial creation of the lightweight boilerplate with Flask WSGI server.", "completed": True},
        {"year": 2025, "title": "Glassmorphic Design System", "desc": "Integration of modern dark mode tokens, fluid typography, and CSS grid.", "completed": True},
        {"year": 2026, "title": "Multi-Page Static Suite", "desc": "Expanded into a full multi-page modular static website platform.", "completed": True},
        {"year": 2027, "title": "Cloud Microservices", "desc": "Planned serverless container deployments and automated CI/CD.", "completed": False},
    ]

    # 4. Pass all data into render_template
    return render_template(
        "about.html",
        company_name=company_name,
        founded_year=founded_year,
        is_hiring=is_hiring,
        team=team,
        milestones=milestones,
    )


@app.route("/service")
def service():
    # 1. Read query parameters from URL: /service?tier=pro&promo=FLASK20
    # request.args.get(key, default_value)
    selected_tier = request.args.get("tier", default="all")
    discount_code = request.args.get("promo", default="FLASK20").strip()

    # Pre-defined promotional discounts dictionary
    valid_promos = {
        "FLASK20": 20,
        "SUMMER50": 50,
        "WELCOME10": 10,
        "VIP100": 100,
    }
    discount_percent = valid_promos.get(discount_code.upper(), 0) if discount_code else 0

    print("=" * 40)
    print("URL Query Parameters Received in Python:")
    print(f"  tier  = {selected_tier}")
    print(f"  promo = {discount_code} ({discount_percent}% discount)")
    print("=" * 40)

    # 2. Pass query parameter values to template
    return render_template(
        "service.html",
        selected_tier=selected_tier,
        discount_code=discount_code,
        discount_percent=discount_percent,
    )


@app.route("/study")
def study():
    return render_template("study.html")


# Custom Jinja Template Filter demonstration
@app.template_filter("currency")
def currency_filter(value):
    """Formats numeric values as currency strings."""
    if value is None:
        return "Custom Quote"
    return f"${value:,.2f}"


# Custom Error Handlers
@app.errorhandler(404)
def page_not_found(error):
    """Handles 404 Not Found errors with content negotiation for API vs Web."""
    if request.path.startswith("/api/"):
        return {"success": False, "error": "Endpoint not found", "code": 404}, 404
    return render_template("404.html", error=error), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Handles 500 Internal Server Errors defensively."""
    if request.path.startswith("/api/"):
        return {"success": False, "error": "Internal server error", "code": 500}, 500
    return render_template("404.html", error=error, error_code=500, error_title="500 - Internal Server Error"), 500


if __name__ == "__main__":
    app.run(debug=True)