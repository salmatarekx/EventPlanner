# EventPlanner - OpenShift Deployment Summary

## 📋 Phase 3 Overview

This document summarizes the OpenShift deployment setup for the EventPlanner application.

## 🏗️ Architecture

### Application Stack
- **Frontend**: Angular 17+ (served with Nginx)
- **Backend**: Python FastAPI
- **Database**: MongoDB Atlas (Cloud)

### OpenShift Components
- **BuildConfigs**: Build Docker images from GitHub repository
- **ImageStreams**: Store built container images
- **Deployments**: Run application containers
- **Services**: Internal networking between components
- **Routes**: External HTTPS access to applications
- **Secrets**: Store sensitive data (MongoDB URI, API keys)

## 📁 Files Created

### OpenShift Configuration Files
1. **backend-buildconfig.yaml** - Builds backend Docker image from GitHub
2. **backend-deployment.yaml** - Deploys backend with MongoDB Atlas connection
3. **frontend-buildconfig.yaml** - Builds frontend Docker image from GitHub
4. **frontend-deployment.yaml** - Deploys frontend application

### Environment Configuration
5. **frontend/eventplanner-frontend/src/environments/environment.ts** - Production config
6. **frontend/eventplanner-frontend/src/environments/environment.development.ts** - Dev config

### Helper Scripts
7. **update-backend-url.ps1** - PowerShell script to update backend URL
8. **update-backend-url.sh** - Bash script to update backend URL

### Documentation
9. **OPENSHIFT_DEPLOYMENT_GUIDE.md** - Complete deployment instructions

## 🔄 Changes Made

### 1. Database Migration
- ✅ Updated `.env` file to use MongoDB Atlas connection string
- ✅ Changed from local MongoDB to cloud-hosted MongoDB Atlas
- ✅ Connection string: `mongodb+srv://moyasser_database_eventplanner:...@eventplanner.nl4k3zl.mongodb.net/eventplanner`

### 2. CORS Configuration
- ✅ Updated `main.py` to allow all origins (required for OpenShift dynamic URLs)

### 3. Frontend API Configuration
- ✅ Created environment configuration system
- ✅ Updated `auth.service.ts` to use environment config
- ✅ Updated `event.service.ts` to use environment config
- ✅ Supports both development (localhost) and production (OpenShift) URLs

## 🚀 Quick Deployment Steps

### Prerequisites
```bash
# Install OpenShift CLI (oc)
# Get it from: https://mirror.openshift.com/pub/openshift-v4/clients/ocp/

# Login to OpenShift
oc login --token=YOUR_TOKEN --server=YOUR_SERVER_URL
```

### 1. Create Project
```bash
oc new-project eventplanner
```

### 2. Push Code to GitHub
```bash
git add .
git commit -m "Prepare for OpenShift deployment"
git push origin phase3-testm
```

### 3. Deploy Backend
```bash
# Create build configuration
oc apply -f backend-buildconfig.yaml

# Start build
oc start-build backend-build --follow

# Deploy application (update YOUR_PROJECT_NAME first!)
oc apply -f backend-deployment.yaml

# Get backend URL
oc get route backend-route
```

### 4. Update Frontend with Backend URL
```powershell
# Windows PowerShell
.\update-backend-url.ps1 -BackendUrl "https://YOUR-BACKEND-URL"

# Or Linux/Mac
./update-backend-url.sh https://YOUR-BACKEND-URL
```

### 5. Deploy Frontend
```bash
# Commit updated frontend
git add .
git commit -m "Update frontend with OpenShift backend URL"
git push origin phase3-testm

# Create build configuration
oc apply -f frontend-buildconfig.yaml

# Start build
oc start-build frontend-build --follow

# Deploy application (update YOUR_PROJECT_NAME first!)
oc apply -f frontend-deployment.yaml

# Get frontend URL
oc get route frontend-route
```

## 📸 Phase 3 Deliverables

### 1. App Dynamic URLs
Get the URLs with:
```bash
oc get routes
```

You'll receive:
- **Frontend URL**: `https://frontend-route-eventplanner.apps.YOUR_CLUSTER.com`
- **Backend URL**: `https://backend-route-eventplanner.apps.YOUR_CLUSTER.com`

### 2. Infrastructure Screenshot
1. Go to OpenShift Web Console
2. Navigate to **Developer** perspective → **Topology**
3. Take a screenshot showing:
   - Frontend deployment (Angular + Nginx)
   - Backend deployment (Python FastAPI)
   - Services connecting them
   - Routes for external access
   - Visual connections between all components

### 3. GitHub Repository Screenshot
1. In OpenShift Web Console, go to **Builds** → **BuildConfigs**
2. Click on either `backend-build` or `frontend-build`
3. Take a screenshot showing:
   - GitHub repository URL: `https://github.com/salmatarekx/EventPlanner.git`
   - Branch: `phase3-testm`
   - Build source configuration

## 🔍 Verification Commands

```bash
# Check all pods are running
oc get pods

# Check deployments
oc get deployments

# Check services
oc get services

# Check routes
oc get routes

# View backend logs
oc logs -f deployment/backend

# View frontend logs
oc logs -f deployment/frontend

# Check build status
oc get builds
```

## 🐛 Troubleshooting

### Pods not starting
```bash
oc describe pod POD_NAME
oc logs POD_NAME
```

### Build failures
```bash
oc logs build/BUILD_NAME
```

### Rebuild application
```bash
oc start-build backend-build --follow
oc start-build frontend-build --follow
```

### Delete and redeploy
```bash
oc delete -f backend-deployment.yaml
oc delete -f frontend-deployment.yaml
oc apply -f backend-deployment.yaml
oc apply -f frontend-deployment.yaml
```

## 📝 Important Notes

1. **MongoDB Atlas**: The application now uses cloud-hosted MongoDB instead of local database
2. **HTTPS**: All routes automatically use HTTPS in OpenShift
3. **Environment Variables**: Sensitive data is stored in OpenShift Secrets
4. **Auto-scaling**: Can be configured with `oc scale deployment/backend --replicas=3`
5. **GitHub Integration**: Builds are triggered from the `phase3-testm` branch

## 🎯 Success Criteria

- ✅ Both frontend and backend pods are running
- ✅ Frontend URL is accessible in browser
- ✅ Users can register and login
- ✅ Events can be created and viewed
- ✅ Data persists in MongoDB Atlas
- ✅ All three deliverables are ready for submission

## 📚 Additional Resources

- [OpenShift Documentation](https://docs.openshift.com/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Angular Documentation](https://angular.io/docs)

## 🆘 Support

For detailed step-by-step instructions, see: **OPENSHIFT_DEPLOYMENT_GUIDE.md**

---

**Good luck with your Phase 3 deployment! 🚀**
