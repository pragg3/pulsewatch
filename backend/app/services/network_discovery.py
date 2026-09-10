import asyncio
import socket
from ipaddress import IPv4Address

import dns.exception
import dns.resolver
import dns.reversename

from backend.app.core.config import (
    NETWORK_DNS_SERVER,
    NETWORK_DNS_TIMEOUT_SECONDS,
    NETWORK_PROBE_TIMEOUT_SECONDS,
    NETWORK_SCAN_CONCURRENCY,
)
from backend.app.schemas.network import DiscoveredHost

# V1 uses a deliberately small, fixed set of common service ports.
#
# These are reachability hints. This is NOT intended to be a
# user-configurable arbitrary port scanner.
PROBE_PORTS = (
    80,  # HTTP
    443,  # HTTPS
    22,  # SSH
    445,  # SMB
    3389,  # RDP
)


async def try_tcp_connection(
    ip: str,
    port: int,
) -> bool:
    """
    Attempt a TCP connection to one approved port.

    Returns True only when the TCP connection succeeds.
    """

    try:
        _reader, writer = await asyncio.wait_for(
            asyncio.open_connection(
                ip,
                port,
            ),
            timeout=NETWORK_PROBE_TIMEOUT_SECONDS,
        )

        writer.close()

        try:
            await writer.wait_closed()
        except OSError:
            pass

        return True

    except (
        TimeoutError,
        ConnectionRefusedError,
        OSError,
    ):
        return False


async def is_reachable(ip: str) -> bool:
    """
    Determine whether a host responds on at least one approved
    TCP service port.
    """

    tasks = [asyncio.create_task(try_tcp_connection(ip, port)) for port in PROBE_PORTS]

    try:
        for task in asyncio.as_completed(tasks):
            if await task:
                return True

        return False

    finally:
        for task in tasks:
            if not task.done():
                task.cancel()


def system_reverse_dns_lookup(ip: str) -> str | None:
    """
    Resolve an address using the operating system's configured
    resolver.

    This remains the default when no installation-specific DNS
    server has been configured.
    """

    try:
        hostname, _aliases, _addresses = socket.gethostbyaddr(ip)

        return hostname.rstrip(".")

    except (
        socket.herror,
        socket.gaierror,
        OSError,
    ):
        return None


def configured_reverse_dns_lookup(
    ip: str,
    dns_server: str,
) -> str | None:
    """
    Perform a PTR lookup against an explicitly configured internal
    DNS resolver.

    The resolver address is installation configuration and is never
    supplied by the network-discovery request.
    """

    resolver = dns.resolver.Resolver(
        configure=False,
    )

    resolver.nameservers = [
        dns_server,
    ]

    resolver.timeout = NETWORK_DNS_TIMEOUT_SECONDS
    resolver.lifetime = NETWORK_DNS_TIMEOUT_SECONDS

    try:
        reverse_name = dns.reversename.from_address(ip)

        answers = resolver.resolve(
            reverse_name,
            "PTR",
        )

        for answer in answers:
            hostname = str(answer).rstrip(".")

            if hostname:
                return hostname

        return None

    except (
        dns.exception.DNSException,
        ValueError,
    ):
        return None


def reverse_dns_lookup(ip: str) -> str | None:
    """
    Resolve an IP address to a hostname.

    If an internal DNS server has been configured for this
    installation, use it. Otherwise fall back to the operating
    system resolver.
    """

    if NETWORK_DNS_SERVER:
        return configured_reverse_dns_lookup(
            ip,
            NETWORK_DNS_SERVER,
        )

    return system_reverse_dns_lookup(ip)


async def resolve_hostname(ip: str) -> str | None:
    """
    DNS resolution is blocking, so execute it in a worker thread
    rather than blocking FastAPI's asyncio event loop.
    """

    return await asyncio.to_thread(
        reverse_dns_lookup,
        ip,
    )


async def inspect_host(
    address: IPv4Address,
    semaphore: asyncio.Semaphore,
) -> DiscoveredHost | None:
    """
    Inspect one authorized address.

    Hostname resolution happens only after reachability has been
    established.
    """

    ip = str(address)

    async with semaphore:
        reachable = await is_reachable(ip)

        if not reachable:
            return None

        hostname = await resolve_hostname(ip)

        return DiscoveredHost(
            ip=ip,
            hostname=hostname,
            reachable=True,
        )


async def discover_hosts(
    addresses: list[IPv4Address],
) -> list[DiscoveredHost]:
    """
    Discover reachable hosts while limiting concurrent work.
    """

    semaphore = asyncio.Semaphore(NETWORK_SCAN_CONCURRENCY)

    tasks = [
        asyncio.create_task(
            inspect_host(
                address,
                semaphore,
            )
        )
        for address in addresses
    ]

    results = await asyncio.gather(
        *tasks,
        return_exceptions=True,
    )

    hosts = [result for result in results if isinstance(result, DiscoveredHost)]

    hosts.sort(key=lambda host: int(IPv4Address(host.ip)))

    return hosts
