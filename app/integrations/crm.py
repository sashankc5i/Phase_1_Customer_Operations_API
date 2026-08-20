import time

import httpx

from .circuit_breaker import CircuitBreaker
from .retry import request_with_retry


class CRMClient:

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
    ):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret

        self.access_token = None
        self.token_expires_at = 0

        self.circuit_breaker = CircuitBreaker()

        self.timeout = httpx.Timeout(
            connect=2.0,
            read=5.0,
            write=5.0,
            pool=2.0,
        )

    async def get_access_token(self):

        if (
            self.access_token
            and time.time() < self.token_expires_at - 30
        ):
            return self.access_token

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:

            response = await client.post(
                f"{self.base_url}/mock/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )

            response.raise_for_status()

            data = response.json()

            self.access_token = data["access_token"]

            self.token_expires_at = (
                time.time()
                + data.get("expires_in", 3600)
            )

            return self.access_token

    async def get_customer_profile(
        self,
        customer_id: int,
    ):

        if not self.circuit_breaker.can_execute():
            raise RuntimeError(
                "CRM circuit breaker is open"
            )

        try:

            token = await self.get_access_token()

            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:

                response = await request_with_retry(
                    client,
                    "GET",
                    f"{self.base_url}/mock/crm/customers/{customer_id}",
                    headers={
                        "Authorization":
                            f"Bearer {token}"
                    },
                )

                response.raise_for_status()

                self.circuit_breaker.record_success()

                return response.json()

        except Exception:
            self.circuit_breaker.record_failure()
            raise