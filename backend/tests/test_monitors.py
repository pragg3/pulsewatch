def test_create_monitor(client):
    response = client.post(
        "/monitors",
        json={
            "name": "Google",
            "url": "https://google.com",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Google"
    assert data["url"] == "https://google.com/"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


def test_list_monitors(client):
    client.post(
        "/monitors",
        json={
            "name": "GitHub",
            "url": "https://github.com",
        },
    )

    response = client.get("/monitors")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "GitHub"


def test_duplicate_monitor_returns_409(client):
    payload = {
        "name": "Google",
        "url": "https://google.com",
    }

    first_response = client.post("/monitors", json=payload)
    second_response = client.post("/monitors", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "A monitor with this URL already exists"
    }
