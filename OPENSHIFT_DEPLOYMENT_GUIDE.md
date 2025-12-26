# EventPlanner - OpenShift Deployment Guide

## Prerequisites
- OpenShift account (you can use Red Hat OpenShift Developer Sandbox: https://developers.redhat.com/developer-sandbox)
- oc CLI installed (OpenShift Command Line Interface)
- Git repository pushed to GitHub with branch `phase3-testm`

## Phase 3: Deployment Steps

### Step 1: Login to OpenShift

1. Go to your OpenShift web console
2. Click on your username (top right) → "Copy login command"
3. Click "Display Token"
4. Copy the `oc login` command and run it in your terminal:

```bash
oc login --token=YOUR_TOKEN --server=YOUR_SERVER_URL
```

### Step 2: Create a New Project

```bash
oc new-project eventplanner
```

Or if the project already exists:
```bash
oc project eventplanner
```

### Step 3: Push Your Code to GitHub

Make sure all your changes are committed and pushed to the `phase3-testm` branch:

```bash
git add .
git commit -m "Prepare for OpenShift deployment with MongoDB Atlas"
git push origin phase3-testm
```

### Step 4: Deploy Backend

#### 4.1 Create Backend BuildConfig and ImageStream
```bash
oc apply -f backend-buildconfig.yaml
```

#### 4.2 Start Backend Build
```bash
oc start-build backend-build --follow
```

Wait for the build to complete. This will:
- Pull your code from GitHub
- Build the Docker image using your Dockerfile
- Push the image to OpenShift's internal registry

#### 4.3 Deploy Backend Application
Before deploying, update the `backend-deployment.yaml` file:
- Replace `YOUR_PROJECT_NAME` with `eventplanner` (or your actual project name)

Then apply:
```bash
oc apply -f backend-deployment.yaml
```

#### 4.4 Verify Backend Deployment
```bash
oc get pods
oc logs -f deployment/backend
```

#### 4.5 Get Backend URL
```bash
oc get route backend-route
```

The URL will be something like: `https://backend-route-eventplanner.apps.YOUR_CLUSTER.com`

### Step 5: Update Frontend to Use Backend URL

Before deploying the frontend, you need to update the Angular app to use the OpenShift backend URL.

1. Get your backend route URL from Step 4.5
2. Update the frontend environment files with this URL
3. Commit and push the changes:

```bash
git add .
git commit -m "Update frontend to use OpenShift backend URL"
git push origin phase3-testm
```

### Step 6: Deploy Frontend

#### 6.1 Create Frontend BuildConfig and ImageStream
```bash
oc apply -f frontend-buildconfig.yaml
```

#### 6.2 Start Frontend Build
```bash
oc start-build frontend-build --follow
```

#### 6.3 Deploy Frontend Application
Before deploying, update the `frontend-deployment.yaml` file:
- Replace `YOUR_PROJECT_NAME` with `eventplanner` (or your actual project name)

Then apply:
```bash
oc apply -f frontend-deployment.yaml
```

#### 6.4 Verify Frontend Deployment
```bash
oc get pods
oc logs -f deployment/frontend
```

#### 6.5 Get Frontend URL
```bash
oc get route frontend-route
```

The URL will be something like: `https://frontend-route-eventplanner.apps.YOUR_CLUSTER.com`

### Step 7: Verify Complete Deployment

1. **Check all pods are running:**
```bash
oc get pods
```

All pods should show `Running` status.

2. **Check all routes:**
```bash
oc get routes
```

3. **Test the application:**
- Open the frontend URL in your browser
- Test user registration, login, and event creation
- Verify data is being stored in MongoDB Atlas

### Step 8: Get Screenshots for Deliverables

#### Screenshot 1: Infrastructure and Connections
In OpenShift web console:
1. Go to **Topology** view (Developer perspective)
2. This shows all your deployments, services, and routes
3. Take a full screenshot showing:
   - Frontend deployment
   - Backend deployment
   - Services connecting them
   - Routes (external access)
   - The visual connections between components

#### Screenshot 2: GitHub Repository URL
In OpenShift web console:
1. Go to **Builds** → **BuildConfigs**
2. Click on `backend-build` or `frontend-build`
3. Scroll to the **Source** section
4. Take a screenshot showing the GitHub repository URL: `https://github.com/salmatarekx/EventPlanner.git`
5. Also show the branch: `phase3-testm`

Alternatively:
```bash
oc describe bc/backend-build | grep -A 5 "Source"
oc describe bc/frontend-build | grep -A 5 "Source"
```

### Step 9: Phase 3 Deliverables Checklist

✅ **App Dynamic URL on OpenShift:**
- Frontend URL: (Get from `oc get route frontend-route`)
- Backend URL: (Get from `oc get route backend-route`)

✅ **Full screenshot of infrastructure and connections:**
- Go to OpenShift Console → Topology view
- Screenshot showing all deployments, services, and routes

✅ **Full screenshot showing GitHub repo URL:**
- Go to OpenShift Console → Builds → BuildConfigs
- Screenshot showing the GitHub repository URL in the build configuration

## Troubleshooting

### If pods are not starting:
```bash
oc get pods
oc describe pod POD_NAME
oc logs POD_NAME
```

### If build fails:
```bash
oc get builds
oc logs build/BUILD_NAME
```

### To rebuild:
```bash
oc start-build backend-build --follow
oc start-build frontend-build --follow
```

### To delete and redeploy:
```bash
oc delete -f backend-deployment.yaml
oc delete -f frontend-deployment.yaml
oc apply -f backend-deployment.yaml
oc apply -f frontend-deployment.yaml
```

## Important Notes

1. **MongoDB Atlas Connection:** Your app is now using MongoDB Atlas (cloud database) instead of local MongoDB
2. **Environment Variables:** Secrets are stored in OpenShift Secrets (backend-secrets)
3. **HTTPS:** All routes use HTTPS by default in OpenShift
4. **Scaling:** You can scale your application using `oc scale deployment/backend --replicas=3`

## Monitoring

View application logs:
```bash
oc logs -f deployment/backend
oc logs -f deployment/frontend
```

View resource usage:
```bash
oc adm top pods
```

## Success Criteria

Your deployment is successful when:
- ✅ Both frontend and backend pods are running
- ✅ You can access the frontend URL in a browser
- ✅ You can register/login users
- ✅ You can create and view events
- ✅ Data persists in MongoDB Atlas
- ✅ All three deliverables are ready for submission
