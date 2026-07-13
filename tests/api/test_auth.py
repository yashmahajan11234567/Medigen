def test_register_login_and_read_current_user(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "MediGen Tester",
            "email": "tester@example.com",
            "password": "Password123",
        },
    )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == "tester@example.com"

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "tester@example.com", "password": "Password123"},
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["full_name"] == "MediGen Tester"

