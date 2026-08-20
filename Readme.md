# Customer Operations API
### Phase 1 — REST API Engineering

## 1. The Problem I Was Trying to Solve

I approached this project as if I were building an API for a client that needs to expose customer information to a frontend application and potentially other downstream systems.

The requirement initially sounds simple:

> "Build an API that allows consumers to retrieve and manage customer information."

However, once I looked at the problem from an engineering perspective, several questions immediately appeared:

- How should the API resources be structured?
- How should clients authenticate?
- How should permissions be enforced?
- What happens when the customer dataset becomes very large?
- How should invalid requests and missing resources be communicated?
- What happens if a client sends too many requests?
- How can another development team understand the API without reading the backend source code?

I used these questions to drive the design instead of treating the API as a collection of endpoints.

The result is a FastAPI-based Customer Operations API demonstrating the fundamental principles of REST API engineering.

---

# 2. What I Built

The API exposes a customer resource through a REST-oriented interface.

The primary operations are:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/customers` | Retrieve customers with pagination |
| GET | `/customers/{customer_id}` | Retrieve one customer |
| POST | `/customers` | Create a customer |
| PATCH | `/customers/{customer_id}` | Partially update a customer |
| DELETE | `/customers/{customer_id}` | Delete a customer |
| GET | `/health` | Check service health |

The API also demonstrates:

- HTTP request/response handling
- REST resource design
- Bearer authentication
- Role-based authorization
- HTTP headers
- Pagination
- Request validation
- Error handling
- Rate limiting
- Correlation IDs
- OpenAPI documentation

---

# 3. Why I Chose a Resource-Oriented API

One of the first design decisions was how to structure the endpoints.

I could have created action-oriented endpoints such as:

```text
/getCustomer
/createCustomer
/updateCustomer
/deleteCustomer
I decided not to use that approach.

Instead, I modelled the business entity as a resource:

/customers
/customers/{customer_id}

and use HTTP methods to describe the operation.

For example:

GET    /customers/101
PATCH  /customers/101
DELETE /customers/101

For creation:

POST /customers

This gives the API a consistent resource model.

The URI identifies the resource, while the HTTP method communicates what I want to do with that resource.

I found this approach easier to reason about because consumers don't need to learn a different endpoint for every operation.

4. HTTP as the Communication Layer

HTTP provides the protocol used by the API.

The API uses standard HTTP concepts such as:

Methods
Status codes
Headers
Request bodies
Response bodies

For example:

GET /customers/101
Authorization: Bearer phase1-viewer
Accept: application/json

The important distinction I learned during the implementation is that HTTP and REST are not the same thing.

HTTP is the communication protocol.

REST is the architectural style used to structure the API around resources and standardized interactions.

5. Authentication and Authorization

Because customer information is not public, I treated authentication as part of the API design rather than something to add later.

I separated two concepts:

Authentication

Who is making the request?

Authorization

Is that user allowed to perform this operation?

The API expects a Bearer token through the Authorization header.

For this learning implementation I used two demonstration tokens:

Bearer phase1-viewer
Bearer phase1-admin

These represent:

phase1-viewer → viewer role
phase1-admin  → admin role

The implementation is intentionally simplified for demonstration.

It should NOT be interpreted as production-grade identity management.

In a production environment I would use an established identity provider and validate OAuth2/OIDC access tokens, including relevant claims such as:

issuer
audience
expiration
signature
scopes
roles
6. Authentication vs Authorization in the API

The API demonstrates the difference through destructive operations.

A viewer can retrieve customer information:

GET /customers/101
Authorization: Bearer phase1-viewer

This succeeds.

However:

DELETE /customers/101
Authorization: Bearer phase1-viewer

returns:

403 Forbidden

because the identity is valid but the user does not have sufficient permissions.

If authentication itself is missing or invalid:

401 Unauthorized

is returned.

This gives the API a clear distinction between:

401 → Authentication problem
403 → Authorization problem
7. HTTP Headers

I used headers to separate communication metadata from business data.

For example:

Authorization: Bearer phase1-viewer
Content-Type: application/json
Accept: application/json
X-Correlation-ID: abc123

The important distinction between Content-Type and Accept is:

Content-Type → What format am I sending?


Accept → What format do I want back?

For example:

Content-Type: application/json
Accept: application/json

means the request body is JSON and the client expects the response as JSON.

8. Correlation IDs

I also introduced an X-Correlation-ID response/request concept.

This is useful when troubleshooting APIs.

For example, a client might report:

"The request failed."

Instead of searching through millions of log entries, the client and support team can provide the correlation ID:

X-Correlation-ID: abc123

The engineering team can then use that identifier to trace the request through application logs and, in a distributed system, potentially through downstream services.

In a production environment I would also consider standardized distributed tracing mechanisms such as W3C Trace Context.

9. Designing for a Large Dataset

One of the most useful parts of this exercise was deliberately creating a large dataset.

I generated:

1,000,000 customers

in the in-memory repository.

I did this because I did not want pagination to remain a theoretical concept.

If the API simply returned:

GET /customers

and attempted to return all one million records, it could create unnecessary:

database load
application memory usage
network traffic
response latency
client processing
timeout risk

Therefore, I introduced bounded pagination.

10. Pagination

The API supports:

GET /customers?page=1&limit=20

The response contains both the data and pagination metadata:

{
  "data": [
    {
      "id": 1,
      "name": "Customer 1",
      "email": "customer1@example.com"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1000000,
    "has_next": true
  }
}

I also enforced a maximum page size:

Maximum limit = 100

Therefore:

GET /customers?page=1&limit=101

fails validation rather than allowing an unnecessarily large response.

This is important because pagination is not simply a frontend feature.

I see it as a resource-management mechanism that protects the API, database and consuming applications.

11. Why I Would Not Return One Million Records

If a stakeholder asked:

"Why can't we just increase the limit to one million so the client makes fewer requests?"

I would first understand the actual business requirement.

I would ask:

How many records does the consumer actually need?
Is the consumer displaying the data or processing it?
How frequently is the data requested?
What is the expected response latency?
What is the backend/database capacity?
Can the consumer process a million records in memory?

I would then choose an appropriate page size and retrieval strategy.

For very large and frequently changing datasets, I would also evaluate cursor/keyset pagination rather than assuming offset pagination is always the best solution.

12. In-Memory Data vs Production Storage

The one-million-record dataset is intentionally stored in Python memory for this learning project.

That allows me to demonstrate API behavior without introducing database infrastructure into the first phase.

However, this is not how I would deploy the production system.

The production architecture would be closer to:

Client
   |
   v
API
   |
   v
Repository / Data Access Layer
   |
   v
Database

The API should request only the records required for the current operation.

I would not load an entire production customer table into application memory during startup.

This exercise actually made that distinction very clear to me because the application startup time increased when the one-million-record dataset was generated.

13. Error Handling

I treated errors as part of the API contract.

Different failures communicate different things to the consumer.

The API uses meaningful HTTP status codes:

Status	Meaning
200	Successful request
201	Resource created
204	Successful operation with no response body
401	Authentication failure
403	Insufficient permissions
404	Resource not found
422	Request validation failure
429	Rate limit exceeded
500	Unexpected server-side failure

For example:

GET /customers/9999999

when the customer doesn't exist returns:

404 Not Found

rather than:

500 Internal Server Error

A 500 response would incorrectly suggest that the server itself failed when the actual condition is simply that the requested resource does not exist.

14. Safe Error Responses

I also considered the difference between information returned to the client and information retained in server-side diagnostics.

A client should not receive internal details such as:

database connection strings
internal IP addresses
stack traces
SQL statements
implementation details
secrets

Instead, the API should return a safe message while detailed diagnostics remain in application logs.

The general principle is:

Client
   |
   | Safe error response
   v
API


Backend
   |
   | Detailed diagnostics
   v
Logs / Monitoring
15. Rate Limiting

A shared API cannot assume that every consumer will behave predictably.

A client could accidentally create:

10,000 requests/second

because of:

a retry loop
a frontend bug
an integration problem
unexpected traffic growth

This could overload the application or downstream database.

I therefore added a simple sliding-window rate limiter.

The demonstration limit is:

100 requests / 60 seconds

When the limit is exceeded:

429 Too Many Requests

is returned.

16. Why Rate Limiting Must Be Designed Carefully

The current implementation stores rate-limit state in application memory.

This is sufficient for demonstrating the concept, but it is not sufficient for a horizontally scaled production service.

For example:

Load Balancer
     |
  +--+--+
  |  |  |
 API API API

If every API instance maintains its own counter, the same client could effectively receive a separate limit from each instance.

For production I would consider enforcing rate limits at a centralized API gateway or using a shared distributed mechanism such as Redis.

The actual limit should also be based on:

expected traffic
service capacity
client requirements
tenant requirements
endpoint cost

I would not select a rate limit arbitrarily.

17. OpenAPI

Once the API design was established, I wanted the interface to be understandable without requiring consumers to inspect the backend source code.

FastAPI automatically generates an OpenAPI specification.

The service exposes:

/docs

for interactive Swagger UI documentation.

It also exposes:

/openapi.json

as the machine-readable API contract.

And:

/redoc

for ReDoc-based documentation.

The distinction I use is:

OpenAPI
    |
    +---- /openapi.json
    |      Machine-readable contract
    |
    +---- /docs
    |      Interactive Swagger UI
    |
    +---- /redoc
           Alternative documentation interface
18. Why OpenAPI Matters

I see OpenAPI as more than automatically generated documentation.

It gives frontend and downstream teams a shared contract describing:

endpoints
HTTP methods
parameters
request bodies
response schemas
validation
authentication
possible responses

This reduces integration ambiguity.

It also creates a foundation for future capabilities such as:

client SDK generation
contract testing
API mocking
automated documentation
API lifecycle management
19. Technology Choices
Component	Choice
Language	Python
API Framework	FastAPI
Validation	Pydantic
Data Repository	In-memory
API Documentation	OpenAPI / Swagger UI / ReDoc
Testing	Pytest + FastAPI TestClient
Authentication	Demonstration Bearer tokens
Rate Limiting	In-memory sliding window
20. Project Structure
rest-api-engineering/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── repository.py
│   ├── auth.py
│   └── rate_limit.py
│
├── tests/
│   └── test_customers.py
│
├── requirements.txt
├── pytest.ini
└── README.md

I intentionally separated the API layer, data access, authentication, rate limiting and data models instead of putting the entire application into one file.

This makes the design easier to understand and gives each concern a clear responsibility.

21. Running the Application

Create and activate a virtual environment:

python -m venv .venv

Activate it on Windows:

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Start the API:

uvicorn app.main:app --reload

The API will be available at:

http://127.0.0.1:8000
22. API Documentation

Open:

http://127.0.0.1:8000/docs

for interactive Swagger UI.

Open:

http://127.0.0.1:8000/redoc

for ReDoc.

Open:

http://127.0.0.1:8000/openapi.json

for the machine-readable OpenAPI contract.

23. Example Requests
Health
GET /health

Response:

{
  "status": "healthy"
}
Retrieve customer
GET /customers/101
Authorization: Bearer phase1-viewer
Retrieve customers
GET /customers?page=1&limit=20
Authorization: Bearer phase1-viewer
Create customer
POST /customers
Authorization: Bearer phase1-admin
Content-Type: application/json


{
  "name": "New Customer",
  "email": "newcustomer@example.com"
}
Update customer
PATCH /customers/101
Authorization: Bearer phase1-admin
Content-Type: application/json


{
  "name": "Updated Customer"
}
Delete customer
DELETE /customers/101
Authorization: Bearer phase1-admin
24. What I Would Change for Production

This project intentionally focuses on REST API engineering fundamentals.

Before production deployment, I would address several areas.

Authentication

Replace demonstration tokens with a real identity provider using OAuth2/OIDC and proper access-token validation.

Data storage

Replace the in-memory repository with a production database such as Azure SQL or PostgreSQL.

Rate limiting

Move rate-limit enforcement to an API gateway or shared distributed mechanism.

Secrets

Move secrets and credentials into a secure secret-management solution rather than source code.

Observability

Add:

structured logging
metrics
distributed tracing
request correlation
dashboards
alerting
Deployment

Containerize the API and deploy it behind an appropriate ingress/API gateway.

Testing

Expand testing to include:

unit tests
integration tests
contract tests
load tests
security tests
CI/CD

Add automated:

Lint
  ↓
Unit Tests
  ↓
Integration Tests
  ↓
Build
  ↓
Security Scan
  ↓
Deploy
25. What I Learned From This Exercise

The biggest thing I took away from this exercise is that building an API is not just about writing endpoints.

Initially, the requirement could be reduced to:

"Create CRUD endpoints for customers."

But once I considered the system as something another team would consume, the design became broader.

I had to think about:

Resource design
      ↓
Authentication
      ↓
Authorization
      ↓
Request metadata
      ↓
Large datasets
      ↓
Failure handling
      ↓
Traffic protection
      ↓
API contract

The one-million-record simulation was particularly useful because it made pagination and resource management concrete.

It also showed me that an API design decision cannot be evaluated only from the endpoint itself. The impact extends to the database, network, application memory, client and overall system capacity.

26. Client Conversation

If I were presenting this solution to a client, I would not start by explaining FastAPI.

I would start with the problem.

I would say:

"I approached the API as a contract between your systems rather than simply a set of backend functions. I structured the API around customer resources, used HTTP methods to communicate operations, and introduced authentication and authorization so that identity and permissions are explicit."

Then I would explain scale:

"Because the customer dataset can grow significantly, I don't want the API to expose an unbounded collection. I introduced pagination with a controlled maximum page size so that the consumer gets predictable responses without unnecessarily loading the backend or network."

Then reliability:

"I also treated failures and traffic spikes as part of the API design. The API uses meaningful status codes, consistent validation behavior and rate limiting so consumers can distinguish between invalid requests, authorization problems, missing resources and temporary service constraints."

Finally, the contract:

"The API is exposed through OpenAPI, so your frontend and downstream teams can understand the endpoints, schemas, authentication requirements and expected responses without needing to inspect the backend implementation."

This is the way I would want to communicate the solution because it focuses on business requirements and engineering decisions rather than technology for technology's sake.

27. Phase 1 Outcome

The Phase 1 exercise resulted in a documented FastAPI service demonstrating:

 HTTP fundamentals
 REST resource-oriented design
 Authentication
 Authorization
 HTTP headers
 Pagination
 Error handling
 Rate limiting
 OpenAPI
 Interactive API documentation
 One-million-record simulation
 Basic automated API testing

The implementation intentionally separates learning/demo decisions from production architecture decisions.

That distinction is important because a solution can successfully demonstrate an engineering concept without pretending that every implementation detail is production-ready.



---


# 🎯 This README is doing something important


Notice what we **didn't** do.


We didn't write:


> "REST means Representational State Transfer."


and then spend 500 words defining it.


Instead, the document tells a story:


**Client problem → design decision → technical implementation → tradeoff → production consideration.**


That's exactly the skill you told me you wanted to practice.


---


## One change I want you to make


At the very top, after:


```markdown
# Customer Operations API
### Phase 1 — REST API Engineering

add this:

> **My objective:** Build an API that is not only functional, but predictable, secure, scalable in its interface, observable during failures, and understandable to another engineering team.

That gives the document a clear personal engineering objective rather than making it look like generated documentation.