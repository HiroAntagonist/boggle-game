#!/usr/bin/env python3
"""
Script to test Sentry alerts by triggering errors in production.

This will:
1. Register/login a test user
2. Call the /test/sentry endpoint multiple times
3. Trigger the following alerts:
   - New Issue alert (first error)
   - Error Rate Spike alert (>10 errors in 1 minute)
"""
import requests
import time
import sys

BASE_URL = "https://boggle-game-ar.fly.dev"
TEST_EMAIL = "sentry-test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_DISPLAY_NAME = "Sentry Tester"

def register_or_login():
    """Register a test user or login if already exists."""
    # Try to register
    print(f"🔐 Registering test user: {TEST_EMAIL}")
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "display_name": TEST_DISPLAY_NAME
    })

    if response.status_code == 201:
        print("✅ User registered successfully")
        return response.json()["access_token"]
    elif response.status_code == 400 and "already registered" in response.text:
        # User exists, try to login
        print("ℹ️  User already exists, logging in...")
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            print("✅ Logged in successfully")
            return response.json()["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code} {response.text}")
            sys.exit(1)
    else:
        print(f"❌ Registration failed: {response.status_code} {response.text}")
        sys.exit(1)

def trigger_sentry_error(token, error_num):
    """Call the /test/sentry endpoint to trigger an error."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/test/sentry", headers=headers)

    # We expect this to fail with 500 (ValueError)
    if response.status_code == 500:
        print(f"✅ Error {error_num} triggered successfully (status: 500)")
        return True
    else:
        print(f"⚠️  Unexpected response: {response.status_code} {response.text}")
        return False

def main():
    print("🧪 Sentry Alert Testing Script")
    print("=" * 50)

    # Get auth token
    token = register_or_login()
    print()

    # Trigger first error (should create New Issue alert)
    print("🚨 Triggering first error (should trigger 'New Issue' alert)...")
    trigger_sentry_error(token, 1)
    print()

    # Wait a bit for Sentry to process
    print("⏳ Waiting 3 seconds for Sentry to process...")
    time.sleep(3)
    print()

    # Trigger multiple errors quickly to spike the error rate
    print("🚨 Triggering 15 more errors to spike error rate (should trigger 'Error Rate Spike' alert)...")
    for i in range(2, 17):
        trigger_sentry_error(token, i)
        time.sleep(0.1)  # Small delay between requests

    print()
    print("=" * 50)
    print("✅ Test complete!")
    print()
    print("Check your Slack #Drishti Labs channel for alerts:")
    print("1. 'New Issue' alert (first error)")
    print("2. 'Error Rate Spike' alert (>10 errors in 1 minute)")
    print()
    print("Also check Sentry dashboard at: https://sentry.io/organizations/YOUR_ORG/issues/")

if __name__ == "__main__":
    main()
