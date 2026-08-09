"""
Shared URL parsing/building helpers for the service-connection settings.

Redis and RabbitMQ both accept "either a URL or discrete parameters", and both
previously carried their own hand-rolled regex for it. One implementation on top
of :mod:`urllib.parse` handles percent-encoded credentials, IPv6 literals and
missing components correctly for both.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote, urlsplit


@dataclass(frozen=True)
class UrlParts:
    """Normalised components of a service connection URL."""

    scheme: str
    host: str
    port: int
    username: str | None
    password: str | None
    path: str


def parse_url(
    url: str,
    *,
    default_port: int,
    default_host: str,
    default_path: str = "",
) -> UrlParts:
    """
    Split ``url`` into its components.

    Raises:
        ValueError: if the URL has no scheme, i.e. is not a URL at all.
    """
    split = urlsplit(url)
    if not split.scheme:
        raise ValueError(f"Invalid connection URL (no scheme): {url!r}")

    return UrlParts(
        scheme=split.scheme,
        host=split.hostname or default_host,
        port=split.port or default_port,
        username=split.username or None,
        password=split.password or None,
        path=split.path or default_path,
    )


def build_url(
    *,
    scheme: str,
    host: str,
    port: int,
    username: str | None = None,
    password: str | None = None,
    path: str = "",
) -> str:
    """Assemble a connection URL, percent-encoding the credentials."""
    credentials = ""
    if username or password:
        credentials = (
            f"{quote(username or '', safe='')}:{quote(password or '', safe='')}@"
        )

    if path and not path.startswith("/"):
        path = f"/{path}"

    return f"{scheme}://{credentials}{host}:{port}{path}"
