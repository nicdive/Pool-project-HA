"""HTTP client for Arduino / web-relay GET commands."""

from __future__ import annotations

import logging
from urllib.parse import quote

from aiohttp import ClientError, ClientSession, ClientTimeout

from .const import DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class PoolHttpClientError(Exception):
    """Raised when a command request fails."""


class PoolHttpClient:
    """Send GET commands to a single host (e.g. Arduino Ethernet)."""

    def __init__(self, session: ClientSession, host: str, port: int) -> None:
        self._session = session
        self._host = host.strip()
        self._port = port
        self._timeout = ClientTimeout(total=DEFAULT_TIMEOUT)

    @property
    def base_url(self) -> str:
        """Base URL without trailing path."""
        if self._port == 80:
            return f"http://{self._host}"
        return f"http://{self._host}:{self._port}"

    def command_url(self, path: str) -> str:
        """Build absolute URL for a command path (e.g. ouvre / ferme)."""
        cleaned = path.strip().lstrip("/")
        # Keep path segments safe but allow simple Arduino routes like "ouvre"
        encoded = "/".join(quote(segment, safe="") for segment in cleaned.split("/"))
        return f"{self.base_url}/{encoded}"

    async def async_send_command(self, path: str) -> None:
        """Issue HTTP GET to host/path (eedomus-compatible)."""
        url = self.command_url(path)
        _LOGGER.debug("GET %s", url)
        try:
            async with self._session.get(url, timeout=self._timeout) as response:
                # Arduino sketches often return 200 with a short body; accept 2xx.
                if response.status >= 400:
                    body = await response.text()
                    raise PoolHttpClientError(
                        f"HTTP {response.status} for {url}: {body[:200]}"
                    )
                # Drain body so the connection can be reused
                await response.read()
        except TimeoutError as err:
            raise PoolHttpClientError(f"Timeout calling {url}") from err
        except ClientError as err:
            raise PoolHttpClientError(f"Request failed for {url}: {err}") from err

    async def async_test_connection(self) -> bool:
        """Best-effort reachability check (any HTTP response means host is up)."""
        url = f"{self.base_url}/"
        try:
            async with self._session.get(url, timeout=self._timeout) as response:
                await response.read()
                return True
        except (TimeoutError, ClientError) as err:
            _LOGGER.debug("Connection test failed for %s: %s", url, err)
            return False
