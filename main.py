
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
    # 1. Define variables in Python
    company_name = "FlaskCraft Technologies"
    founded_year = 2024

    # 2. Pass them to the template as keyword arguments: template_var=python_var
    return render_template(
        "about.html",
        company_name=company_name,
        founded_year=founded_year,
    )


@app.route("/service")
def service():
    return render_template("service.html")

if __name__ == "__main__":
    app.run(debug=True) 