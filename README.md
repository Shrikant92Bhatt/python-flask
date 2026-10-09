# Python Flask

Repository for Python Flask projects and tutorials.

---

## Getting Started

### 1. Prerequisites
- Python 3.10+ installed

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 4. Run the Application

Using the Flask CLI:
```bash
flask --app main run
```

Or run in development mode (with auto-reload and debugger enabled):
```bash
flask --app main run --debug
```

---

### 5. Open in Browser
Once running, open your browser and navigate to:
[http://127.0.0.1:5000](http://127.0.0.1:5000)
