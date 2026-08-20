import httpx

from .circuit_breaker import CircuitBreaker
from .retry import request_with_retry


class PaymentClient:

    def __init__(
        self,
        base_url: str,
        api_key: str,
    ):
        self.base_url = base_url
        self.api_key = api_key

        self.circuit_breaker = CircuitBreaker()

        self.timeout = httpx.Timeout(
            connect=2.0,
            read=5.0,
            write=5.0,
            pool=2.0,
        )

    async def get_payment_status(
        self,
        customer_id: int,
    ):

        if not self.circuit_breaker.can_execute():
            raise RuntimeError(
                "Payment circuit breaker is open"
            )

        try:

            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:

                response = await request_with_retry(
                    client,
                    "GET",
                    f"{self.base_url}/mock/payments/{customer_id}",
                    headers={
                        "X-API-Key": self.api_key
                    },
                )

                response.raise_for_status()

                self.circuit_breaker.record_success()

                return response.json()

        except Exception:
            self.circuit_breaker.record_failure()
            raise