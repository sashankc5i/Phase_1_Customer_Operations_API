import httpx

from .retry import request_with_retry


class NotificationClient:

    def __init__(
        self,
        base_url: str,
        api_key: str,
    ):
        self.base_url = base_url
        self.api_key = api_key

        self.timeout = httpx.Timeout(
            connect=2.0,
            read=5.0,
            write=5.0,
            pool=2.0,
        )

    async def send_notification(
        self,
        customer_id: int,
        message: str,
    ):

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:

            response = await request_with_retry(
                client,
                "POST",
                f"{self.base_url}/mock/notifications",
                headers={
                    "X-API-Key": self.api_key
                },
                json={
                    "customer_id": customer_id,
                    "message": message,
                },
            )

            response.raise_for_status()

            return response.json()