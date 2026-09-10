import os
from ipaddress import IPv4Address

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://pulsewatch:pulsewatch@localhost:5432/pulsewatch",
)


def get_bool_env(
    name: str,
    default: bool = False,
) -> bool:
    """
    Read a boolean environment variable.

    Accepted true values:
    1, true, yes, on

    Accepted false values:
    0, false, no, off
    """

    value = os.getenv(name)

    if value is None:
        return default

    normalized = value.strip().lower()

    if normalized in {
        "1",
        "true",
        "yes",
        "on",
    }:
        return True

    if normalized in {
        "0",
        "false",
        "no",
        "off",
    }:
        return False

    raise RuntimeError(f"{name} must be a boolean value.")


# ---------------------------------------------------------------------------
# Network discovery
# ---------------------------------------------------------------------------

NETWORK_DISCOVERY_ENABLED = get_bool_env(
    "NETWORK_DISCOVERY_ENABLED",
    False,
)

NETWORK_DISCOVERY_KEY = os.getenv(
    "NETWORK_DISCOVERY_KEY",
    "",
).strip()

NETWORK_MAX_SCAN_HOSTS = int(
    os.getenv(
        "NETWORK_MAX_SCAN_HOSTS",
        "512",
    )
)

NETWORK_SCAN_CONCURRENCY = int(
    os.getenv(
        "NETWORK_SCAN_CONCURRENCY",
        "32",
    )
)

NETWORK_PROBE_TIMEOUT_SECONDS = float(
    os.getenv(
        "NETWORK_PROBE_TIMEOUT_SECONDS",
        "0.8",
    )
)

NETWORK_SCAN_RATE_LIMIT = os.getenv(
    "NETWORK_SCAN_RATE_LIMIT",
    "5/minute",
).strip()

NETWORK_TRUST_PROXY_HEADERS = get_bool_env(
    "NETWORK_TRUST_PROXY_HEADERS",
    False,
)


# ---------------------------------------------------------------------------
# Network discovery DNS
# ---------------------------------------------------------------------------
#
# NETWORK_DNS_SERVER is optional.
#
# When empty, hostname discovery uses the operating system / Kubernetes
# resolver.
#
# An installation that has private internal DNS may provide the address of
# its internal resolver through the environment. No customer-specific DNS
# address is hardcoded in PulseWatch.
#
# Example installation configuration:
#
# NETWORK_DNS_SERVER=<internal DNS IPv4 address>
#
# Do not put organization-specific values in source control.

NETWORK_DNS_SERVER = os.getenv(
    "NETWORK_DNS_SERVER",
    "",
).strip()

NETWORK_DNS_TIMEOUT_SECONDS = float(
    os.getenv(
        "NETWORK_DNS_TIMEOUT_SECONDS",
        "1.5",
    )
)


# ---------------------------------------------------------------------------
# Configuration validation
# ---------------------------------------------------------------------------

if NETWORK_MAX_SCAN_HOSTS <= 0:
    raise RuntimeError("NETWORK_MAX_SCAN_HOSTS must be greater than 0.")

if NETWORK_SCAN_CONCURRENCY <= 0:
    raise RuntimeError("NETWORK_SCAN_CONCURRENCY must be greater than 0.")

if NETWORK_PROBE_TIMEOUT_SECONDS <= 0:
    raise RuntimeError("NETWORK_PROBE_TIMEOUT_SECONDS must be greater than 0.")

if not NETWORK_SCAN_RATE_LIMIT:
    raise RuntimeError("NETWORK_SCAN_RATE_LIMIT must not be empty.")

if NETWORK_DNS_TIMEOUT_SECONDS <= 0:
    raise RuntimeError("NETWORK_DNS_TIMEOUT_SECONDS must be greater than 0.")

if NETWORK_DNS_SERVER:
    try:
        IPv4Address(NETWORK_DNS_SERVER)
    except ValueError as exc:
        raise RuntimeError("NETWORK_DNS_SERVER must be a valid IPv4 address.") from exc

PULSEWATCH_HOST_IP = os.getenv(
    "PULSEWATCH_HOST_IP",
    "",
).strip()

if PULSEWATCH_HOST_IP:
    try:
        IPv4Address(PULSEWATCH_HOST_IP)
    except ValueError as exc:
        raise RuntimeError("PULSEWATCH_HOST_IP must be a valid IPv4 address.") from exc
