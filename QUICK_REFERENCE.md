# 🚀 OpenShift Deployment - Quick Reference

## ⚡ Quick Start Commands

### 1. Login to OpenShift
```bash
oc login --token=YOUR_TOKEN --server=YOUR_SERVER_URL
oc new-project eventplanner
```

### 2. Deploy Backend
```bash
oc apply -f backend-buildconfig.yaml
oc start-build backend-build --follow
# Edit backend-deployment.yaml: Replace YOUR_PROJECT_NAME with eventplanner
oc apply -f backend-deployment.yaml
oc get route backend-route
```

### 3. Update Frontend with Backend URL
```powershell
# Copy the backend URL from step 2, then run:
.\update-backend-url.ps1 -BackendUrl "https://YOUR-BACKEND-URL"
git add .
git commit -m "Update frontend with OpenShift backend URL"
git push origin phase3-testm
```

### 4. Deploy Frontend
```bash
oc apply -f frontend-buildconfig.yaml
oc start-build frontend-build --follow
# Edit frontend-deployment.yaml: Replace YOUR_PROJECT_NAME with eventplanner
oc apply -f frontend-deployment.yaml
oc get route frontend-route
```

### 5. Get Your URLs
```bash
oc get routes
```

## 📸 Screenshots Needed

### Screenshot 1: Topology View
- OpenShift Console → Developer → Topology
- Shows: Deployments, Services, Routes, Connections

### Screenshot 2: GitHub Repo URL
- OpenShift Console → Builds → BuildConfigs → backend-build
- Shows: GitHub URL and branch name

## ✅ Verification
```bash
oc get pods              # All should be Running
oc logs -f deployment/backend
oc logs -f deployment/frontend
```

## 🔧 Troubleshooting
```bash
oc describe pod POD_NAME
oc logs POD_NAME
oc start-build backend-build --follow    # Rebuild
oc start-build frontend-build --follow   # Rebuild
```

## 📋 Deliverables Checklist
- [ ] Frontend URL (from `oc get routes`)
- [ ] Backend URL (from `oc get routes`)
- [ ] Topology screenshot
- [ ] BuildConfig screenshot showing GitHub URL

---
For detailed instructions, see: **OPENSHIFT_DEPLOYMENT_GUIDE.md**
