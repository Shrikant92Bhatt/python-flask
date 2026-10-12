"""
=============================================================================
REST API Module for FlaskCraft
Demonstrating Flask's `jsonify`, HTTP methods (GET, POST), status codes,
request payload parsing (`request.get_json()`), and Blueprint modularity.
=============================================================================
"""

from datetime import datetime, timezone
from flask import Blueprint, jsonify, request

# Create a dedicated Flask Blueprint for all API endpoints
api_bp = Blueprint("api", __name__, url_prefix="/api")

# In-memory mock data stores
SERVICES_DB = [
    {
        "id": "starter",
        "name": "Starter Website",
        "price": 499,
        "currency": "USD",
        "tier": "starter",
        "features": [
            "Up to 5 static pages",
            "Responsive glassmorphic UI",
            "Working contact form",
            "Fast deployment setup",
        ],
        "active": True,
    },
    {
        "id": "pro",
        "name": "Full Application",
        "price": 1299,
        "currency": "USD",
        "tier": "pro",
        "features": [
            "Unlimited modular pages",
            "REST API endpoints",
            "Database integration (SQL)",
            "Admin & analytics panels",
            "Priority email support",
        ],
        "active": True,
    },
    {
        "id": "enterprise",
        "name": "Custom Enterprise",
        "price": None,
        "currency": "USD",
        "tier": "enterprise",
        "features": [
            "Microservice architecture",
            "Cloud infrastructure setup",
            "Custom security & authentication",
            "24/7 SLA maintenance",
        ],
        "active": True,
    },
]

PROMO_CODES = {
    "FLASK20": {"discount": 20, "description": "20% off all web packages"},
    "SUMMER50": {"discount": 50, "description": "50% off mid-year promotion"},
    "WELCOME10": {"discount": 10, "description": "10% new customer welcome discount"},
    "VIP100": {"discount": 100, "description": "100% complimentary VIP access"},
}

INQUIRIES_DB = []


# ---------------------------------------------------------------------------
# 1. API Health Check Endpoint
# ---------------------------------------------------------------------------
@api_bp.route("/health", methods=["GET"])
def health_check():
    """Returns the API operational status and metadata as JSON."""
    return (
        jsonify(
            {
                "status": "healthy",
                "service": "FlaskCraft REST API",
                "version": "1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "endpoints": [
                    "GET  /api/health",
                    "GET  /api/services",
                    "GET  /api/services/<id>",
                    "GET  /api/promo/validate?code=<promo>",
                    "GET  /api/team",
                    "POST /api/inquiries",
                ],
            }
        ),
        200,
    )


# ---------------------------------------------------------------------------
# 2. List Services with Optional Query Parameter Filtering
# ---------------------------------------------------------------------------
@api_bp.route("/services", methods=["GET"])
def get_services():
    """
    Returns services collection as JSON.
    Supports query parameter: /api/services?tier=pro
    """
    tier = request.args.get("tier")
    if tier and tier.lower() != "all":
        filtered = [s for s in SERVICES_DB if s["tier"] == tier.lower()]
    else:
        filtered = SERVICES_DB

    return (
        jsonify(
            {
                "success": True,
                "count": len(filtered),
                "filter_applied": tier if tier else "all",
                "data": filtered,
            }
        ),
        200,
    )


# ---------------------------------------------------------------------------
# 3. Retrieve a Single Service by ID (Path Parameter)
# ---------------------------------------------------------------------------
@api_bp.route("/services/<string:service_id>", methods=["GET"])
def get_service_by_id(service_id):
    """
    Returns details of a single service by ID.
    Demonstrates 404 error responses with JSON.
    """
    matched = next((s for s in SERVICES_DB if s["id"] == service_id.lower()), None)
    if not matched:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Not Found",
                    "message": f"Service with ID '{service_id}' does not exist.",
                    "available_ids": [s["id"] for s in SERVICES_DB],
                }
            ),
            404,
        )

    return (
        jsonify(
            {
                "success": True,
                "data": matched,
            }
        ),
        200,
    )


# ---------------------------------------------------------------------------
# 4. Promo Code Validation Endpoint (Query Parameters + JSON)
# ---------------------------------------------------------------------------
@api_bp.route("/promo/validate", methods=["GET"])
def validate_promo():
    """
    Validates a promotional code passed via query string:
    Example: /api/promo/validate?code=FLASK20
    """
    code = request.args.get("code", default="").strip().upper()

    if not code:
        return (
            jsonify(
                {
                    "success": False,
                    "valid": False,
                    "error": "Missing Parameter",
                    "message": "Query parameter 'code' is required. Example: /api/promo/validate?code=FLASK20",
                }
            ),
            400,
        )

    if code in PROMO_CODES:
        promo_info = PROMO_CODES[code]
        return (
            jsonify(
                {
                    "success": True,
                    "valid": True,
                    "code": code,
                    "discount_percent": promo_info["discount"],
                    "description": promo_info["description"],
                    "message": f"Promo code '{code}' is valid! {promo_info['discount']}% discount granted.",
                }
            ),
            200,
        )

    return (
        jsonify(
            {
                "success": True,
                "valid": False,
                "code": code,
                "discount_percent": 0,
                "message": f"Promo code '{code}' is invalid or expired.",
                "sample_valid_codes": list(PROMO_CODES.keys()),
            }
        ),
        200,
    )


# ---------------------------------------------------------------------------
# 5. Create Inquiry Endpoint (POST with JSON Body & Status 201)
# ---------------------------------------------------------------------------
@api_bp.route("/inquiries", methods=["POST"])
def create_inquiry():
    """
    Accepts JSON body:
    {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "subject": "Full-Stack Development",
        "message": "We need a Flask dashboard."
    }
    Demonstrates `request.get_json()` and 201 Created response.
    """
    data = request.get_json(silent=True)

    if not data or not isinstance(data, dict):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Bad Request",
                    "message": "Invalid JSON payload. Ensure Content-Type is 'application/json'.",
                }
            ),
            400,
        )

    # Validate required fields
    required_fields = ["name", "email", "message"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Unprocessable Entity",
                    "message": f"Missing required fields: {', '.join(missing)}",
                    "required_fields": required_fields,
                }
            ),
            422,
        )

    inquiry_record = {
        "id": len(INQUIRIES_DB) + 1,
        "name": data.get("name").strip(),
        "email": data.get("email").strip(),
        "subject": data.get("subject", "General Inquiry").strip(),
        "message": data.get("message").strip(),
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    INQUIRIES_DB.append(inquiry_record)

    return (
        jsonify(
            {
                "success": True,
                "message": "Inquiry successfully recorded via API.",
                "data": inquiry_record,
            }
        ),
        201,
    )


# ---------------------------------------------------------------------------
# 6. Team Endpoint (Data collection)
# ---------------------------------------------------------------------------
@api_bp.route("/team", methods=["GET"])
def get_team():
    """Returns team roster as JSON."""
    team = [
        {"name": "Alice Johnson", "role": "Lead Architect", "experience_years": 8},
        {"name": "Bob Smith", "role": "Frontend Specialist", "experience_years": 5},
        {"name": "Charlie Davis", "role": "DevOps Engineer", "experience_years": 3},
        {"name": "Diana Prince", "role": "UI/UX Designer", "experience_years": 2},
    ]
    return (
        jsonify(
            {
                "success": True,
                "total_members": len(team),
                "data": team,
            }
        ),
        200,
    )
