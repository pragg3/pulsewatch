import secrets
from ipaddress import IPv4Address, IPv4Network

from fastapi import Header, HTTPException, status

from backend.app.core.config import (
    NETWORK_DISCOVERY_ENABLED,
    NETWORK_DISCOVERY_KEY,
    NETWORK_MAX_SCAN_HOSTS,
)

# These are Internet-standard RFC1918 private IPv4 spaces.
#
# They are NOT customer/company-specific network configuration.
PRIVATE_IPV4_NETWORKS = (
    IPv4Network("10.0.0.0/8"),
    IPv4Network("172.16.0.0/12"),
    IPv4Network("192.168.0.0/16"),
)


def ensure_network_discovery_enabled() -> None:
    if not NETWORK_DISCOVERY_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Network discovery is disabled.",
        )


def require_discovery_key(
    x_pulsewatch_discovery_key: str | None = Header(
        default=None,
        alias="X-PulseWatch-Discovery-Key",
    ),
) -> None:
    """
    Require additional authorization before exposing LAN discovery.

    The key must come from runtime secret configuration and must
    never be committed to Git.
    """

    if not NETWORK_DISCOVERY_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Network discovery authentication "
                "is not configured."
            ),
        )

    if x_pulsewatch_discovery_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Network discovery authentication required.",
        )

    if not secrets.compare_digest(
        x_pulsewatch_discovery_key,
        NETWORK_DISCOVERY_KEY,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid network discovery credentials.",
        )


def _private_network_for(
    address: IPv4Address,
) -> IPv4Network | None:
    """
    Return the standardized RFC1918 network containing an address.
    """

    return next(
        (
            network
            for network in PRIVATE_IPV4_NETWORKS
            if address in network
        ),
        None,
    )


def validate_scan_range(
    start_ip: str,
    end_ip: str,
) -> list[IPv4Address]:
    start = IPv4Address(start_ip)
    end = IPv4Address(end_ip)

    if end < start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "end_ip must be greater than or equal "
                "to start_ip."
            ),
        )

    start_network = _private_network_for(start)
    end_network = _private_network_for(end)

    if start_network is None or end_network is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Public or non-private addresses are not "
                "permitted for LAN discovery."
            ),
        )

    if start_network != end_network:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "The complete discovery range must remain "
                "inside one private IPv4 address space."
            ),
        )

    host_count = int(end) - int(start) + 1

    if host_count > NETWORK_MAX_SCAN_HOSTS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Requested range contains {host_count} addresses. "
                f"Maximum allowed is {NETWORK_MAX_SCAN_HOSTS}."
            ),
        )

    addresses = [
        IPv4Address(value)
        for value in range(
            int(start),
            int(end) + 1,
        )
    ]

    # Defence in depth: reject unusual address types even if
    # validation rules change later.
    for address in addresses:
        if (
            address.is_loopback
            or address.is_link_local
            or address.is_multicast
            or address.is_unspecified
            or address.is_reserved
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Special-purpose addresses are not "
                    "permitted for LAN discovery."
                ),
            )

    return addresses