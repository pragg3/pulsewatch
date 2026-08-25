from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.network import DiscoveredHost


@patch(
    "backend.app.api.routes.network.discover_hosts",
    new_callable=AsyncMock,
)
def test_discover_private_range(
    mock_discover_hosts,
    client,
):
    mock_discover_hosts.return_value = [
        DiscoveredHost(
            ip="192.168.50.10",
            hostname="server-one.internal",
            reachable=True,
        ),
        DiscoveredHost(
            ip="192.168.50.12",
            hostname="server-two.internal",
            reachable=True,
        ),
    ]

    response = client.post(
        "/network/discover",
        json={
            "start_ip": "192.168.50.10",
            "end_ip": "192.168.50.20",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["start_ip"] == "192.168.50.10"
    assert data["end_ip"] == "192.168.50.20"
    assert data["requested_hosts"] == 11
    assert data["reachable_hosts"] == 2
    assert len(data["hosts"]) == 2

    assert data["hosts"][0]["ip"] == "192.168.50.10"
    assert data["hosts"][0]["hostname"] == (
        "server-one.internal"
    )
    assert data["hosts"][0]["reachable"] is True

    mock_discover_hosts.assert_awaited_once()


def test_network_info(client):
    response = client.get("/network/info")

    assert response.status_code == 200

    data = response.json()

    assert "client_ip" in data
    assert "scanner_ip" in data

    # We deliberately do NOT assert a particular real IP.
    # The application must work on any installation/network.


def test_network_info_requires_discovery_key():
    with TestClient(app) as unauthenticated_client:
        response = unauthenticated_client.get(
            "/network/info"
        )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Network discovery authentication required."
    )


def test_network_info_rejects_wrong_discovery_key():
    with TestClient(
        app,
        headers={
            "X-PulseWatch-Discovery-Key": "wrong-key",
        },
    ) as wrong_client:
        response = wrong_client.get(
            "/network/info"
        )

    assert response.status_code == 403

    assert response.json()["detail"] == (
        "Invalid network discovery credentials."
    )


def test_discover_rejects_reversed_range(client):
    response = client.post(
        "/network/discover",
        json={
            "start_ip": "192.168.50.20",
            "end_ip": "192.168.50.10",
        },
    )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "end_ip must be greater than or equal to start_ip."
    )


def test_discover_rejects_range_over_limit(client):
    response = client.post(
        "/network/discover",
        json={
            "start_ip": "192.168.1.1",
            "end_ip": "192.168.3.10",
        },
    )

    assert response.status_code == 422

    assert "Maximum allowed" in response.json()["detail"]


def test_discover_rejects_invalid_ipv4(client):
    response = client.post(
        "/network/discover",
        json={
            "start_ip": "not-an-ip",
            "end_ip": "192.168.1.10",
        },
    )

    assert response.status_code == 422


def test_discover_rejects_public_range(client):
    response = client.post(
        "/network/discover",
        json={
            "start_ip": "8.8.8.1",
            "end_ip": "8.8.8.10",
        },
    )

    assert response.status_code == 403

    assert response.json()["detail"] == (
        "Public or non-private addresses are not "
        "permitted for LAN discovery."
    )


def test_discover_rejects_loopback_range(client):
    response = client.post(
        "/network/discover",
        json={
            "start_ip": "127.0.0.1",
            "end_ip": "127.0.0.10",
        },
    )

    assert response.status_code == 403


def test_discover_rejects_link_local_range(client):
    response = client.post(
        "/network/discover",
        json={
            "start_ip": "169.254.1.1",
            "end_ip": "169.254.1.10",
        },
    )

    assert response.status_code == 403


@patch(
    "backend.app.api.routes.network.discover_hosts",
    new_callable=AsyncMock,
)
def test_discover_accepts_10_private_range(
    mock_discover_hosts,
    client,
):
    mock_discover_hosts.return_value = []

    response = client.post(
        "/network/discover",
        json={
            "start_ip": "10.50.20.1",
            "end_ip": "10.50.20.10",
        },
    )

    assert response.status_code == 200

    mock_discover_hosts.assert_awaited_once()


@patch(
    "backend.app.api.routes.network.discover_hosts",
    new_callable=AsyncMock,
)
def test_discover_accepts_172_private_range(
    mock_discover_hosts,
    client,
):
    mock_discover_hosts.return_value = []

    response = client.post(
        "/network/discover",
        json={
            "start_ip": "172.20.10.1",
            "end_ip": "172.20.10.10",
        },
    )

    assert response.status_code == 200

    mock_discover_hosts.assert_awaited_once()