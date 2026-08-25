import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://pulsewatch:pulsewatch@localhost:5432/pulsewatch",
)

# ---------------------------------------------------------------------------
# Network discovery
# ---------------------------------------------------------------------------

NETWORK_DISCOVERY_ENABLED = (
    os.getenv("NETWORK_DISCOVERY_ENABLED", "false").lower() == "true"
)

# Additional protection for the network-discovery endpoints.
#
# Do NOT put the real value in source control.
NETWORK_DISCOVERY_KEY = os.getenv(
    "NETWORK_DISCOVERY_KEY",
    "",
)

# Maximum number of addresses accepted in one request.
NETWORK_MAX_SCAN_HOSTS = int(
    os.getenv("NETWORK_MAX_SCAN_HOSTS", "512")
)

# Maximum number of hosts inspected concurrently.
NETWORK_SCAN_CONCURRENCY = int(
    os.getenv("NETWORK_SCAN_CONCURRENCY", "32")
)

# Timeout for individual TCP reachability attempts.
NETWORK_PROBE_TIMEOUT_SECONDS = float(
    os.getenv("NETWORK_PROBE_TIMEOUT_SECONDS", "0.8")
)

# Maximum number of discovery requests per client.
NETWORK_SCAN_RATE_LIMIT = os.getenv(
    "NETWORK_SCAN_RATE_LIMIT",
    "5/minute",
)

# Only trust X-Forwarded-For when PulseWatch is deployed behind
# its own trusted reverse proxy.
NETWORK_TRUST_PROXY_HEADERS = (
    os.getenv("NETWORK_TRUST_PROXY_HEADERS", "false").lower() == "true"
)