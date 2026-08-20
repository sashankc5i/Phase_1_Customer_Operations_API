import asyncio
import random

import httpx


RETRYABLE_STATUS_CODES = {
    408,
    429,
    500,
    502,
    503,
    504,
}


async def request_with_retry(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    max_retries: int = 3,
    **kwargs,
) -> httpx.Response:

    for attempt in range(max_retries + 1):

        try:

            response = await client.request(
                method,
                url,
                **kwargs,
            )

            if (
                response.status_code
                not in RETRYABLE_STATUS_CODES
            ):
                return response

            if attempt == max_retries:
                return response

        except (
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.ConnectError,
        ):

            if attempt == max_retries:
                raise

        delay = (
            0.5 * (2 ** attempt)
            + random.uniform(0, 0.2)
        )

        await asyncio.sleep(delay)

    raise RuntimeError("Retry logic exhausted")