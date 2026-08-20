Phase 3 — Repository Structure
Your project should now look like:
customer-operations-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── repository.py
│   ├── auth.py
│   ├── rate_limit.py
│   │
│   └── integrations/
│       ├── __init__.py
│       ├── crm.py
│       ├── payment.py
│       ├── notification.py
│       ├── retry.py
│       └── circuit_breaker.py
│
├── tests/
│   └── test_customers.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .gitignore
├── README.md
├── requirements.txt
└── pytest.ini
________________________________________
1. .gitignore
At the root of the repository create:
.gitignore
Paste:
# ==========================================================
# Python
# ==========================================================

__pycache__/
*.py[cod]
*.pyo
*.pyd

# ==========================================================
# Virtual environments
# ==========================================================

.venv/
venv/
env/
ENV/

# ==========================================================
# Environment variables / secrets
# ==========================================================

.env
.env.*
!.env.example

# ==========================================================
# Testing / Coverage
# ==========================================================

.pytest_cache/
.coverage
htmlcov/
.coverage.*

# ==========================================================
# Type checking / tooling
# ==========================================================

.mypy_cache/
.ruff_cache/

# ==========================================================
# IDE
# ==========================================================

.vscode/
.idea/

# ==========================================================
# OS
# ==========================================================

.DS_Store
Thumbs.db

# ==========================================================
# Logs
# ==========================================================

*.log

# ==========================================================
# Build artifacts
# ==========================================================

build/
dist/
*.egg-info/
Why this matters
The most important part for our project is:
.env
.env.*
because Phase 2 introduced:
OAuth client secret
API keys
We never want those accidentally committed.
________________________________________
2. .env.example
I recommend adding an example configuration file.
Create:
.env.example
Put:
# CRM OAuth
CRM_CLIENT_ID=your-client-id
CRM_CLIENT_SECRET=your-client-secret
CRM_BASE_URL=https://crm.example.com

# Payment API
PAYMENT_API_KEY=your-payment-api-key
PAYMENT_BASE_URL=https://payment.example.com

# Notification API
NOTIFICATION_API_KEY=your-notification-api-key
NOTIFICATION_BASE_URL=https://notification.example.com
This file is safe to commit because it contains placeholders, not real secrets.
It tells another developer:
"These are the configuration values this application expects."
________________________________________
3. requirements.txt
Let's make the dependency file explicit.
fastapi
uvicorn[standard]
pydantic
email-validator
httpx
pytest
python-multipart
For a truly production repository, we'd eventually pin versions or use a lock/dependency-management strategy.
For today's exercise, this is sufficient.
________________________________________
4. pytest.ini
Keep:
[pytest]
pythonpath = .
This makes the project root available to pytest.
We already verified that the test suite passes.
________________________________________
5. GitHub Actions workflow
Create:
.github/workflows/ci.yml
Use:
name: Customer API CI

on:
  push:
    branches:
      - main
      - "feature/**"

  pull_request:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: |
          python -m pytest -q
________________________________________
6. README.md
You already have our Phase 1 + Phase 2 documentation.
For the standalone repository, the README should eventually contain:
Customer Operations API
│
├── Project Overview
├── Architecture
├── Features
├── API Endpoints
├── Authentication
├── Enterprise Integrations
├── Local Setup
├── Testing
├── CI Workflow
├── Production Considerations
└── Documentation
Don't rewrite it right now.
Copy the README we've already created into this repository and we'll add a small Phase 3 section later.
________________________________________
7. Add a CONTRIBUTING.md
Since the objective is a professional development workflow, this is worthwhile.
Create:
CONTRIBUTING.md
Use:
# Contributing

## Development Workflow

All feature development should happen on a dedicated branch.

Example:

```text
feature/add-customer-search
fix/payment-timeout
docs/update-api-guide
Changes should be submitted through a Pull Request rather than pushed directly to main.
Before Opening a Pull Request
Run the test suite locally:
python -m pytest -q
Make sure:
•	Tests pass
•	No secrets are committed
•	Documentation is updated when required
•	The change has a meaningful commit message
Pull Requests
A Pull Request should explain:
•	What changed
•	Why the change was required
•	How it was tested
•	Any known limitations
CI checks must pass before the change is merged.
Commit Messages
Use descriptive commit messages.
Examples:
feat: add customer search
fix: handle payment timeout
test: add webhook validation tests
docs: update integration guide
ci: add GitHub Actions workflow
Secrets
Never commit:
•	API keys
•	OAuth client secrets
•	passwords
•	access tokens
•	.env files containing real credentials
Use environment variables or an appropriate secret-management system.

---

# 8. Optional `LICENSE`

For a personal portfolio project, we **don't need to add a license right now** unless you actually want others to reuse the code.

So skip it for now.

---

# ✅ Final repository

After these changes:

```text
customer-operations-api/
│
├── app/
├── tests/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
├── README.md
├── requirements.txt
└── pytest.ini
This already looks substantially more like a real engineering repository than our original learning workspace.
________________________________________
🔐 One important cleanup before Git
Because our Phase 2 code currently contains demo credentials such as:
client_id="phase2-client"
client_secret="phase2-secret"
and:
api_key="phase2-payment-key"
don't put actual production credentials into the code.
For today's mock integration they're harmless demo values, but in the standalone repository I'd like us to eventually move the configuration to environment variables:
CRM_CLIENT_ID = os.getenv("CRM_CLIENT_ID")
CRM_CLIENT_SECRET = os.getenv("CRM_CLIENT_SECRET")
and similarly for the API keys.
That gives us another excellent Phase 3 lesson:
Git workflow and security are connected — repository hygiene isn't just about branches and PRs; it's also about preventing credentials from becoming part of source control history.
