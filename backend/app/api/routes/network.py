import socket

from fastapi import APIRouter, Depends, Request

from backend.app.api.dependencies.network_security import (
    ensure_network_discovery_enabled,
    require_discovery_key,
    validate_scan_range,
)
from backend.app.core.config import (
    NETWORK_SCAN_RATE_LIMIT,
    NETWORK_TRUST_PROXY_HEADERS,
)
from backend.app.core.rate_limit import limiter
from backend.app.schemas.network import (
    NetworkInfoResponse,
    NetworkScanRequest,
    NetworkScanResponse,
)
from backend.app.services.network_discovery import discover_hosts

router = APIRouter(
    prefix="/network",
    tags=["network"],
)


def get_scanner_ip() -> str | None:
    """
    Determine the IPv4 address selected by the operating system
    for ordinary outbound traffic.
    """

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM,
    )

    try:
        sock.connect(("1.1.1.1", 80))
        return sock.getsockname()[0]

    except OSError:
        return None

    finally:
        sock.close()


def get_client_ip(
    request: Request,
) -> str | None:
    """
    Return the HTTP client's detected address.

    Proxy forwarding headers are only trusted when explicitly
    enabled by deployment configuration.
    """

    if NETWORK_TRUST_PROXY_HEADERS:
        forwarded_for = request.headers.get(
            "x-forwarded-for"
        )

        if forwarded_for:
            client_ip = forwarded_for.split(
                ",",
                maxsplit=1,
            )[0].strip()

            if client_ip:
                return client_ip

    if request.client:
        return request.client.host

    return None


@router.get(
    "/info",
    response_model=NetworkInfoResponse,
    dependencies=[
        Depends(ensure_network_discovery_enabled),
        Depends(require_discovery_key),
    ],
)
async def network_info(
    request: Request,
) -> NetworkInfoResponse:
    return NetworkInfoResponse(
        client_ip=get_client_ip(request),
        scanner_ip=get_scanner_ip(),
    )


@router.post(
    "/discover",
    response_model=NetworkScanResponse,
    dependencies=[
        Depends(ensure_network_discovery_enabled),
        Depends(require_discovery_key),
    ],
)
@limiter.limit(NETWORK_SCAN_RATE_LIMIT)
async def network_discover(
    request: Request,
    payload: NetworkScanRequest,
) -> NetworkScanResponse:
    addresses = validate_scan_range(
        payload.start_ip,
        payload.end_ip,
    )

    hosts = await discover_hosts(addresses)

    return NetworkScanResponse(
        start_ip=payload.start_ip,
        end_ip=payload.end_ip,
        requested_hosts=len(addresses),
        reachable_hosts=len(hosts),
        hosts=hosts,
    )