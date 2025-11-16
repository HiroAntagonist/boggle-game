#!/bin/bash
#
# Script to test Sentry alerts by triggering errors in production.
#
# This will:
# 1. Register/login a test user
# 2. Call the /test/sentry endpoint multiple times
# 3. Trigger the following alerts:
#    - New Issue alert (first error)
#    - Error Rate Spike alert (>10 errors in 1 minute)

BASE_URL="https://boggle-game-ar.fly.dev"
TEST_EMAIL="sentry-test@example.com"
TEST_PASSWORD="TestPassword123!"
TEST_DISPLAY_NAME="Sentry Tester"

echo "🧪 Sentry Alert Testing Script"
echo "=================================================="
echo ""

# Try to register user
echo "🔐 Registering test user: $TEST_EMAIL"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"display_name\":\"$TEST_DISPLAY_NAME\"}")

# Extract token if successful
TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('access_token', ''))" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo "✅ User registered successfully"
else
    # User exists, try to login
    echo "ℹ️  User already exists, logging in..."
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
      -H "Content-Type: application/json" \
      -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    echo "✅ Logged in successfully"
fi

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get auth token"
    exit 1
fi

echo ""

# Trigger first error
echo "🚨 Triggering first error (should trigger 'New Issue' alert)..."
HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/test/sentry" \
  -H "Authorization: Bearer $TOKEN")
if [ "$HTTP_CODE" = "500" ]; then
    echo "✅ Error 1 triggered (HTTP 500 as expected)"
else
    echo "⚠️  Unexpected HTTP code: $HTTP_CODE"
fi
echo ""

# Wait for Sentry to process
echo "⏳ Waiting 3 seconds for Sentry to process..."
sleep 3
echo ""

# Trigger multiple errors to spike the rate
echo "🚨 Triggering 15 more errors to spike error rate (should trigger 'Error Rate Spike' alert)..."
for i in {2..16}; do
    curl -s -o /dev/null "$BASE_URL/test/sentry" \
      -H "Authorization: Bearer $TOKEN"
    echo "✅ Error $i triggered"
    sleep 0.1
done

echo ""
echo "=================================================="
echo "✅ Test complete! 16 errors triggered in total."
echo ""
echo "📊 Expected results:"
echo "  1. New Issue alert → Slack #Drishti Labs (first error)"
echo "  2. Error Rate Spike alert → Slack #Drishti Labs (>10 errors in 1 min)"
echo ""
echo "🔍 Check Sentry dashboard for the new issue with:"
echo "  - Error: ValueError: Sentry test error triggered by $TEST_EMAIL"
echo "  - User context: $TEST_EMAIL"
echo "  - Release tag: boggle@<git-sha>"
