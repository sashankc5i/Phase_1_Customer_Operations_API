Phase 2 — Enterprise API Integration
1. The Problem
After building the Customer Operations API, I wanted to understand what happens when my API depends on systems that I don't control.
In a real enterprise environment, our API may need to communicate with CRM, payment and notification systems. Those systems can have different authentication mechanisms, response times and failure patterns.
So the goal of Phase 2 was to build an integration layer that can communicate with external services without allowing those external failures to directly bring down our API.
________________________________________
2. OAuth
For the CRM integration, I used the OAuth 2.0 client credentials flow.
The important thing I learned was that the client ID and client secret are used to authenticate the application with the authorization server. They are not directly sent to the CRM resource API.
The flow is:
Client ID + Secret
        ↓
Authorization Server
        ↓
Access Token
        ↓
CRM API
Our CRM client caches the access token and reuses it until it approaches expiry.
For this project, the credentials are demo values. In production, I would store them in a secret-management system.
________________________________________
3. API Keys
For the payment and notification services, I used API-key-based authentication.
For example:
X-API-Key: phase2-payment-key
I learned that not every external integration needs OAuth. The authentication mechanism should depend on the contract provided by the external service and the security requirements.
The important part is that credentials should never be hard-coded in a production application.
________________________________________
4. Timeouts
One of the biggest risks when calling an external API is waiting indefinitely.
I therefore configured explicit httpx timeouts for:
•	connection
•	reading the response
•	writing the request
•	connection pool
The thinking was simple:
An external service should not be allowed to hold our application resources indefinitely.
If the payment service becomes slow, our API should eventually stop waiting and handle the failure.
________________________________________
5. Retries
A temporary failure doesn't always mean the external service is permanently unavailable.
For retryable failures such as:
408
429
500
502
503
504
our integration layer can retry the request.
I used exponential backoff with jitter instead of immediately retrying.
Attempt 1
   ↓
wait
   ↓
Attempt 2
   ↓
wait longer
   ↓
Attempt 3
The important lesson for me was that we shouldn't blindly retry every failure.
A 404 or 400 generally isn't fixed by sending the same request again.
I also learned that retries need to consider idempotency. Retrying a payment operation without an idempotency strategy could potentially create a duplicate transaction.
________________________________________
6. Webhooks
The direction of communication changes with a webhook.
Instead of:
Our API → External API
we have:
External API → Our API
I implemented:
POST /webhooks/notification
and validated the webhook signature before accepting the event.
The webhook also requires an event_id.
In a production implementation, I would persist that event ID and use it for idempotency because external providers may deliver the same event more than once.
The important principle I took away is:
A webhook should be treated as an external, untrusted event rather than automatically trusted input.
________________________________________
7. Async API Calls
The enterprise profile endpoint needs information from both the CRM and payment services.
These calls are independent, so I used asynchronous HTTP calls.
Instead of:
CRM
 ↓
wait
 ↓
Payment
 ↓
wait
I can do:
       ┌→ CRM
Request ┤
       └→ Payment
             ↓
          Response
using asyncio.gather().
This is useful for I/O-bound operations because the application doesn't need to sit idle while one external service responds.
I also learned that async should not be added just because it sounds faster. It makes sense when the operations are independent and primarily waiting on I/O.
________________________________________
8. Circuit Breaker
Retries alone aren't enough.
If the payment service is completely unavailable, repeatedly retrying every customer request can make our own API slower and consume resources unnecessarily.
I therefore introduced a circuit breaker with three states:
CLOSED
  ↓ repeated failures
OPEN
  ↓ recovery period
HALF-OPEN
  ↓
success → CLOSED
failure → OPEN
When the circuit is open, the application stops calling the unhealthy dependency and fails fast.
This protects our system from continuously depending on a service that is currently unavailable.
________________________________________
9. Three Enterprise Integrations
I integrated three enterprise-style services:
Service	Authentication	Main concepts
CRM	OAuth 2.0	OAuth, token caching, retries, timeout
Payment	API Key	API keys, retries, timeout, circuit breaker
Notification	API Key	API keys, webhooks
The Customer API acts as the integration layer between the consumer and these external services.
________________________________________
10. What I Learned
The biggest change in my thinking from Phase 1 to Phase 2 was this:
In Phase 1, I was designing an API. In Phase 2, I had to design for dependency failure.
An external API is not something I can assume will always respond quickly or successfully.
So before calling an external service, I now think about:
Authentication
      ↓
Timeout
      ↓
Retry policy
      ↓
Idempotency
      ↓
Circuit breaker
      ↓
Failure handling
And if the external system needs to notify us:
Webhook
   ↓
Verify
   ↓
Identify event
   ↓
Check idempotency
   ↓
Process
That is the main engineering lesson I took from this phase.
