# Script to update frontend environment with OpenShift backend URL
# Usage: .\update-backend-url.ps1 -BackendUrl "https://backend-route-eventplanner.apps.cluster.com"

param(
    [Parameter(Mandatory=$true)]
    [string]$BackendUrl
)

$envFilePath = "frontend\eventplanner-frontend\src\environments\environment.ts"

$content = @"
export const environment = {
  production: true,
  apiUrl: '$BackendUrl'
};
"@

Set-Content -Path $envFilePath -Value $content

Write-Host "✅ Updated environment.ts with backend URL: $BackendUrl" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Commit and push the changes:"
Write-Host "   git add ."
Write-Host "   git commit -m 'Update frontend with OpenShift backend URL'"
Write-Host "   git push origin phase3-testm"
Write-Host ""
Write-Host "2. Rebuild the frontend in OpenShift:"
Write-Host "   oc start-build frontend-build --follow"
