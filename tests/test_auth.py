# tests/test_auth.py
import pytest
from services.users import hash_password
from data.models import User

# Note: Adjust the URL prefix if your auth_route in main.py 
# is mounted with a prefix (e.g., "/auth")
LOGIN_URL = "/auth/login" 

def test_login_success(client, db_session):
    """
    Test that a valid user can login and receive a cookie.
    """
    # 1. ARRANGE: Create a user in the test database
    password = "securePassword123"
    hashed = hash_password(password)
    
    new_user = User(
        username="test_admin",
        hashed_password=hashed,
        role="admin",
        display_name="Test Admin",
        disabled=False
    )
    db_session.add(new_user)
    db_session.commit()

    # 2. ACT: Attempt to login
    # IMPORTANT: Use 'data' for Form(...), not 'json'
    payload = {
        "username": "test_admin", 
        "password": password,
        "remember_me": True
    }
    response = client.post(LOGIN_URL, data=payload)

    # 3. ASSERT: Check status and content
    assert response.status_code == 200
    assert response.json() == {"status": "success", "role": "admin"}

    # 4. ASSERT: Check Cookie
    assert "access_token" in response.cookies
    # Optional: Check cookie attributes (httponly is hard to check via TestClient usually, 
    # but presence is the main thing)

def test_login_bad_credentials(client, db_session):
    """
    Test that login fails with wrong password.
    """
    # 1. ARRANGE
    new_user = User(
        username="test_user",
        hashed_password=hash_password("correct_password"),
        role="user"
    )
    db_session.add(new_user)
    db_session.commit()

    # 2. ACT
    payload = {
        "username": "test_user", 
        "password": "WRONG_PASSWORD"
    }
    response = client.post(LOGIN_URL, data=payload)

    # 3. ASSERT
    assert response.status_code == 401
    assert "access_token" not in response.cookies

def test_login_disabled_user(client, db_session):
    """
    Test that a disabled user cannot login.
    """
    # 1. ARRANGE
    new_user = User(
        username="banned_user",
        hashed_password=hash_password("password"),
        role="user",
        disabled=True # <--- User is disabled
    )
    db_session.add(new_user)
    db_session.commit()

    # 2. ACT
    payload = {
        "username": "banned_user", 
        "password": "password"
    }
    response = client.post(LOGIN_URL, data=payload)

    # 3. ASSERT
    assert response.status_code == 401