# 📘 Comprehensive Flask & Jinja2 Study Guide

This study guide outlines all the core concepts covered in this repository, structured into interactive accordions with code examples and direct references to the files where each example is implemented.

---

<details>
<summary><h3>01. Flask Application Setup & WSGI Server</h3></summary>

#### Core Concept
Flask initializes an application instance using `Flask(__name__, template_folder="template")`. This object acts as the central WSGI application that receives HTTP requests and dispatches them to view functions. Setting `app.secret_key` enables encrypted session cookies, which are mandatory for flash messages.

#### Key Code
```python
from flask import Flask, render_template, request

app = Flask(__name__, template_folder="template")
app.secret_key = "flaskcraft-dev-secret-key-2026"

if __name__ == "__main__":
    app.run(debug=True)
```

#### Where to Find in Codebase
- File: [main.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/main.py#L1-L15)
- Running: `python main.py` runs on `http://127.0.0.1:5000`

</details>

---

<details>
<summary><h3>02. URL Routing & View Functions</h3></summary>

#### Core Concept
Routes map URL paths to Python callable functions using the `@app.route("<path>")` decorator. The function's return value is converted by Flask into an HTTP response.

#### Key Code
```python
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")
```

#### Where to Find in Codebase
- File: [main.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/main.py#L6-L10)

</details>

---

<details>
<summary><h3>03. HTTP Methods Handling (GET & POST)</h3></summary>

#### Core Concept
By default, routes only accept `GET` requests. To receive form submissions or API mutations, declare `methods=["GET", "POST"]` and inspect `request.method` inside the view function.

#### Key Code
```python
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        # Handle submission...
        return render_template("contact.html", success=True)
    return render_template("contact.html")
```

#### Where to Find in Codebase
- File: [main.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/main.py#L22-L59)
- Template: [template/contact.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/contact.html#L80-L115)

</details>

---

<details>
<summary><h3>04. URL Query Parameters (request.args.get)</h3></summary>

#### Core Concept
Query parameters (GET parameters) pass key-value pairs in the URL string after a `?` delimiter (e.g. `/service?tier=pro&promo=FLASK20`). Flask parses them into the `request.args` dictionary. Use `request.args.get(key, default)` to safely retrieve values with default fallbacks without throwing `KeyError`.

#### How URL Query Parameters Work in Flask (4 Steps):
1. **In the URL:** Appended after a question mark: `/service?tier=pro&promo=FLASK20`
2. **Reading in Python (`main.py`):** Flask provides the `request.args` dictionary:
   ```python
   tier = request.args.get("tier", default="all")
   promo = request.args.get("promo", default="FLASK20")
   ```
3. **Generating in Templates (`url_for`):** Pass extra arguments and Flask converts them into query strings:
   ```html
   <a href="{{ url_for('service', tier='pro', promo=discount_code) }}">Pro Plan</a>
   <!-- Generates: /service?tier=pro&promo=FLASK20 -->
   ```
4. **Pre-populating Form Input Boxes:** Bind the variable to the input's `value` attribute:
   ```html
   <input type="text" name="promo" value="{{ discount_code }}">
   <!-- Displays active or default promo code in the input box -->
   ```

#### Where to Find in Codebase
- File: [main.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/main.py#L96-L125)
- Template: [template/service.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/service.html#L84-L140)
- Interactive Study Topic: [template/study.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/study.html#L152-L195)

</details>

---

<details>
<summary><h3>05. Pre-populating HTML Form Inputs</h3></summary>

#### Core Concept
To provide default or preserved form values, pass the variable into the template and set the HTML `<input>` element's `value="{{ variable }}"` attribute. When the form uses `method="GET"`, submitting reflects the values back into the URL query parameters.

#### Key Code
```html
<form method="GET" action="{{ url_for('service') }}">
    <input 
        type="text" 
        name="promo" 
        value="{{ discount_code }}" 
        placeholder="Enter code"
    >
    <button type="submit">Apply Code</button>
</form>
```

#### Where to Find in Codebase
- Template: [template/service.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/service.html#L110-L135)

</details>

---

<details>
<summary><h3>06. Jinja2 Loops & Loop Helpers (loop.index)</h3></summary>

#### Core Concept
Iterate over lists and collections using `{% for item in items %}` and close with `{% endfor %}`. Jinja provides the built-in `loop` helper with attributes such as:
- `loop.index`: Current iteration (1-indexed)
- `loop.index0`: Current iteration (0-indexed)
- `loop.first`: True if this is the first item
- `loop.last`: True if this is the last item
- `loop.length`: Total count of items

#### Key Code
```html
{% for member in team %}
    <div class="team-card">
        <span>#{{ loop.index }}</span>
        <h3>{{ member.name }}</h3>
        <p>{{ member.role }}</p>
    </div>
{% endfor %}
```

#### Where to Find in Codebase
- Python Data: [main.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/main.py#L70-L83)
- Template: [template/about.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/about.html#L35-L65)
- Template: [template/contact.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/contact.html#L95-L98)

</details>

---

<details>
<summary><h3>07. Jinja2 Conditionals ({% if %}, {% elif %}, {% else %})</h3></summary>

#### Core Concept
Control rendering logic based on Python boolean values, comparisons, or list membership using `{% if %}`, `{% elif %}`, `{% else %}`, and `{% endif %}`.

#### Key Code
```html
{% if is_hiring %}
    <span class="badge-green">Actively Hiring!</span>
{% else %}
    <span class="badge-gray">No open roles</span>
{% endif %}

{% if selected_tier in ['all', 'starter'] %}
    <!-- Render Starter Pricing Card -->
{% endif %}
```

#### Where to Find in Codebase
- Template: [template/about.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/about.html#L48-L60)
- Template: [template/service.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/service.html#L140-L190)

</details>

---

<details>
<summary><h3>08. Template Inheritance ({% extends %} & {% block %})</h3></summary>

#### Core Concept
Template inheritance eliminates HTML duplication. The parent template (`base.html`) defines the HTML skeleton, shared `<head>` assets, header, and footer. Child templates inherit via `{% extends "base.html" %}` and fill specific slots using `{% block <name> %} ... {% endblock %}`.

#### Key Code
```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Default Title{% endblock %}</title>
</head>
<body>
    {% include 'components/navbar.html' %}
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>

<!-- child: home.html -->
{% extends "base.html" %}
{% block title %}Home | FlaskCraft{% endblock %}
{% block content %}
    <h1>Welcome to FlaskCraft</h1>
{% endblock %}
```

#### Where to Find in Codebase
- Parent: [template/base.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/base.html)
- Children: [home.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/home.html), [about.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/about.html), [service.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/service.html), [contact.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/contact.html)

</details>

---

<details>
<summary><h3>09. Modular Partials / Components ({% include %})</h3></summary>

#### Core Concept
Extract reusable components into dedicated files under `template/components/` and inject them using `{% include 'components/filename.html' %}`.

#### Key Code
```html
{% include 'components/navbar.html' %}
{% include 'components/flash_messages.html' %}
{% include 'components/footer.html' %}
```

#### Where to Find in Codebase
- [template/components/navbar.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/components/navbar.html)
- [template/components/footer.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/components/footer.html)
- [template/components/flash_messages.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/components/flash_messages.html)

</details>

---

<details>
<summary><h3>10. Static Assets: url_for() vs Direct Paths</h3></summary>

#### Core Concept
Static assets (CSS, JavaScript, SVG, images) can be resolved dynamically via Flask's `url_for('static', filename='...')` helper or linked directly from the root path `/static/...`. The `url_for` method is preferred for production as it automatically adjusts for application roots and reverse proxies.

#### Key Code
```html
<!-- Via url_for helper: -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

<!-- Via direct path: -->
<link rel="icon" type="image/svg+xml" href="/static/images/favicon.svg">
<script src="/static/js/main.js"></script>
```

#### Where to Find in Codebase
- File: [template/base.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/base.html#L14-L37)
- Directory: [static/](https://github.com/Shrikant92Bhatt/python-flask/blob/main/static)

</details>

---

<details>
<summary><h3>11. Dynamic URL Generation with url_for()</h3></summary>

#### Core Concept
`url_for('<view_function_name>', **values)` dynamically computes URLs based on function names rather than hardcoded URLs. Any extra keyword arguments are automatically appended as URL query parameters.

#### Key Code
```html
<a href="{{ url_for('home') }}">Home</a>
<a href="{{ url_for('service', tier='pro', promo='FLASK20') }}">Pro with Promo</a>
<!-- Resulting URL: /service?tier=pro&promo=FLASK20 -->
```

#### Where to Find in Codebase
- [template/components/navbar.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/components/navbar.html)
- [template/service.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/service.html#L85-L95)

</details>

---

<details>
<summary><h3>12. Modular Architecture with Flask Blueprints</h3></summary>

#### Core Concept
Flask Blueprints allow decomposing an application into reusable, isolated modules across separate Python files. Each Blueprint can have its own routes, URL prefixes, and templates.

#### Key Code
```python
# In api.py:
from flask import Blueprint, jsonify
api_bp = Blueprint("api", __name__, url_prefix="/api")

# In main.py:
from api import api_bp
from flash_demo import flash_bp

app.register_blueprint(api_bp)
app.register_blueprint(flash_bp)
```

#### Where to Find in Codebase
- [api.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/api.py)
- [flash_demo.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/flash_demo.py)
- [main.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/main.py)

</details>

---

<details>
<summary><h3>13. REST APIs & JSON Serialization with jsonify</h3></summary>

#### Core Concept
Flask's `jsonify()` serializes Python dictionaries/lists into JSON strings, sets the `Content-Type: application/json` header, and pairs with appropriate HTTP status codes (200 OK, 201 Created, 400 Bad Request, 404 Not Found, 422 Unprocessable). Use `request.get_json()` to parse incoming JSON payloads.

#### Key Code
```python
@api_bp.route("/services", methods=["GET"])
def get_services():
    return jsonify({"success": True, "count": len(services), "data": services}), 200

@api_bp.route("/inquiries", methods=["POST"])
def create_inquiry():
    payload = request.get_json()
    if not payload or "name" not in payload:
        return jsonify({"success": False, "error": "Invalid payload"}), 400
    return jsonify({"success": True, "data": payload}), 201
```

#### Where to Find in Codebase
- File: [api.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/api.py)
- Test endpoints:
  - `GET /api/health`
  - `GET /api/services`
  - `GET /api/promo/validate?code=FLASK20`
  - `POST /api/inquiries`

</details>

---

<details>
<summary><h3>14. Flask Flash Messages, Login & Logout Flow, and Floating Toasts</h3></summary>

#### Core Concept
Flash messages allow storing temporary feedback notifications in the user's encrypted session cookie. The notification is displayed on the next request and immediately discarded.
- In Authentication: Used on **Login** (success/error alerts), **Logout** (session destroyed confirmation), and **Protected Pages** (access denied warnings).
- As Floating Toasts: Rendered using a fixed top-right **Toast notification component** (`toast.html`) featuring auto-dismissal, icons, and progress timers instead of jarring inline page alerts.
- In Python: `flash(message, category)` then `redirect(url_for(...))` (Post/Redirect/Get pattern)
- In Jinja: `get_flashed_messages(with_categories=True)`
- Requires: `app.secret_key = "..."`

#### Key Code
```python
# Auth Login Route in auth.py:
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if check_credentials(username, password):
            session["user"] = username
            flash(f"Welcome back, {username.title()}! You have successfully logged in.", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials! Please check your username and password.", "danger")
            return render_template("login.html")
    return render_template("login.html")

# Auth Logout Route in auth.py:
@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been safely logged out.", "info")
    return redirect(url_for("auth.login"))
```

```html
<!-- Floating Toast Component (components/toast.html): -->
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
    <div class="toast-container" id="toast-container">
        {% for category, message in messages %}
        <div class="toast-card toast-{{ category }}">
            <span class="toast-icon">✓</span>
            <div class="toast-content">{{ message }}</div>
            <button class="toast-close-btn" onclick="dismissToast(this.closest('.toast-card'))">✕</button>
        </div>
        {% endfor %}
    </div>
    {% endif %}
{% endwith %}
```

#### Where to Find in Codebase
- Auth Backend: [auth.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/auth.py)
- Login Template: [template/login.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/login.html)
- Dashboard Template: [template/dashboard.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/dashboard.html)
- Floating Toast Component: [template/components/toast.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/components/toast.html)
- Interactive Demo: [template/flash_demo.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/flash_demo.html)

</details>
