#!/bin/bash

# Script to update frontend environment with OpenShift backend URL
# Usage: ./update-backend-url.sh <BACKEND_URL>

if [ -z "$1" ]; then
    echo "Error: Backend URL is required"
    echo "Usage: ./update-backend-url.sh <BACKEND_URL>"
    echo "Example: ./update-backend-url.sh https://backend-route-eventplanner.apps.cluster.com"
    exit 1
fi

BACKEND_URL=$1

# Update the production environment file
cat > frontend/eventplanner-frontend/src/environments/environment.ts << EOF
export const environment = {
  production: true,
  apiUrl: '${BACKEND_URL}'
};
EOF

echo "✅ Updated environment.ts with backend URL: ${BACKEND_URL}"
echo ""
echo "Next steps:"
echo "1. Commit and push the changes:"
echo "   git add ."
echo "   git commit -m 'Update frontend with OpenShift backend URL'"
echo "   git push origin phase3-testm"
echo ""
echo "2. Rebuild the frontend in OpenShift:"
echo "   oc start-build frontend-build --follow"
