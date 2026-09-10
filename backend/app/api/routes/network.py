import socket

from fastapi import APIRouter, Depends, Request

from backend.app.api.dependencies.network_security import (
    ensure_network_discovery_enabled,
    require_discovery_key,
    validate_scan_range,
)
from backend.app.core.config import (
    NETWORK_SCAN_RATE_LIMIT,
    PULSEWATCH_HOST_IP,
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


@router.get(
    "/info",
    response_model=NetworkInfoResponse,
    dependencies=[
        Depends(ensure_network_discovery_enabled),
        Depends(require_discovery_key),
    ],
)
async def network_info() -> NetworkInfoResponse:
    return NetworkInfoResponse(
        host_ip=PULSEWATCH_HOST_IP or None,
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
