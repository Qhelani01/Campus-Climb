#!/bin/bash
# Script to create admin user on Vercel deployment
# Usage: ./setup_vercel_admin.sh <setup_token> <email> <password> [first_name] [last_name]

if [ $# -lt 3 ]; then
    echo "Usage: $0 <setup_token> <email> <password> [first_name] [last_name]"
    echo "Example: $0 my-secret-token qhestoemoyo@gmail.com admin123 Qhelani Moyo"
    exit 1
fi

SETUP_TOKEN=$1
EMAIL=$2
PASSWORD=$3
FIRST_NAME=${4:-Admin}
LAST_NAME=${5:-User}

VERCEL_URL="https://campus-climb.vercel.app"

echo "Setting up admin user on Vercel..."
echo "Email: $EMAIL"
echo "Name: $FIRST_NAME $LAST_NAME"

curl -X POST "$VERCEL_URL/api/setup/admin" \
  -H "Content-Type: application/json" \
  -H "X-Setup-Token: $SETUP_TOKEN" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"first_name\": \"$FIRST_NAME\",
    \"last_name\": \"$LAST_NAME\"
  }" | jq '.'

echo ""
echo "Done! Try logging in with the credentials above."
