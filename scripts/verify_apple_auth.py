import requests
import sys

BASE_URL = "http://localhost:8000"

def test_delete_account():
    print("\n🧪 Testing Account Deletion Flow...")

    # 1. Register a temporary user
    email = "test_delete_1@example.com"
    password = "password123"
    print(f"  Creating user {email}...")

    reg_payload = {"email": email, "password": password, "display_name": "Delete Me"}
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
        if resp.status_code != 201 and "Email already registered" not in resp.text:
             print(f"  ❌ Registration failed: {resp.status_code} {resp.text}")
             return

        # If already exists, login
        if resp.status_code != 201:
             print("  User exists, logging in...")
    except Exception as e:
        print(f"  ❌ Failed to connect: {e}")
        return

    # 2. Login to get token
    login_payload = {"email": email, "password": password}
    resp = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    if resp.status_code != 200:
        print(f"  ❌ Login failed: {resp.status_code} {resp.text}")
        return

    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  ✅ Logged in")

    # 3. Verify user exists
    resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if resp.status_code != 200:
        print(f"  ❌ Failed to fetch profile: {resp.status_code} {resp.text}")
        return
    print("  ✅ Profile fetched")

    # 4. Delete account
    print("  Deleting account...")
    resp = requests.delete(f"{BASE_URL}/auth/me", headers=headers)
    if resp.status_code != 200:
        print(f"  ❌ Delete failed: {resp.status_code} {resp.text}")
        return

    # Check response structure
    data = resp.json()
    if "message" in data and "status" in data:
        print(f"  ✅ Delete response valid: {data}")
    else:
        print(f"  ❌ Unexpected response format: {data}")

    # 5. Verify user is GONE (login should fail or auth/me should fail)
    print("  Verifying deletion...")
    resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if resp.status_code == 401:
        print("  ✅ Verified: Token is now invalid (401)")
    else:
        print(f"  ❌ User might still exist? Status: {resp.status_code}")

    # Try login again
    resp = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    if resp.status_code == 401:
        print("  ✅ Verified: Login fails (401)")
    else:
        print(f"  ❌ Login still possible? Status: {resp.status_code}")


def test_apple_auth_endpoint():
    print("\n🧪 Testing Apple Auth Endpoint (Structure)...")
    # We send a dummy token. We expect 401 or 400, but NOT 404 (endpoint missing) or 500 (crash)

    payload = {"id_token": "invalid.token.here"}
    resp = requests.post(f"{BASE_URL}/auth/apple", json=payload)

    if resp.status_code == 401:
        print(f"  ✅ Endpoint reachable and handled invalid token correctly (401).")
        print(f"  Response: {resp.json().get('detail')}")
    elif resp.status_code == 500:
         print(f"  ❌ Server error (500). Validate imports/dependencies.")
         print(resp.text)
    elif resp.status_code == 404:
         print(f"  ❌ Endpoint not found (404). Check routing.")
    else:
         print(f"  ⚠️ Unexpected status: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    test_delete_account()
    test_apple_auth_endpoint()
