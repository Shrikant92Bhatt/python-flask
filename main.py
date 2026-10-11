
from flask import Flask, render_template, request

app = Flask(__name__, template_folder="template")

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
    return render_template("service.html")

if __name__ == "__main__":
    app.run(debug=True) 