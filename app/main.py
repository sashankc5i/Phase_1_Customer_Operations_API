from uuid import uuid4
import asyncio

from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Query,
    Request,
    Form,
)

from fastapi.responses import JSONResponse

from .auth import authenticate, require_admin
from .models import (
    Customer,
    CustomerCreate,
    CustomerListResponse,
    CustomerUpdate,
)
from .rate_limit import RateLimiter
from .repository import CustomerRepository

from .integrations.crm import CRMClient
from .integrations.payment import PaymentClient
from .integrations.notification import NotificationClient

# ---------------------------------------------------------
# Application
# ---------------------------------------------------------

app = FastAPI(
    title="Customer Operations API",
    description="""
    Phase 1 REST API Engineering project.

    Demonstrates:
    - HTTP and REST resource design
    - Authentication and authorization
    - HTTP headers
    - Pagination
    - Error handling
    - Rate limiting
    - OpenAPI documentation
    """,
    version="1.0.0",
)


# ---------------------------------------------------------
# Application state
# ---------------------------------------------------------

repository = CustomerRepository(size=1_000_000)

rate_limiter = RateLimiter(
    max_requests=100,
    window_seconds=60,
)
crm_client = CRMClient(
    base_url="http://127.0.0.1:8000",
    client_id="phase2-client",
    client_secret="phase2-secret",
)

payment_client = PaymentClient(
    base_url="http://127.0.0.1:8000",
    api_key="phase2-payment-key",
)

notification_client = NotificationClient(
    base_url="http://127.0.0.1:8000",
    api_key="phase2-notification-key",
)


# ---------------------------------------------------------
# Request ID middleware
# ---------------------------------------------------------

@app.middleware("http")
async def add_request_id(
    request: Request,
    call_next
):
    request_id = request.headers.get(
        "X-Correlation-ID",
        str(uuid4())
    )

    response = await call_next(request)

    response.headers["X-Correlation-ID"] = request_id

    return response


# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

@app.get(
    "/health",
    tags=["Health"],
)
def health_check():
    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# GET single customer
# ---------------------------------------------------------

@app.get(
    "/customers/{customer_id}",
    response_model=Customer,
    tags=["Customers"],
)
def get_customer(
    customer_id: int,
    authorization: str | None = Header(default=None),
):
    role = authenticate(authorization)

    rate_limiter.check(role)

    customer = repository.get_by_id(customer_id)

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer


# ---------------------------------------------------------
# GET customers with pagination
# ---------------------------------------------------------

@app.get(
    "/customers",
    response_model=CustomerListResponse,
    tags=["Customers"],
)
def get_customers(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number starting from 1"
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of records per page. Maximum 100."
    ),
    authorization: str | None = Header(default=None),
):
    role = authenticate(authorization)

    rate_limiter.check(role)

    offset = (page - 1) * limit

    customers = repository.get_page(
        offset=offset,
        limit=limit
    )

    total = repository.count()

    return {
        "data": customers,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "has_next": offset + limit < total,
        }
    }


# ---------------------------------------------------------
# POST create customer
# ---------------------------------------------------------

@app.post(
    "/customers",
    response_model=Customer,
    status_code=201,
    tags=["Customers"],
)
def create_customer(
    customer_data: CustomerCreate,
    authorization: str | None = Header(default=None),
):
    role = authenticate(authorization)

    require_admin(role)

    rate_limiter.check(role)

    return repository.create(
        name=customer_data.name,
        email=str(customer_data.email),
    )


# ---------------------------------------------------------
# PATCH update customer
# ---------------------------------------------------------

@app.patch(
    "/customers/{customer_id}",
    response_model=Customer,
    tags=["Customers"],
)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    authorization: str | None = Header(default=None),
):
    role = authenticate(authorization)

    require_admin(role)

    rate_limiter.check(role)

    customer = repository.update(
        customer_id=customer_id,
        name=customer_data.name,
        email=(
            str(customer_data.email)
            if customer_data.email is not None
            else None
        ),
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer


# ---------------------------------------------------------
# DELETE customer
# ---------------------------------------------------------

@app.delete(
    "/customers/{customer_id}",
    status_code=204,
    tags=["Customers"],
)
def delete_customer(
    customer_id: int,
    authorization: str | None = Header(default=None),
):
    role = authenticate(authorization)

    require_admin(role)

    rate_limiter.check(role)

    deleted = repository.delete(customer_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return None


# ---------------------------------------------------------
# Global unexpected error handler
# ---------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    request_id = request.headers.get(
        "X-Correlation-ID"
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "request_id": request_id,
            }
        },
    )

from fastapi import Form
@app.post("/mock/oauth/token")
async def mock_oauth_token(
    client_id: str = Form(...),
    client_secret: str = Form(...),
):

    if (
        client_id != "phase2-client"
        or client_secret != "phase2-secret"
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid client credentials"
        )

    return {
        "access_token": "crm-demo-access-token",
        "token_type": "Bearer",
        "expires_in": 3600,
    }
@app.get(
    "/mock/crm/customers/{customer_id}"
)
async def mock_crm_customer(
    customer_id: int,
    authorization: str | None = Header(
        default=None
    ),
):

    if authorization != (
        "Bearer crm-demo-access-token"
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid CRM token"
        )

    return {
        "customer_id": customer_id,
        "crm_status": "active",
        "segment": "enterprise",
        "source": "CRM"
    }
@app.get(
    "/mock/payments/{customer_id}"
)
async def mock_payment_status(
    customer_id: int,
    x_api_key: str | None = Header(
        default=None
    ),
):

    if x_api_key != "phase2-payment-key":
        raise HTTPException(
            status_code=401,
            detail="Invalid payment API key"
        )

    return {
        "customer_id": customer_id,
        "payment_status": "paid",
        "source": "Payment Service"
    }
@app.post(
    "/mock/notifications"
)
async def mock_notification(
    payload: dict,
    x_api_key: str | None = Header(
        default=None
    ),
):

    if x_api_key != (
        "phase2-notification-key"
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid notification API key"
        )

    return {
        "status": "accepted",
        "customer_id": payload["customer_id"],
        "message": payload["message"],
    }
# ---------------------------------------------------------
# Enterprise profile integration
# ---------------------------------------------------------

@app.get(
    "/customers/{customer_id}/enterprise-profile"
)
async def get_enterprise_profile(
    customer_id: int,
    authorization: str | None = Header(default=None),
):
    role = authenticate(authorization)

    rate_limiter.check(role)

    customer = repository.get_by_id(customer_id)

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    crm_task = crm_client.get_customer_profile(
        customer_id
    )

    payment_task = payment_client.get_payment_status(
        customer_id
    )

    crm_data, payment_data = await asyncio.gather(
        crm_task,
        payment_task,
    )

    return {
        "customer": customer,
        "crm": crm_data,
        "payment": payment_data,
    }


# ---------------------------------------------------------
# Notification webhook
# ---------------------------------------------------------

@app.post(
    "/webhooks/notification"
)
async def notification_webhook(
    payload: dict,
    x_webhook_signature: str | None = Header(
        default=None
    ),
):

    if x_webhook_signature != "demo-signature":
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature"
        )

    event_id = payload.get("event_id")

    if not event_id:
        raise HTTPException(
            status_code=400,
            detail="event_id is required"
        )

    return {
        "status": "accepted",
        "event_id": event_id,
    }