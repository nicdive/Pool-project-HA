"""Unit tests for PoolHttpClient / helpers (no Home Assistant required)."""

from __future__ import annotations

import asyncio
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
PKG = "pool_http_actuators"
PKG_DIR = ROOT / "custom_components" / PKG


def _load_module(fullname: str, path: Path):
    spec = importlib.util.spec_from_file_location(fullname, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[fullname] = module
    spec.loader.exec_module(module)
    return module


# Minimal package stub so relative imports in http_client work
_pkg = types.ModuleType(PKG)
_pkg.__path__ = [str(PKG_DIR)]
sys.modules[PKG] = _pkg
_load_module(f"{PKG}.const", PKG_DIR / "const.py")
_http = _load_module(f"{PKG}.http_client", PKG_DIR / "http_client.py")
_helpers = _load_module(f"{PKG}.helpers", PKG_DIR / "helpers.py")
PoolHttpClient = _http.PoolHttpClient
PoolHttpClientError = _http.PoolHttpClientError
slugify = _helpers.slugify


class FakeResponse:
    def __init__(self, status: int = 200, body: bytes = b"ok") -> None:
        self.status = status
        self._body = body

    async def text(self) -> str:
        return self._body.decode()

    async def read(self) -> bytes:
        return self._body

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None


class TestPoolHttpClient(unittest.TestCase):
    def test_command_url_default_port(self) -> None:
        client = PoolHttpClient(MagicMock(), "192.168.23.241", 80)
        self.assertEqual(
            client.command_url("ouvre"),
            "http://192.168.23.241/ouvre",
        )
        self.assertEqual(
            client.command_url("/ferme"),
            "http://192.168.23.241/ferme",
        )

    def test_command_url_custom_port(self) -> None:
        client = PoolHttpClient(MagicMock(), "192.168.23.241", 8080)
        self.assertEqual(
            client.command_url("ouvre"),
            "http://192.168.23.241:8080/ouvre",
        )

    def test_send_command_success(self) -> None:
        session = MagicMock()
        session.get = MagicMock(return_value=FakeResponse(200))
        client = PoolHttpClient(session, "192.168.23.241", 80)

        async def _run() -> None:
            await client.async_send_command("ouvre")

        asyncio.run(_run())
        session.get.assert_called_once()
        args, _kwargs = session.get.call_args
        self.assertEqual(args[0], "http://192.168.23.241/ouvre")

    def test_send_command_http_error(self) -> None:
        session = MagicMock()
        session.get = MagicMock(return_value=FakeResponse(500, b"fail"))
        client = PoolHttpClient(session, "192.168.23.241", 80)

        async def _run() -> None:
            await client.async_send_command("ferme")

        with self.assertRaises(PoolHttpClientError):
            asyncio.run(_run())


class TestSlugify(unittest.TestCase):
    def test_basic(self) -> None:
        self.assertEqual(slugify("Cascade"), "cascade")

    def test_accents(self) -> None:
        self.assertEqual(slugify("Éclairage"), "eclairage")

    def test_spaces(self) -> None:
        self.assertEqual(slugify("Pompe pH"), "pompe_ph")


if __name__ == "__main__":
    unittest.main()
