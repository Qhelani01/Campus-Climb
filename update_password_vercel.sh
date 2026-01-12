#!/bin/bash
# Script to update admin password using Vercel setup endpoint
# Usage: ./update_password_vercel.sh <setup_token>

if [ -z "$1" ]; then
    echo "Usage: ./update_password_vercel.sh <setup_token>"
    echo "Example: ./update_password_vercel.sh my-secret-token-12345"
    echo ""
    echo "First, set SETUP_TOKEN in Vercel environment variables, then redeploy."
    exit 1
fi

SETUP_TOKEN=$1
VERCEL_URL="https://campus-climb.vercel.app"

echo "Updating admin password on Vercel..."
echo "Email: qhestoemoyo@gmail.com"
echo "Password: admin123"
echo ""

curl -X POST "$VERCEL_URL/api/setup/admin" \
  -H "Content-Type: application/json" \
  -H "X-Setup-Token: $SETUP_TOKEN" \
  -d '{
    "email": "qhestoemoyo@gmail.com",
    "password": "admin123",
    "first_name": "Qhelani",
    "last_name": "Moyo"
  }' | python3 -m json.tool 2>/dev/null || cat

echo ""
echo "Done! Try logging in now."
