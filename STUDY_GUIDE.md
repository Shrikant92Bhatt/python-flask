# 📘 Comprehensive Flask & Jinja2 Study Guide

This comprehensive study guide details 20 core Flask and Jinja architectural concepts implemented in this repository. Each section provides in-depth under-the-hood mechanics, execution lifecycles, production code implementations, common pitfalls, and direct links to the codebase.

---

<details>
<summary><h3>01. Flask Application Setup & WSGI Server (main.py)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
The Web Server Gateway Interface (WSGI, PEP 3333) standardizes communication between Python web applications and web servers. In Flask, `Flask(__name__) instantiates the central WSGI application callable. It resolves root filesystem paths, binds application configuration, registers URL routing rules, and configures secure session handling.

> **How Flask Works Under the Hood:** When an HTTP request reaches the server, the WSGI server invokes `app(environ, start_response). Flask wraps the low-level CGI `environ dictionary into a high-level `Request object, matches the request URL against its routing map, dispatches execution to the corresponding view function, and converts the return value into a `Response byte stream. In local development, `app.run(debug=True) launches Werkzeug's local supervisor and child reloader process (using StatReloader or Watchdog). It mounts an interactive browser debugging console protected by a PIN. In production environments, `debug=True must never be enabled because it permits arbitrary remote code execution. Instead, a multi-worker production WSGI server like Gunicorn or uWSGI must manage worker concurrency.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Root Path Resolution:** Flask inspects `__name__ to detect whether it is running as a standalone module or package, accurately determining absolute filesystem paths for templates and static files.
2. **WSGI Callable Registration:** The `Flask class implements the Python `__call__ dunder method to adhere strictly to PEP 3333 WSGI compliance.
3. **Cryptographic Secret Key Configuration:** Assigning `app.secret_key provides the cryptographic seed used by the `itsdangerous serializer to sign session cookies and flash messages.
4. **Blueprint and Extension Registration:** Modular blueprints (API, Auth, Flash) and extensions are registered onto the central application object before request handling begins.
5. **Server Dispatch & Execution:** Executing `app.run() starts the development HTTP server, binding to the configured host and port (default `127.0.0.1:5000).

#### 💻 Production-Grade Code Implementation (main.py & Production Setup)
```python
from flask import Flask, render_template, request
import os

# Initialize Flask application with explicit custom template directory
app = Flask(__name__, template_folder="template")

# Secret key for cryptographically signing session cookies & flash messages
# In production, always load from an environment variable:
app.secret_key = os.environ.get("SECRET_KEY", "flaskcraft-dev-secret-key-2026")

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    # Local development server with auto-reload and traceback console:
    # WARNING: Never run debug=True in production!
    app.run(host="127.0.0.1", port=5000, debug=True)

# -------------------------------------------------------------
# Production WSGI Deployment Command (e.g. Gunicorn):
# gunicorn --workers 4 --bind 0.0.0.0:5000 --access-logfile - main:app
# -------------------------------------------------------------
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Production Debug Vulnerability:** Leaving `debug=True enabled on public servers exposes the Werkzeug interactive debugging shell, allowing unauthenticated attackers to execute arbitrary Python commands on your server.

**Missing Secret Key:** Forgetting `app.secret_key will raise a `RuntimeError: The session is unavailable because no secret key was set whenever session or flash operations run.

#### 📊 Technical Reference & Attributes Matrix
| Parameter / Attribute | Type | Purpose | Default Value |
| --- | --- | --- | --- |
| `import_name | str | Identifies root package to resolve template and static asset paths | Mandatory (usually `__name__) |
| `template_folder | str | Subdirectory path containing Jinja HTML template files | `'templates' (customized to `'template') |
| `static_folder | str | Subdirectory path containing public static assets (CSS, JS, images) | `'static' |
| `secret_key | str / bytes | Cryptographic seed for signing session cookies and flash queues | `None (Must be set for sessions) |
| `debug | bool | Activates live file auto-reloader and interactive traceback debugger | `False |

#### 📍 Where to Find in Codebase
- File: [main.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/main.py#L1-L15)

</details>

---

<details>
<summary><h3>02. URL Routing, View Functions & Parameter Converters (main.py)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Routing maps incoming HTTP request URL paths to corresponding Python view functions using the `@app.route() decorator. Flask leverages Werkzeug's routing engine to compile route definitions into regex patterns, extract dynamic URL path parameters, and validate data types with built-in parameter converters.

> **How Flask Works Under the Hood:** Under the hood, each `@app.route() call constructs a `werkzeug.routing.Rule object and registers it inside `app.url_map (an instance of `werkzeug.routing.Map). When a request arrives, `url_map.bind_to_environ(environ) analyzes the requested path against all registered rules. If dynamic converters like `&lt;int:id&gt; are present, Werkzeug's converter executes regex matching, casts the path fragment to a Python integer, and injects it as a keyword argument into the view function. Flask strictly follows RFC 3986 URL canonicalization: if a route is defined with a trailing slash (e.g. `/projects/), a visit to `/projects triggers an automatic HTTP 308 Permanent Redirect. If defined without a trailing slash, requesting with a slash yields an HTTP 404.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Route Registration:** Decorator registers URL path, supported HTTP methods, and endpoint name into `app.url_map.
2. **Request URL Matching:** Werkzeug matches incoming request path against compiled regular expression patterns in the routing table.
3. **Type Coercion via Converters:** Path parameters are validated and converted into Python primitives (`int, `uuid, etc.).
4. **View Function Invocation:** Flask invokes the associated view function, passing extracted path variables as keyword arguments.
5. **Response Transformation:** The function return value (string, template, dict, or tuple) is coerced into an HTTP `Response object.

#### 💻 Production-Grade Code Implementation (main.py (Route Definitions))
```python
from flask import render_template, abort

# 1. Static Route
@app.route("/")
def home():
    return render_template("home.html")

# 2. Dynamic Route with Multiple Converters
@app.route("/projects/<string:category>/<int:project_id>")
def project_detail(category, project_id):
    # category is typed as str, project_id is guaranteed to be an int
    if project_id <= 0:
        abort(404)
    return render_template("project.html", category=category, project_id=project_id)

# 3. Path Converter (matches across multiple slashes)
@app.route("/docs/<path:subpath>")
def documentation(subpath):
    return render_template("docs.html", doc_path=subpath)
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**String vs Integer Casting:** Omitting the converter type (e.g. `&lt;user_id&gt; instead of `&lt;int:user_id&gt;) passes the parameter as a string, causing bugs in database lookups or mathematical checks.

**Trailing Slash Inconsistencies:** Navigating to `/service/ when the route is defined as `/service returns a 404 error instead of redirecting.

#### 📊 Technical Reference & Attributes Matrix
| Converter | Syntax | Accepted Input | Python Type |
| --- | --- | --- | --- |
| `string (default) | `&lt;string:var&gt; | Any text without slashes | `str |
| `int | `&lt;int:var&gt; | Positive integers only | `int |
| `float | `&lt;float:var&gt; | Positive floating point numbers | `float |
| `path | `&lt;path:var&gt; | Accepts slashes and directory sub-paths | `str |
| `uuid | `&lt;uuid:var&gt; | Accepts 36-character UUID strings | `uuid.UUID |

#### 📍 Where to Find in Codebase
- File: [main.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/main.py#L15-L20)

</details>

---

<details>
<summary><h3>03. HTTP Methods Handling (GET, POST & The PRG Pattern) (main.py & contact.html)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
HTTP methods express the intended action of a request. By default, Flask routes only accept `GET requests. Specifying `methods=["GET", "POST"] enables a single view function to render an HTML form on initial visit and process incoming form payloads upon submission.

> **How Flask Works Under the Hood:** When handling a POST submission with `application/x-www-form-urlencoded or `multipart/form-data, Flask parses the request stream into `request.form, an instance of `werkzeug.datastructures.ImmutableMultiDict. This data structure is strictly read-only; attempts to mutate keys raise a `TypeError. Furthermore, accessing a non-existent key via bracket subscripting `request.form["missing"] raises a `BadRequestKeyError (which Flask transforms into an HTTP 400 Bad Request). Safe extraction requires `request.form.get("key", default=None). Production form handling should implement the Post/Redirect/Get (PRG) pattern: after processing a successful POST, return an HTTP 302/303 redirect rather than rendering a template directly, preventing the browser from prompting 'Confirm Form Resubmission' if the user refreshes.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Method Declaration:** Pass allowed verbs via `methods=["GET", "POST"] in the route decorator.
2. **Method Discrimination:** Check `if request.method == "POST": to branch form processing logic away from initial page rendering.
3. **Safe Field Extraction:** Extract values using `request.form.get("field_name", "").strip() to avoid unhandled 400 exceptions.
4. **Server-Side Validation:** Verify required inputs, data formats, and business constraints before executing database writes.
5. **PRG Redirect & Flash:** Store a feedback notification with `flash() and return `redirect(url_for(...)).

#### 💻 Production-Grade Code Implementation (main.py (Contact Form Processing))
```python
from flask import request, render_template, redirect, url_for, flash

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # 1. Safely extract form values without throwing BadRequestKeyError
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        # 2. Server-side validation
        if not name or not email or not message:
            flash("All form fields are mandatory!", "warning")
            return render_template("contact.html", name=name, email=email)

        # 3. Process business logic (e.g. database save or email dispatch)
        save_inquiry(name, email, message)

        # 4. Post/Redirect/Get (PRG) pattern prevents duplicate submissions
        flash(f"Thank you {name}! Your message has been sent.", "success")
        return redirect(url_for("contact"))

    # Initial GET request renders clean form
    return render_template("contact.html")
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Bracket Subscripting Exception:** Using `request.form["email"] crashes with an HTTP 400 Bad Request if the user omits or tampers with the form field. Always use `request.form.get("email").

**Missing PRG Pattern:** Directly calling `render_template() upon POST causes browsers to warn about resubmitting data if refreshed or backed into.

#### 📊 Technical Reference & Attributes Matrix
| HTTP Method | Idempotent? | Safe? | Primary Use Case in Web Apps |
| --- | --- | --- | --- |
| `GET | Yes | Yes | Retrieve and view pages, search results, or read API resources |
| `POST | No | No | Submit forms, create new records, authenticate credentials |
| `PUT | Yes | No | Completely replace an existing resource with a new payload |
| `PATCH | No | No | Partially update specific fields of an existing resource |
| `DELETE | Yes | No | Remove an existing resource from the server |

#### 📍 Where to Find in Codebase
- File: [main.py & template/contact.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/main.py#L31-L69)

</details>

---

<details>
<summary><h3>04. URL Query Parameters (request.args.get & Type Coercion) (main.py & service.html)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Query parameters (GET parameters) pass serialized key-value pairs in the URL string following the `? delimiter (e.g., `/service?tier=pro&promo=FLASK20&page=2). Flask parses them into `request.args, enabling clean state-sharing, pagination, search queries, and dynamic filters without mutating database records.

> **How Flask Works Under the Hood:** The WSGI server receives the raw URL query string in `environ["QUERY_STRING"]. Flask decodes this via Werkzeug's `url_decode() and populates `request.args as an `ImmutableMultiDict. A powerful feature is the `type parameter in `request.args.get(key, default, type=int): if a user navigates to `?page=invalid, Flask catches the `ValueError internally and cleanly falls back to the default integer without crashing your application. When dealing with multi-value query strings (e.g. `?category=python&category=flask), calling `get() returns only the first value; use `request.args.getlist("category") to obtain all occurrences as a Python list.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Client Request Formulation:** Browser constructs URL with query string: `/service?tier=pro&promo=FLASK20.
2. **Server-Side WSGI Parsing:** Flask parses raw query string into `request.args (ImmutableMultiDict).
3. **Safe Fallback & Type Coercion:** View extracts parameters using `request.args.get("tier", default="all") and `type=int.
4. **Business Logic Execution:** Data is filtered, discounted, or paginated based on the extracted parameters.
5. **Template Variable Passing:** Values are forwarded to Jinja to highlight active filters and pre-fill form input boxes.

#### 💻 Production-Grade Code Implementation (main.py (Service Route Query Parameters))
```python
from flask import request, render_template

@app.route("/service")
def service():
    # 1. Read query parameters with safe default values
    selected_tier = request.args.get("tier", default="all").lower()
    promo_code = request.args.get("promo", default="FLASK20").strip().upper()
    
    # 2. Type coercion for numerical parameters (falls back gracefully on non-integers)
    page = request.args.get("page", default=1, type=int)
    
    # 3. Multi-value checkbox extraction: ?features=api&features=auth
    selected_features = request.args.getlist("features")

    # 4. Dictionary lookup for business logic
    promo_discounts = {"FLASK20": 20, "SUMMER50": 50, "WELCOME10": 10}
    discount_pct = promo_discounts.get(promo_code, 0)

    return render_template(
        "service.html",
        selected_tier=selected_tier,
        discount_code=promo_code,
        discount_percent=discount_pct,
        page=page
    )
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Missing Type Coercion:** Reading `page = int(request.args.get("page", 1)) will raise an unhandled `ValueError and return an HTTP 500 error if someone types `?page=abc. Always use `request.args.get("page", 1, type=int).

**Single vs Multi-Value:** Using `request.args.get("tag") on a URL with repeated keys `?tag=a&tag=b only returns `'a'. Always use `request.args.getlist("tag").

#### 📊 Technical Reference & Attributes Matrix
| Method / Attribute | Signature | Description | Example Return |
| --- | --- | --- | --- |
| `get() | `args.get(key, default=None) | Safely retrieves first matching value with fallback | `'pro' |
| `get(type=...) | `args.get(key, 1, type=int) | Coerces value to specified type; returns default on ValueError | `1 |
| `getlist() | `args.getlist(key) | Retrieves all occurrences of repeated query parameter keys as a list | `['pro', 'enterprise'] |
| `keys() | `args.keys() | Returns an iterator over all unique query parameter keys | `dict_keys(['tier', 'promo']) |

#### 📍 Where to Find in Codebase
- File: [main.py & template/service.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/main.py#L105-L134)

</details>

---

<details>
<summary><h3>05. Pre-populating Form Inputs via Jinja & Preventing XSS (service.html & contact.html)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Form pre-population retains user selections or displays server defaults across page reloads. Whether populating promo codes from query parameters or preserving entered text when validation fails, Jinja binds variables directly to HTML input attributes with automatic contextual escaping to prevent Cross-Site Scripting (XSS).

> **How Flask Works Under the Hood:** Different HTML form control elements bind values through distinct attributes: standard input boxes (`text, `email, `hidden) bind via the `value="..." attribute; `&lt;textarea&gt; elements do NOT support the `value attribute and must enclose the text between opening and closing tags; checkboxes and radio inputs require conditional evaluation to render the boolean `checked attribute; and `&lt;select&gt; option items require the `selected attribute. Jinja2 automatically escapes HTML entities inside `{{ ... }} tags by converting special characters (`&lt;, `&gt;, `&amp;, `&quot;) into HTML entities, preventing attribute breakout exploits (such as injecting `" onfocus="alert(1)).

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Server-Side Variable Binding:** Flask view supplies default, query, or previously submitted values into `render_template().
2. **Attribute Target Selection:** Identify appropriate HTML attribute: `value, inner content, `checked, or `selected.
3. **Jinja Context Interpolation:** Render variable using double curly braces: `value="{{ discount_code }}".
4. **Automatic Entity Escaping:** Jinja converts quotes and malicious tags into safe HTML character entities.
5. **User Experience Preservation:** The browser displays pre-populated fields immediately upon initial rendering.

#### 💻 Production-Grade Code Implementation (template/service.html & template/contact.html)
```html
<!-- 1. Text Input Field (binds via value attribute) -->
<input 
    type="text" 
    name="promo" 
    id="promo-input" 
    class="form-control" 
    value="{{ discount_code }}" 
    placeholder="e.g. FLASK20"
>

<!-- 2. Textarea (enclosed between tags, NOT value attribute!) -->
<textarea name="message" id="message" class="form-control">{{ message|default('') }}</textarea>

<!-- 3. Dropdown Select Option (conditional selected attribute) -->
<select name="tier" class="form-control">
    <option value="all" {% if selected_tier == 'all' %}selected{% endif %}>All Plans</option>
    <option value="starter" {% if selected_tier == 'starter' %}selected{% endif %}>Starter Plan</option>
    <option value="pro" {% if selected_tier == 'pro' %}selected{% endif %}>Pro Plan</option>
</select>

<!-- 4. Checkbox (conditional checked attribute) -->
<input type="checkbox" name="newsletter" value="yes" {% if subscribe %}checked{% endif %}>
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Textarea Value Attribute Bug:** Writing `&lt;textarea value="{{ text }}"&gt;&lt;/textarea&gt; will fail in all web browsers because textareas ignore the value attribute. Text must go between tags: `&lt;textarea&gt;{{ text }}&lt;/textarea&gt;.

**Bypassing Escaping with | safe:** Applying `| safe to user-submitted input inside attributes allows attribute breakouts and XSS attacks.

#### 📊 Technical Reference & Attributes Matrix
| Form Control Type | HTML Element | Pre-population Syntax | Common Mistake |
| --- | --- | --- | --- |
| Text / Email / Number | `&lt;input type="text"&gt; | `value="{{ val }}" | Omitting quotes around attribute |
| Multi-line Text | `&lt;textarea&gt; | `&lt;textarea&gt;{{ val }}&lt;/textarea&gt; | Attempting `value="{{ val }}" |
| Dropdown Select | `&lt;option&gt; | `{% if val == opt %}selected{% endif %} | Placing `selected on `&lt;select&gt; tag |
| Checkbox / Radio | `&lt;input type="checkbox"&gt; | `{% if checked %}checked{% endif %} | Setting `value="true" instead of `checked |

#### 📍 Where to Find in Codebase
- File: [template/service.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/service.html#L38-L55)

</details>

---

<details>
<summary><h3>06. Jinja2 Loops, Loop Metadata & The {% else %} Clause (about.html & contact.html)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Jinja2 `{% for %} loops iterate over collections (lists, tuples, dictionaries, querysets) to dynamically generate repeated HTML structures. Jinja injects a special `loop context object that exposes zero-overhead iteration metadata such as indices, boundary flags, and alternating cycle helpers.

> **How Flask Works Under the Hood:** Jinja compiles template AST blocks into native Python bytecode. When compiling a `for loop, it wraps the iteration inside a `LoopContext. The `loop object provides convenient properties: `loop.index (1-based index), `loop.index0 (0-based index), `loop.first (boolean indicating first iteration), and `loop.last (boolean indicating final iteration). A commonly overlooked feature is Jinja's `{% else %} loop clause: if the iterable is empty (or evaluates to False), the `{% else %} branch renders immediately, eliminating the need to wrap loops in defensive `{% if items %} checks.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Data Structure Preparation:** View function packages list or dictionary into the template context dictionary.
2. **Loop AST Execution:** Jinja initiates loop block and binds the current element to the loop variable.
3. **LoopContext Metadata Injection:** Jinja automatically computes `loop.index, `loop.first, and `loop.last.
4. **HTML Block Generation:** DOM snippet is rendered for each item in the collection.
5. **Empty Fallback Handling:** If collection contains zero elements, the optional `{% else %} block executes.

#### 💻 Production-Grade Code Implementation (template/about.html (Team Cards & Milestones))
```html
<!-- Iterating over list of team member dictionaries with loop helpers -->
<div class="team-grid">
    {% for member in team %}
    <article class="glass-card team-card {% if loop.first %}team-card-featured{% endif %}">
        <div class="card-badge">
            Member #{{ loop.index }} of {{ loop.length }}
        </div>
        <h3>{{ member.name }}</h3>
        <p class="role">{{ member.role }}</p>
        <span class="experience">{{ member.experience }} years experience</span>
        {% if loop.last %}
            <span class="badge-tag">Newest Addition</span>
        {% endif %}
    </article>
    {% else %}
    <!-- Renders automatically if team list is empty -->
    <div class="empty-state">
        <p>No team members are currently listed.</p>
    </div>
    {% endfor %}
</div>
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**1-Based vs 0-Based Indices:** Confusing `loop.index (starts at 1) with `loop.index0 (starts at 0) leads to off-by-one errors in CSS IDs and rankings.

**Dictionary Iteration Traps:** Writing `{% for item in my_dict %} only yields dictionary keys. To access both keys and values, write `{% for key, val in my_dict.items() %}.

#### 📊 Technical Reference & Attributes Matrix
| Loop Variable | Type | Description | Common Use Case |
| --- | --- | --- | --- |
| `loop.index | int | 1-based iteration counter (1, 2, 3...) | Numbered lists, step badges, ranking cards |
| `loop.index0 | int | 0-based iteration counter (0, 1, 2...) | Array indexing, data-offset HTML attributes |
| `loop.first | bool | True if on the first iteration | Applying special highlight or featured styling |
| `loop.last | bool | True if on the final iteration | Omitting bottom divider or appending closing tags |
| `loop.length | int | Total number of items in the iterable | Displaying 'Item X of Total' counters |
| `loop.cycle('a', 'b') | helper | Alternates between given values on each iteration | Zebra striping table rows (`row-even, `row-odd) |

#### 📍 Where to Find in Codebase
- File: [template/about.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/about.html#L70-L135)

</details>

---

<details>
<summary><h3>07. Jinja2 Conditionals (if, elif, else & Built-in Tests) (about.html & service.html)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Conditionals (`{% if %}, `{% elif %}, `{% else %}) dynamically control DOM rendering based on boolean flags, values, membership expressions, and Jinja test operators (`is defined, `is none).

> **How Flask Works Under the Hood:** Jinja evaluates truthiness according to standard Python rules: empty strings (`""), numeric zero (`0), `None, empty lists (`[]), and empty dictionaries (`{}) evaluate to `False. Jinja also provides test expressions invoked via the `is keyword (e.g. `var is defined, `var is none, `num is even). Unlike Python where checking an undefined variable raises a `NameError, Jinja resolves undefined variables to a special `Undefined object (rendering as an empty string) unless `StrictUndefined is configured.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Context Variable Evaluation:** Jinja checks expression passed to `{% if %}.
2. **Operator & Test Evaluation:** Evaluates boolean logic, membership operators (`in), or Jinja tests (`is).
3. **Branch Execution:** Renders the first block whose condition evaluates to truthy.
4. **Fallback Branch Execution:** If all previous branches evaluate to false, renders the optional `{% else %} block.
5. **DOM Cleanup:** Unmatched branches are omitted completely from the compiled output.

#### 💻 Production-Grade Code Implementation (template/about.html & template/service.html)
```html
<!-- 1. Simple Boolean Flag Evaluation -->
{% if is_hiring %}
    <span class="badge badge-success">We are hiring! Join our engineering team.</span>
{% else %}
    <span class="badge badge-neutral">Applications closed for this quarter.</span>
{% endif %}

<!-- 2. Membership & Multi-Branch Logic -->
{% if selected_tier == 'pro' %}
    <div class="pricing-highlight">Displaying Pro Tier Specifications</div>
{% elif selected_tier in ['starter', 'enterprise'] %}
    <div class="pricing-highlight">Displaying Alternative Tier: {{ selected_tier|title }}</div>
{% else %}
    <div class="pricing-highlight">Displaying All Available Tiers</div>
{% endif %}

<!-- 3. Jinja 'is' Test Expressions -->
{% if current_discount is not none and current_discount > 0 %}
    <div class="promo-banner">Special Discount: {{ current_discount }}% OFF!</div>
{% endif %}
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Using JS or Python Syntax:** Writing `{% if a && b %} or `{% if a is None %} causes template syntax errors. In Jinja, use `and, `or, and `is none.

**Silent Undefined Variables:** If a variable name is misspelled (e.g. `{% if invalid_var %}), Jinja treats it as False without warning unless `StrictUndefined is explicitly configured.

#### 📊 Technical Reference & Attributes Matrix
| Jinja Test | Syntax | Behavior | Python Equivalent |
| --- | --- | --- | --- |
| `defined | `{% if var is defined %} | True if variable exists in template context | `'var' in locals() |
| `none | `{% if var is none %} | True if variable is explicitly `None | `var is None |
| `even / odd | `{% if loop.index is even %} | True if integer is divisible by 2 | `val % 2 == 0 |
| `number | `{% if val is number %} | True if value is int or float | `isinstance(val, (int, float)) |
| `iterable | `{% if list is iterable %} | True if value can be iterated over | `isinstance(val, Iterable) |

#### 📍 Where to Find in Codebase
- File: [template/about.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/about.html#L18-L45)

</details>

---

<details>
<summary><h3>08. Template Inheritance (extends, block & super()) (base.html & all child pages)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Template inheritance inverts presentation control: a master layout (`base.html) defines the global HTML document scaffolding (head, metadata, navigation, footer, toast containers), while child templates extend the layout and override designated `{% block %} regions.

> **How Flask Works Under the Hood:** During AST compilation, Jinja detects the `{% extends %} tag at the top of a child template. It compiles the parent template and replaces each parent `BlockNode with the matching block AST from the child. Any HTML written outside of a `{% block %} inside a child template is completely discarded. If a child block needs to append or prepend content rather than replacing the parent block entirely, it calls `{{ super() }}. This is critical when appending page-specific scripts without wiping global scripts.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Master Layout Construction:** `base.html establishes document structure with named blocks: `title, `extra_css, `content, `scripts.
2. **Child Template Declaration:** Child declares `{% extends "base.html" %} as its very first tag.
3. **Block Region Overriding:** Child overrides specific blocks, providing targeted HTML and CSS links.
4. **Parent Block Chaining via super():** Child calls `{{ super() }} to retain parent styles or scripts while appending new ones.
5. **Composite DOM Assembly:** Jinja merges the AST trees into a single, cohesive HTML response.

#### 💻 Production-Grade Code Implementation (template/base.html vs template/home.html)
```html
<!-- In template/base.html (Master Skeleton) -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Default Title | FlaskCraft{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'components/navbar.html' %}
    <main>
        {% block content %}{% endblock %}
    </main>
    {% include 'components/footer.html' %}
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>

<!-- In template/home.html (Child Template) -->
{% extends "base.html" %}

{% block title %}Home | Modern Flask Platform{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="/static/css/home.css">
{% endblock %}

{% block content %}
<section class="hero-section">
    <h1>Welcome to FlaskCraft</h1>
</section>
{% endblock %}
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Placing Markup Outside Blocks:** Any text or HTML tags placed outside `{% block %} tags in an extending template will be silently discarded by Jinja.

**Missing First Tag Rule:** `{% extends %} must be the first non-comment tag in the file; placing HTML above it breaks template inheritance.

#### 📊 Technical Reference & Attributes Matrix
| Block Name | Declared In | Purpose | Default Fallback |
| --- | --- | --- | --- |
| `title | `&lt;head&gt; | Defines page title for browser tab and SEO | `FlaskCraft |
| `meta_description | `&lt;head&gt; | Custom search engine snippet description | Global site description |
| `extra_css | `&lt;head&gt; | Injects page-specific modular stylesheets | Empty (loads base.css only) |
| `content | `&lt;main&gt; | Main unique page body content | Empty |
| `scripts | Before `&lt;/body&gt; | Injects page-specific JavaScript modules | Empty (loads main.js only) |

#### 📍 Where to Find in Codebase
- File: [template/base.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/base.html#L1-L70)

</details>

---

<details>
<summary><h3>09. Modular Partials & Component Architecture (include) (components/ & base.html)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
The `{% include %} tag renders external template fragments and injects their output directly into the host template. This encapsulates reusable UI components (navigation bars, footers, toast notifications, pricing tables) into independent, maintainable partials under `template/components/.

> **How Flask Works Under the Hood:** When Jinja processes an `include, it fetches the referenced template file, compiles it, and renders it using the caller's active context (`with context by default). All variables in scope in the parent template (such as `request, `session, and user variables) are automatically accessible inside the included component. To isolate components and prevent unintentional side effects, you can append `without context. Furthermore, passing `ignore missing prevents template errors if an optional component file is missing.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Component Identification:** Identify repeated UI elements (Navbar, Footer, Toast notifications).
2. **Partial File Creation:** Extract snippet into dedicated file under `template/components/filename.html.
3. **Template Embedding:** Embed component using `{% include 'components/filename.html' %}.
4. **Context Sharing or Scoping:** Component inherits parent variables or executes isolated via `without context.
5. **Single Source of Truth:** Updates to the partial automatically propagate across all pages referencing it.

#### 💻 Production-Grade Code Implementation (template/base.html & template/components/navbar.html)
```html
<!-- In template/base.html -->
<header class="navbar-wrapper">
    <!-- Embed modular navigation component -->
    {% include 'components/navbar.html' %}
</header>

<!-- Embed global toast notification container -->
{% include 'components/toast.html' %}

<main class="page-body">
    {% block content %}{% endblock %}
</main>

<!-- Embed modular footer component -->
{% include 'components/footer.html' %}

<!-- Optional snippet inclusion with ignore missing flag -->
{% include 'components/analytics.html' ignore missing without context %}
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Include vs Extends Confusion:** Using `include for entire page skeletons instead of `extends causes layout duplication and breaks block overrides.

**Variable Shadowing:** Because included templates share the host context by default, variable names inside components can overwrite or collide with host variables.

#### 📊 Technical Reference & Attributes Matrix
| Inclusion Syntax | Context Behavior | Missing File Behavior | Ideal Use Case |
| --- | --- | --- | --- |
| `{% include 'f.html' %} | Shares host context | Raises TemplateNotFound exception | Standard UI partials (Navbar, Footer) |
| `{% include 'f.html' with context %} | Explicitly shares context | Raises TemplateNotFound exception | Components requiring request/session state |
| `{% include 'f.html' without context %} | Strictly isolated context | Raises TemplateNotFound exception | Pure UI widgets independent of host state |
| `{% include 'f.html' ignore missing %} | Shares host context | Silently skips if file does not exist | Optional feature flags, tracking snippets |

#### 📍 Where to Find in Codebase
- File: [template/base.html & template/components/](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/base.html#L28-L55)

</details>

---

<details>
<summary><h3>10. Static Assets Management (url_for vs Direct Path) (static/ & base.html)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Static assets (stylesheets, JavaScript files, images, SVG icons, fonts) reside in the `static/ directory. Flask exposes a built-in static endpoint that can be referenced dynamically using `url_for('static', filename='...') or via direct root-relative paths like `/static/....

> **How Flask Works Under the Hood:** When the Flask application boots, it automatically registers a route: `@app.route('/static/&lt;path:filename&gt;') mapped to the internal endpoint `static. Calling `url_for('static', filename='css/base.css') returns `/static/css/base.css. In production, serving static files directly through Python/WSGI is an anti-pattern: web servers like Nginx, Apache, or CDN proxies (Cloudflare, AWS CloudFront) should intercept `/static/ requests and serve them directly from storage with gzip/brotli compression and long-lived `Cache-Control headers (e.g. `max-age=31536000, immutable). Adding query-string version hashes (e.g. `?v=2026.1) enables instant cache invalidation upon redeployment.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Asset Organization:** Organize assets into subdirectories: `static/css/, `static/js/, `static/images/.
2. **Dynamic URL Resolution:** Reference assets via `url_for('static', filename='...') in templates.
3. **Cache Invalidation (Cache Busting):** Append version query parameters (`?v=2.0) to force browsers to reload updated assets.
4. **MIME Type Verification:** Flask automatically determines correct HTTP `Content-Type headers based on file extensions.
5. **Production Reverse Proxying:** Configure Nginx or CDN to serve `/static/ directly without hitting Python workers.

#### 💻 Production-Grade Code Implementation (template/base.html & template/about.html)
```html
<!-- Option 1: Dynamic url_for Resolver (Recommended for caching & subpath hosting) -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
<link rel="icon" type="image/svg+xml" href="{{ url_for('static', filename='images/favicon.svg') }}">

<!-- Option 2: Direct Root-Relative Path (Clean, modular child page inclusion) -->
<link rel="stylesheet" href="/static/css/study.css">

<!-- Cache Busting with Version Parameter -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/base.css', v='2026.1') }}">

<!-- Dynamic Script Loading -->
<script src="{{ url_for('static', filename='js/main.js') }}" defer></script>
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Hardcoding OS File Paths:** Using local Windows filesystem paths (e.g. `C:\static\style.css) in HTML breaks completely when deployed to Linux or accessed via HTTP.

**Serving Media via WSGI in Production:** Forcing Gunicorn workers to stream multi-megabyte videos or images ties up worker threads and degrades web throughput.

#### 📊 Technical Reference & Attributes Matrix
| Approach | Syntax | Pros | Cons |
| --- | --- | --- | --- |
| Dynamic Resolver | `{{ url_for('static', filename='...') }} | Adapts to custom subpaths, CDN prefixes, and cache queries | Slightly more verbose syntax |
| Direct Root Path | `href="/static/css/base.css" | Compact syntax, standard across front-end toolchains | Requires root-domain hosting |
| Cache-Busted URL | `url_for('static', filename='...', v='1.2') | Forces immediate browser cache refresh on CSS updates | Requires manual or automated version updates |

#### 📍 Where to Find in Codebase
- File: [template/base.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/base.html#L14-L25)

</details>

---

<details>
<summary><h3>11. Dynamic URL Generation with url_for() & External URLs (navbar.html & service.html)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Hardcoding URL paths (e.g. `&lt;a href="/service"&gt;) makes applications brittle and prone to broken links when routes change. Flask's `url_for() provides robust reverse routing: you pass the name of the view function, and Flask dynamically computes the corresponding canonical URL.

> **How Flask Works Under the Hood:** `url_for(endpoint, **values) inspects `app.url_map to find the rule matching the requested endpoint name. If the view belongs to a Blueprint, the endpoint must include the blueprint prefix (e.g. `auth.login, `api.get_services). If a view function within the same blueprint is calling `url_for(), a relative shortcut with a leading dot can be used (e.g. `url_for('.login')). Any keyword arguments that do not correspond to variable path converters are automatically converted and appended as URL-encoded query parameters. Passing `_external=True generates a full, absolute URL including scheme and domain (e.g. `https://flaskcraft.com/reset), which is essential for emails, webhooks, and third-party OAuth callbacks.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Endpoint Resolution:** Flask matches endpoint string (e.g. `'auth.login') against `app.url_map.
2. **Path Variable Substitution:** Keyword arguments matching route parameters (e.g. `id=42) are substituted into the URL path.
3. **Query Parameter Serialization:** Unmatched keyword arguments are converted into a URL query string (`?promo=FLASK20).
4. **Scheme & Host Formatting:** If `_external=True is passed, appends HTTP/HTTPS scheme and server domain name.
5. **Anchor Fragment Appending:** If `_anchor='...' is provided, appends hash fragment (`#section) to the URL.

#### 💻 Production-Grade Code Implementation (template/components/navbar.html & service.html)
```html
<!-- 1. Basic Application Routes -->
<a href="{{ url_for('home') }}">Home</a>
<a href="{{ url_for('about') }}">About Us</a>

<!-- 2. Blueprint Namespaced Routes -->
<a href="{{ url_for('auth.login') }}">Account Login</a>
<a href="{{ url_for('flash_demo.flash_page') }}">Flash Playground</a>

<!-- 3. Dynamic Route with Query Parameters -->
<a href="{{ url_for('service', tier='pro', promo='FLASK20') }}">
    View Pro Tier (20% Off)
</a>
<!-- Outputs: /service?tier=pro&promo=FLASK20 -->

<!-- 4. Absolute External URLs for Emails / Webhooks (in Python) -->
# reset_url = url_for('auth.reset_password', token=token, _external=True)
# Generates: http://127.0.0.1:5000/reset-password?token=xyz
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Missing Blueprint Prefix:** Writing `url_for('login') instead of `url_for('auth.login') raises a `BuildError: Could not build url for endpoint 'login'.

**Passing Function Objects:** Passing the Python function reference itself (e.g. `url_for(home)) instead of a string (`url_for('home')) causes runtime errors in Jinja.

#### 📊 Technical Reference & Attributes Matrix
| Argument | Type | Function | Example Output |
| --- | --- | --- | --- |
| `endpoint | str | Target view function or blueprint.endpoint name | `'service' |
| `_external | bool | If True, generates absolute canonical URL with protocol and host | `http://127.0.0.1:5000/service |
| `_scheme | str | Specifies URL scheme (e.g. 'https') when _external=True | `https://... |
| `_anchor | str | Appends hash fragment identifier to the URL | `/study#topic-urlfor |
| `**values | kwargs | Extra keyword arguments serialized as query parameters | `?tier=pro&promo=FLASK20 |

#### 📍 Where to Find in Codebase
- File: [template/components/navbar.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/template/components/navbar.html#L10-L40)

</details>

---

<details>
<summary><h3>12. Modular Architecture with Flask Blueprints (api.py, auth.py & flash_demo.py)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
A Flask Blueprint is a design pattern for structuring large web applications into modular, cohesive components. Blueprints encapsulate routes, view logic, error handlers, static assets, and templates into separate Python modules that register cleanly onto the main application instance.

> **How Flask Works Under the Hood:** A Blueprint is not a standalone WSGI application; rather, it is a record of operations to be registered onto a `Flask instance. When `app.register_blueprint(api_bp) is called in `main.py, Flask replays the blueprint's recorded routes and hooks, prefixing endpoints with the blueprint name and prepending the configured `url_prefix (e.g. `/api or `/auth). Blueprints can also register their own independent lifecycle hooks (such as `@bp.before_request and `@bp.errorhandler) that apply exclusively to routes within that blueprint namespace.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Blueprint Instantiation:** Instantiate `Blueprint('name', __name__, url_prefix='/...') in a dedicated file.
2. **Route & Hook Definition:** Attach routes using `@bp.route() and middleware using `@bp.before_request.
3. **Exporting Blueprint:** Expose the blueprint instance for consumption by the main application.
4. **Application Registration:** Import and register in `main.py via `app.register_blueprint(bp).
5. **Namespaced Request Dispatching:** Flask dispatches matching incoming requests to blueprint handlers based on URL prefixes.

#### 💻 Production-Grade Code Implementation (api.py & main.py (Blueprint Setup))
```python
# In api.py (Modular API Module)
from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/services")
def list_services():
    return jsonify({"success": True, "count": 3, "data": [...]})

# -------------------------------------------------------------
# In main.py (Central Application Orchestrator)
from flask import Flask
from api import api_bp
from auth import auth_bp
from flash_demo import flash_bp

app = Flask(__name__, template_folder="template")
app.secret_key = "flaskcraft-dev-secret-key-2026"

# Register modular blueprints with the central application
app.register_blueprint(api_bp)                  # Exposes /api/*
app.register_blueprint(auth_bp)                 # Exposes /login, /logout, /dashboard
app.register_blueprint(flash_bp)                # Exposes /flash-demo
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Circular Import Deadlocks:** Importing `app inside a blueprint module while `main.py imports the blueprint causes Python circular import errors. Always instantiate `Blueprint independently without importing `app.

**Missing URL Prefix:** Forgetting `url_prefix="/api" registers API routes directly on the root path, risking collisions with frontend routes.

#### 📊 Technical Reference & Attributes Matrix
| Blueprint Name | File | URL Prefix | Responsibility |
| --- | --- | --- | --- |
| `api_bp | `api.py | `/api | REST API endpoints, JSON responses, status code validation |
| `auth_bp | `auth.py | `None (Root) | Login, logout, session persistence, protected dashboard route |
| `flash_bp | `flash_demo.py | `None (Root) | Flash message interactive playground and toast trigger demos |

#### 📍 Where to Find in Codebase
- File: [api.py & auth.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/api.py#L12-L15)

</details>

---

<details>
<summary><h3>13. REST APIs & JSON Responses with jsonify (api.py)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Flask's `jsonify() serializes Python data structures (dictionaries, lists, primitives) into JSON-formatted HTTP responses. It configures the response MIME type as `application/json and pairs seamlessly with semantic HTTP status code tuples.

> **How Flask Works Under the Hood:** Calling `json.dumps() produces a raw Python string that Flask serves with `Content-Type: text/html; charset=utf-8. In contrast, `jsonify() wraps data in a genuine `Response object with `Content-Type: application/json. To process incoming JSON bodies from clients, use `request.get_json(silent=True): setting `silent=True prevents Flask from raising an unhandled 400 Bad Request if the body is empty or malformed, enabling you to return customized, descriptive JSON error objects.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Request Payload Inspection:** Check incoming request headers and parse JSON body with `request.get_json().
2. **Input Validation:** Validate data types, required fields, and business constraints.
3. **Data Processing:** Perform database querying, record creation, or calculations.
4. **JSON Serialization:** Package output into Python dictionary and pass to `jsonify().
5. **Status Code Assignment:** Return a response tuple pairing JSON data with an appropriate HTTP status code (200, 201, 400, 404).

#### 💻 Production-Grade Code Implementation (api.py (REST Endpoints & Validation))
```python
from flask import Blueprint, jsonify, request
from datetime import datetime, timezone

api_bp = Blueprint("api", __name__, url_prefix="/api")

# 1. GET Request returning JSON with status code 200
@api_bp.route("/services", methods=["GET"])
def get_services():
    tier = request.args.get("tier")
    services = [...] # query database
    return jsonify({
        "success": True,
        "count": len(services),
        "data": services,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

# 2. POST Request parsing JSON body with status code 201 & 400 validation
@api_bp.route("/inquiries", methods=["POST"])
def submit_inquiry():
    data = request.get_json(silent=True)
    if not data or "name" not in data or "email" not in data:
        return jsonify({
            "success": False,
            "error": "Validation failed: 'name' and 'email' are required JSON fields."
        }), 400

    return jsonify({
        "success": True,
        "message": "Inquiry created successfully.",
        "record": data
    }), 201
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Omitting Status Code:** Forgetting the status code tuple in error responses (e.g. `return jsonify({'error': 'Not found'})) sends the error payload with an HTTP 200 OK status code.

**Using json.dumps():** Returning `json.dumps(data) sends `Content-Type: text/html, which can break frontend API clients expecting JSON headers.

#### 📊 Technical Reference & Attributes Matrix
| Status Code | Name | When to Return in APIs | Example Scenario |
| --- | --- | --- | --- |
| `200 OK | Success | Resource successfully retrieved or updated | GET /api/services |
| `201 Created | Created | New resource successfully created | POST /api/inquiries |
| `204 No Content | No Content | Action succeeded; no response body returned | DELETE /api/items/5 |
| `400 Bad Request | Client Error | Invalid JSON syntax or missing required fields | POST with missing 'email' |
| `404 Not Found | Not Found | Requested resource identifier does not exist | GET /api/services/unknown |

#### 📍 Where to Find in Codebase
- File: [api.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/api.py#L70-L180)

</details>

---

<details>
<summary><h3>14. Flask Flash Messages, Login & Logout Flow, and Floating Toasts (auth.py & toast.html)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Flash messaging provides a temporary notification channel across HTTP redirects. Integrated with authentication flows (Login, Logout, protected routes), messages are stored in encrypted session cookies and consumed once on the subsequent page load via floating Toast notifications.

> **How Flask Works Under the Hood:** Flash messages are queued in the user session cookie under `session['_flashes'] as a list of `(category, message) tuples. Calling `get_flashed_messages(with_categories=True) in Jinja consumes the queue, popping the messages and updating the session cookie. Unconsumed messages persist across redirects (such as PRG flows). Rather than displaying static inline banners that shift page content, modern UI architectures render messages in a floating Toast container pinned to the top-right of the viewport. A JavaScript controller tracks each toast, displays an SVG category icon, and automatically triggers smooth fade-out and slide-up dismissal after 4 seconds (with manual click-to-dismiss option).

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Authentication Check:** User submits credentials via POST; server verifies against secure store.
2. **Session & Flash Assignment:** On success, store identity in `session['user'] and queue notification with `flash('Welcome back!', 'success').
3. **HTTP 302 PRG Redirect:** Server issues redirect to destination route (e.g. `url_for('home')).
4. **Flash Queue Consumption:** Jinja invokes `get_flashed_messages(), popping messages from session cookie.
5. **Floating Toast Display & Auto-Dismiss:** Toasts render in floating viewport container; JavaScript fades them out after 4 seconds.

#### 💻 Production-Grade Code Implementation (auth.py & template/components/toast.html)
```python
# In auth.py (Authentication Controller)
@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if verify_user(username, password):
        session["user"] = username
        flash(f"Welcome back, {username}! You have successfully logged in.", "success")
        return redirect(url_for("home"))

    flash("Invalid username or password. Please try again.", "danger")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been safely logged out.", "info")
    return redirect(url_for("auth.login"))

# -------------------------------------------------------------
<!-- In template/components/toast.html (Floating Toast Container) -->
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
    <div class="toast-container" id="toast-container">
        {% for category, message in messages %}
        <div class="toast-card toast-{{ category }}" role="alert">
            <span class="toast-icon">✓</span>
            <div class="toast-content">{{ message }}</div>
            <button type="button" class="toast-close" onclick="this.parentElement.remove()">×</button>
        </div>
        {% endfor %}
    </div>
    {% endif %}
{% endwith %}
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Missing Secret Key:** Forgetting `app.secret_key causes `flash() to crash with a `RuntimeError.

**Multiple Flash Pops:** Calling `get_flashed_messages() multiple times in different templates or partials drains the queue on the first call, leaving subsequent calls empty.

#### 📊 Technical Reference & Attributes Matrix
| Toast Category | UI Color Token | Icon | Semantic Purpose |
| --- | --- | --- | --- |
| `success | Emerald (`--accent-emerald) | ✓ Checkmark | Successful login, form submissions, record creation |
| `danger | Rose (`--accent-rose) | ✕ Warning cross | Authentication errors, validation failures, deletions |
| `warning | Amber (`--accent-amber) | ⚠ Exclamation mark | Session timeouts, missing permissions, alerts |
| `info | Cyan (`--accent-cyan) | ℹ Info badge | Logout confirmations, system notifications, status updates |

#### 📍 Where to Find in Codebase
- File: [auth.py & template/components/toast.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/auth.py#L23-L101)

</details>

---

<details>
<summary><h3>15. Custom Error Handling & HTTP Status Code Pages (@app.errorhandler) (main.py & 404.html)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Production web applications should handle HTTP errors (404 Not Found, 500 Internal Server Error, 403 Forbidden) gracefully rather than exposing raw browser defaults or server stack traces. Using `@app.errorhandler() allows rendering branded error pages and delivering structured JSON error responses for API clients.

> **How Flask Works Under the Hood:** When an unhandled exception occurs or a route invokes `abort(404), Werkzeug raises a subclass of `HTTPException. Flask intercepts the exception and checks for a matching handler registered via `@app.errorhandler(404). If the client requested an API endpoint (verified via `request.path.startswith('/api/') or checking the `Accept header), the handler returns a JSON error payload. Crucially, when returning a custom error template, developers must return an explicit status code tuple (e.g. `return render_template('404.html'), 404). If omitted, Flask defaults to an HTTP 200 OK status code, which impairs SEO crawling and client error handling.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Error Inception:** A non-existent path is requested or `abort(404) is invoked.
2. **Exception Interception:** Flask halts normal processing and searches `app.error_handler_spec for a matching handler.
3. **Content Negotiation:** The handler inspects `request.path or `Accept headers to distinguish API requests from browser visits.
4. **Custom Response Rendering:** Renders `404.html for web browsers or generates a JSON error object for API clients.
5. **Explicit Status Code Tuple Delivery:** Returns the response paired with the integer error status code (404 or 500).

#### 💻 Production-Grade Code Implementation (main.py & template/404.html)
```python
from flask import render_template, request

# 1. Custom 404 Not Found Handler with API Content Negotiation
@app.errorhandler(404)
def page_not_found(error):
    # API endpoints receive structured JSON error payloads
    if request.path.startswith("/api/"):
        return {"success": False, "error": "Endpoint not found", "code": 404}, 404

    # Web pages receive customized glassmorphic error page
    # Note: The second element in the return tuple (404) is mandatory!
    return render_template("404.html", error=error), 404

# 2. Custom 500 Internal Server Error Handler
@app.errorhandler(500)
def internal_server_error(error):
    if request.path.startswith("/api/"):
        return {"success": False, "error": "Internal server error", "code": 500}, 500

    return render_template(
        "404.html",
        error=error,
        error_code=500,
        error_title="Internal Server Error"
    ), 500
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Omitting the Status Code Tuple:** Writing `return render_template('404.html') without `, 404 causes Flask to return an HTTP 200 OK status code, misleading search engines into indexing error pages.

**Failing to Handle 500 Errors:** Unhandled exceptions in production can leak internal variable names, file paths, and database details in the default traceback.

#### 📊 Technical Reference & Attributes Matrix
| Error Code | Exception Class | Trigger Condition | Standard Response |
| --- | --- | --- | --- |
| `400 | `BadRequest | Missing required form fields, invalid JSON payload | Custom 400 error message |
| `401 | `Unauthorized | User unauthenticated for protected route | Redirect to /login with flash toast |
| `403 | `Forbidden | User authenticated but lacks permission | 403 Access Denied template |
| `404 | `NotFound | Requested URL path does not exist on server | Custom 404.html template |
| `405 | `MethodNotAllowed | POST sent to GET-only route | HTTP 405 Method Not Allowed header |
| `500 | `InternalServerError | Unhandled Python exception or database failure | Custom 500.html template |

#### 📍 Where to Find in Codebase
- File: [main.py & template/404.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/main.py)

</details>

---

<details>
<summary><h3>16. Application & Request Context Lifecycle (current_app, g & Proxies) (main.py & auth.py)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Flask uses context locals to handle concurrent requests in multi-threaded environments without requiring you to pass `request or `app arguments to every function. It manages two context tiers: the <strong>Application Context</strong> (exposing `current_app and `g) and the <strong>Request Context</strong> (exposing `request and `session).

> **How Flask Works Under the Hood:** Behind the scenes, Flask manages context isolation using Python's `contextvars (or Werkzeug's `LocalStack). When an incoming HTTP request arrives at the WSGI entry point, Flask pushes both an application context and a request context onto thread-local storage. The variables `request, `session, `current_app, and `g are actually instances of `werkzeug.local.LocalProxy: whenever you access an attribute (such as `request.method), the proxy forwards the lookup to the active context of the current thread or async task. The `flask.g object provides a per-request namespace for temporary data (such as database connections or user identity) that is automatically torn down when the request finishes.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Request Arrival:** WSGI server receives request and creates `RequestContext and `AppContext.
2. **Context Push:** Flask pushes both contexts; `LocalProxy instances bind to current thread/task.
3. **Pre-Request Hooks Execution:** Functions decorated with `@app.before_request execute, often attaching data to `g.
4. **View Function Execution:** View logic accesses `request and `g directly without explicit parameter passing.
5. **Teardown & Cleanup:** `@app.teardown_appcontext executes to close database handles; contexts are popped and destroyed.

#### 💻 Production-Grade Code Implementation (Application Lifecycle Example)
```python
from flask import Flask, g, request, current_app, render_template
import time

app = Flask(__name__, template_folder="template")

# 1. Store request-scoped data in g during before_request hook
@app.before_request
def start_request_timer():
    g.start_time = time.time()
    # Cache user identity or database connection on g:
    g.client_ip = request.remote_addr

# 2. Access g and current_app inside view functions
@app.route("/status")
def server_status():
    duration = time.time() - g.start_time
    app_name = current_app.name
    return {
        "app": app_name,
        "client_ip": g.client_ip,
        "processing_time_ms": round(duration * 1000, 2)
    }

# 3. Teardown hook executes when request completes (guaranteed execution)
@app.teardown_appcontext
def cleanup_resources(exception=None):
    db = g.pop("db_connection", None)
    if db is not None:
        db.close()
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Working Outside Context Error:** Accessing `request or `current_app inside background threads, Celery tasks, or standalone scripts raises `RuntimeError: Working outside of request context. Use `with app.app_context(): to push contexts manually.

**Confusing g with session:** Data stored on `g is destroyed as soon as the current request ends; use `session for data that must persist across subsequent requests.

#### 📊 Technical Reference & Attributes Matrix
| Context | Exposed Proxies | Lifetime | Primary Responsibility |
| --- | --- | --- | --- |
| `Application Context | `current_app, `g | Duration of request or CLI command | Global app config, database connections, logger |
| `Request Context | `request, `session | Single HTTP request transaction | HTTP headers, query args, cookies, form data |

#### 📍 Where to Find in Codebase
- File: [main.py & auth.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/main.py)

</details>

---

<details>
<summary><h3>17. Custom Response Objects, Headers & Cookie Management (make_response) (main.py & api.py)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
While Flask view functions can return simple strings, templates, or dictionaries, creating explicit `Response objects via `make_response() allows fine-grained control over HTTP status codes, custom security headers, MIME types, and browser cookies.

> **How Flask Works Under the Hood:** Flask view functions can return three formats: a string (converted to 200 OK), a tuple (`body, status, headers), or a `Response object. Calling `make_response(render_template(...)) gives you direct access to the underlying Werkzeug `Response instance. This allows setting cookies via `response.set_cookie() with essential security flags: `httponly=True (prevents client JavaScript from reading the cookie, mitigating XSS theft), `samesite='Lax' (mitigates CSRF vulnerabilities), and `secure=True (ensures cookies are transmitted only over encrypted HTTPS). You can also configure security headers like `X-Content-Type-Options: nosniff and HTTP caching policies.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Template or Data Generation:** Render HTML template or serialize JSON data.
2. **Response Wrapping via make_response:** Wrap output into a `Response instance.
3. **Cookie Setting with Security Flags:** Call `response.set_cookie() with `httponly=True and `samesite='Lax'.
4. **Custom Header Attachment:** Attach security, CORS, or caching headers to `response.headers.
5. **Response Dispatch:** Return completed response object to WSGI server.

#### 💻 Production-Grade Code Implementation (Custom Response & Cookie Management)
```python
from flask import make_response, render_template, request

@app.route("/set-theme/<theme_name>")
def set_theme(theme_name):
    # 1. Create explicit Response object from rendered template
    response = make_response(render_template("home.html"))

    # 2. Set persistent client cookie with security flags
    response.set_cookie(
        key="site_theme",
        value=theme_name,
        max_age=60 * 60 * 24 * 30,  # 30 days expiration
        httponly=True,              # Mitigates XSS cookie theft
        samesite="Lax",             # Mitigates CSRF vulnerabilities
        secure=False                # Set to True on production HTTPS
    )

    # 3. Add custom HTTP security & caching headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

    return response

@app.route("/clear-theme")
def clear_theme():
    response = make_response(render_template("home.html"))
    response.delete_cookie("site_theme")
    return response
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Missing HttpOnly Flag:** Setting sensitive cookies without `httponly=True allows any malicious JavaScript executed via an XSS flaw to read `document.cookie.

**Setting Cookies on Strings:** Calling `set_cookie() on the return value of `render_template() raises an `AttributeError because strings lack cookie methods. Always wrap in `make_response().

#### 📊 Technical Reference & Attributes Matrix
| Cookie Parameter | Type | Security Impact | Recommended Value |
| --- | --- | --- | --- |
| `httponly | bool | Blocks client-side JavaScript access via `document.cookie | `True (mandatory for auth) |
| `samesite | str | Prevents browser from sending cookie on cross-site requests | `'Lax' or `'Strict' |
| `secure | bool | Restricts cookie transmission strictly to HTTPS connections | `True in production |
| `max_age | int | Cookie lifespan in seconds | e.g. `2592000 (30 days) |
| `path | str | Limits cookie availability to specific URL subdirectories | `'/' (entire site) |

#### 📍 Where to Find in Codebase
- File: [main.py & api.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/main.py)

</details>

---

<details>
<summary><h3>18. Jinja2 Filters, Custom Template Filters & Safe Escaping (main.py & study.html)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Jinja2 filters transform and format variable outputs inside templates using the pipe operator (`|). Flask enables automatic HTML entity escaping by default on templates to defend against Cross-Site Scripting (XSS). Custom Python functions can be registered as template filters using `@app.template_filter().

> **How Flask Works Under the Hood:** When Jinja processes an expression like `{{ value | filter_name }}, it passes the value as the first argument to the filter function. Multiple filters can be chained sequentially: `{{ title | striptags | title }}. Jinja's automatic escaping converts characters like `&lt;, `&gt;, `&amp;, and `&quot; into HTML entities. The `| safe filter marks a string as safe HTML, disabling auto-escaping. If untrusted user inputs are passed into `| safe, attackers can inject arbitrary `&lt;script&gt; tags. When passing Python objects into JavaScript inside templates, always use the `| tojson filter to ensure valid, safe JSON serialization.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Filter Function Registration:** Define a Python function and decorate it with `@app.template_filter('name') in `main.py.
2. **Template Application:** Apply the filter in Jinja using pipe syntax: `{{ price | currency }}.
3. **Chaining Multiple Filters:** Chain transformations from left to right: `{{ text | default('N/A') | upper }}.
4. **Safe Escaping Verification:** Ensure user-supplied variables are auto-escaped; avoid `| safe on unsanitized input.
5. **Client Serialization:** Use `| tojson when embedding Python data into client-side JavaScript.

#### 💻 Production-Grade Code Implementation (main.py (Filter Registration) & Template Usage)
```python
# In main.py: Registering custom template filter
@app.template_filter("currency")
def currency_filter(value):
    """Formats a numeric price into a localized USD currency string."""
    if value is None:
        return "Custom Quote"
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)

# -------------------------------------------------------------
<!-- In Jinja Template: Usage Examples -->
<!-- 1. Custom Currency Filter -->
<p>Starter Plan: {{ 499 | currency }}</p>
<!-- Renders: $499.00 -->

<!-- 2. Built-in Fallback Default Filter -->
<p>User Bio: {{ user_bio | default('No bio provided yet.', boolean=True) }}</p>

<!-- 3. Safe Embedding of Python Data into JavaScript -->
<script>
    const teamMembers = {{ team | tojson }};
    console.log("Loaded team members:", teamMembers);
</script>

<!-- 4. HTML Stripping -->
<p>Preview: {{ raw_html_content | striptags | truncate(100) }}</p>
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**XSS via | safe Filter:** Applying `{{ user_comment | safe }} on unescaped user input allows malicious users to inject `&lt;script&gt; tags and steal session cookies.

**Missing boolean=True in default:** By default, `| default('fallback') only activates on `Undefined variables, not empty strings (`""). Use `| default('fallback', boolean=True) to catch both.

#### 📊 Technical Reference & Attributes Matrix
| Filter | Syntax | Operation | Example |
| --- | --- | --- | --- |
| `currency (custom) | `{{ 1299 | currency }} | Formats number into USD currency string | `$1,299.00 |
| `default | `{{ val | default('N/A', boolean=True) }} | Provides fallback if variable is None or empty | `N/A |
| `tojson | `{{ py_data | tojson }} | Safely converts Python data into valid JavaScript JSON | `[{"id": 1}] |
| `striptags | `{{ html | striptags }} | Strips all SGML/HTML tags from string | `Plain text |
| `length | `{{ list | length }} | Returns element count of list, dict, or string | `4 |
| `round | `{{ 3.14159 | round(2) }} | Rounds float to specified decimal places | `3.14 |

#### 📍 Where to Find in Codebase
- File: [main.py & template/study.html](https://github.com/Shrikant92Bhatt/python-flask/blob/main/main.py)

</details>

---

<details>
<summary><h3>19. Session Security, Cryptographic Signing & CSRF Protection (main.py & auth.py)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Unlike frameworks that store session data in server-side databases by default, Flask uses <strong>client-side cryptographically signed cookies</strong> powered by `itsdangerous. Understanding session structure, key entropy, and Cross-Site Request Forgery (CSRF) mitigation is critical for application security.

> **How Flask Works Under the Hood:** A Flask session cookie consists of three base64-encoded segments separated by dots: `Payload.Timestamp.Signature. The Payload contains serialized JSON session state; it is base64-encoded, *not encrypted*, meaning clients can read its contents. The Timestamp tracks issuance for expiration checks. The Signature is a cryptographic HMAC-SHA256 hash computed with `app.secret_key. If a client tampers with the cookie (e.g. altering `user: guest to `user: admin), the server's recomputed HMAC will not match, and Flask will automatically discard the session. Cross-Site Request Forgery (CSRF) occurs when unauthorized external websites trick a user's browser into submitting malicious POST requests; setting `SESSION_COOKIE_SAMESITE = 'Lax' and validating CSRF tokens mitigates this threat.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Session State Mutation:** View sets data: `session['user'] = 'shrikant'.
2. **JSON Serialization:** Flask serializes session dictionary into a JSON string payload.
3. **Cryptographic HMAC Signing:** `itsdangerous computes an HMAC-SHA256 signature using `app.secret_key.
4. **Cookie Dispatch:** Browser receives signed cookie in the HTTP `Set-Cookie header.
5. **Tamper Verification on Inbound Request:** On subsequent requests, Flask recalculates the HMAC; invalid signatures reset the session.

#### 💻 Production-Grade Code Implementation (main.py & Session Security Configuration)
```python
import os
import secrets
from datetime import timedelta
from flask import Flask, session

app = Flask(__name__, template_folder="template")

# 1. Cryptographically Secure Secret Key Generation
# Generate via: python -c "import secrets; print(secrets.token_hex(32))"
app.secret_key = os.environ.get("SECRET_KEY", "flaskcraft-dev-secret-key-2026")

# 2. Strict Session Cookie Hardening Configuration
app.config.update(
    # Mitigates XSS cookie exfiltration
    SESSION_COOKIE_HTTPONLY=True,
    # Restricts cookie transmission strictly to HTTPS in production
    SESSION_COOKIE_SECURE=False, # Set to True in production HTTPS
    # Mitigates Cross-Site Request Forgery (CSRF) attacks
    SESSION_COOKIE_SAMESITE="Lax",
    # Controls session cookie lifespan (e.g. 7 days)
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)
)

@app.before_request
def make_session_permanent():
    # Enforces lifetime expiration across browser restarts
    session.permanent = True
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Storing Sensitive Data in Session:** Flask session cookies are signed, NOT encrypted! Anyone who inspects their browser cookies can decode the base64 payload. Never store passwords, API secrets, or credit card numbers in `session.

**Predictable Secret Keys:** Using predictable keys like `app.secret_key = 'secret' allows attackers to compute valid signatures and forge arbitrary session identities.

#### 📊 Technical Reference & Attributes Matrix
| Config Option | Type | Security Purpose | Production Value |
| --- | --- | --- | --- |
| `SECRET_KEY | str / bytes | Cryptographic seed for HMAC-SHA256 signature calculation | Random 64-char hex string |
| `SESSION_COOKIE_HTTPONLY | bool | Blocks JavaScript access to session cookie | `True |
| `SESSION_COOKIE_SECURE | bool | Restricts cookie transmission strictly to HTTPS | `True |
| `SESSION_COOKIE_SAMESITE | str | Defends against Cross-Site Request Forgery (CSRF) | `'Lax' |
| `PERMANENT_SESSION_LIFETIME | timedelta | Controls session expiration interval | `timedelta(days=7) |

#### 📍 Where to Find in Codebase
- File: [main.py & auth.py](https://github.com/Shrikant92Bhatt/python-flask/blob/main/auth.py#L46-L56)

</details>

---

<details>
<summary><h3>20. Modular CSS Architecture & Scalable Frontend Design in Flask (static/css/ & base.html)</h3></summary>

#### 🧠 Architectural Concept & Under-the-Hood Mechanics
Monolithic stylesheets lead to specificity collisions, bloated payloads, and maintenance issues. FlaskCraft implements a two-tier modular CSS architecture: global design tokens and primitives in `base.css paired with page-specific modules (`home.css, `service.css, `study.css, etc.) injected on demand via Jinja's `{% block extra_css %}, with strict adherence to zero inline CSS.

> **How Flask Works Under the Hood:** The modular architecture separates styles into two layers: <strong>Tier 1 - Global Design System (`base.css)</strong> defines CSS custom properties (colors, typography, shadows, border radii), global resets, and shared primitives (`.btn, `.form-control, `.glass-card, `.toast-card). <strong>Tier 2 - Page-Specific Feature Stylesheets</strong> (`about.css, `contact.css, `service.css, `study.css) contain only the layout rules and components unique to that template. Child templates inject their respective stylesheet in the document head using `{% block extra_css %}. Eliminating inline `style="..." attributes supports Content Security Policy (CSP) compliance, improves browser caching, and keeps presentation logic cleanly decoupled from HTML structure.

#### ⚙️ Step-by-Step Execution Lifecycle
1. **Global Design Tokens Initialization:** Define color palettes, typography, spacing, and glassmorphic variables in `static/css/base.css.
2. **Component Primitives Isolation:** Build reusable UI primitives (buttons, inputs, cards) once in `base.css.
3. **Feature Stylesheet Splitting:** Extract page-specific styles into separate files (`about.css, `service.css, `study.css).
4. **Template Head Injection:** Child templates inject their stylesheet using `{% block extra_css %} in `&lt;head&gt;.
5. **Strict Zero-Inline-CSS Enforcement:** Ensure all styles are driven by semantic CSS classes and IDs, keeping HTML markup completely clean.

#### 💻 Production-Grade Code Implementation (Modular CSS Architecture Breakdown)
```css
/* Directory Structure:
static/css/
  ├── base.css       <- Global tokens, CSS reset, navbar, footer, buttons, toasts
  ├── home.css       <- Hero showcase, feature grid, CTAs
  ├── about.css      <- Team cards, timeline, milestone badges
  ├── service.css    <- Pricing matrix, query promo voucher controls
  ├── contact.css    <- Glassmorphic contact form, copy email button
  ├── auth.css       <- Login card, demo credentials panel
  ├── flash.css      <- Floating toast animations & notification categories
  ├── study.css      <- Accordion components, search filtering, code blocks
  └── style.css      <- Master production bundle importing all modules

<!-- Child Template Injection via Jinja Block: -->
{% extends "base.html" %}

{% block extra_css %}
<!-- Only loads study.css on the study guide page, avoiding stylesheet bloat -->
<link rel="stylesheet" href="/static/css/study.css">
{% endblock %}
```

#### ⚠️ Common Pitfalls, Gotchas & Security Traps
**Using Inline Styles:** Adding `style="color: red;" directly on HTML tags violates Content Security Policy (CSP), bypasses browser caching, and complicates maintenance.

**Global Utility Class Overrides:** Overriding global utility classes (like `.btn or `.form-control) inside page-specific stylesheets introduces side effects on other pages. Always use scoped selector prefixes.

#### 📊 Technical Reference & Attributes Matrix
| Stylesheet Module | File Path | Scope & Contents | Included Via |
| --- | --- | --- | --- |
| `base.css | `static/css/base.css | Global CSS variables, reset, layout grid, buttons, toasts | `base.html (site-wide) |
| `study.css | `static/css/study.css | Interactive accordions, search filter bar, callout boxes | `{% block extra_css %} in `study.html |
| `service.css | `static/css/service.css | Pricing cards, promo code input, tier filter buttons | `{% block extra_css %} in `service.html |
| `contact.css | `static/css/contact.css | Glassmorphic contact form, copy email button states | `{% block extra_css %} in `contact.html |
| `auth.css | `static/css/auth.css | Login authentication card, credential chips | `{% block extra_css %} in `login.html |

#### 📍 Where to Find in Codebase
- File: [template/base.html & static/css/](https://github.com/Shrikant92Bhatt/python-flask/blob/main/static/css/base.css)

</details>

---

