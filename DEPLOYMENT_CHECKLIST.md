# Phase 3 Deployment Checklist

## ✅ Pre-Deployment Setup (COMPLETED)

- [x] Created new branch `phase3-testm` from `phase-2/test-5`
- [x] Updated MongoDB connection to MongoDB Atlas
- [x] Updated CORS settings to allow all origins
- [x] Created environment configuration for frontend
- [x] Updated frontend services to use environment config
- [x] Created OpenShift YAML files:
  - [x] backend-buildconfig.yaml
  - [x] backend-deployment.yaml
  - [x] frontend-buildconfig.yaml
  - [x] frontend-deployment.yaml
- [x] Created deployment documentation
- [x] Committed and pushed changes to GitHub

## 📝 Deployment Steps (TO DO)

### Step 1: OpenShift Login
- [ ] Sign up for OpenShift (Red Hat Developer Sandbox or other)
- [ ] Install `oc` CLI tool
- [ ] Login to OpenShift: `oc login --token=... --server=...`
- [ ] Create project: `oc new-project eventplanner`

### Step 2: Backend Deployment
- [ ] Apply backend BuildConfig: `oc apply -f backend-buildconfig.yaml`
- [ ] Start backend build: `oc start-build backend-build --follow`
- [ ] Edit `backend-deployment.yaml` - Replace `YOUR_PROJECT_NAME` with `eventplanner`
- [ ] Apply backend deployment: `oc apply -f backend-deployment.yaml`
- [ ] Verify backend pod is running: `oc get pods`
- [ ] Get backend URL: `oc get route backend-route`
- [ ] **SAVE BACKEND URL**: _________________________________

### Step 3: Frontend Configuration Update
- [ ] Run: `.\update-backend-url.ps1 -BackendUrl "YOUR_BACKEND_URL"`
- [ ] Verify `frontend/eventplanner-frontend/src/environments/environment.ts` is updated
- [ ] Commit changes: `git add . && git commit -m "Update frontend with OpenShift backend URL"`
- [ ] Push to GitHub: `git push origin phase3-testm`

### Step 4: Frontend Deployment
- [ ] Apply frontend BuildConfig: `oc apply -f frontend-buildconfig.yaml`
- [ ] Start frontend build: `oc start-build frontend-build --follow`
- [ ] Edit `frontend-deployment.yaml` - Replace `YOUR_PROJECT_NAME` with `eventplanner`
- [ ] Apply frontend deployment: `oc apply -f frontend-deployment.yaml`
- [ ] Verify frontend pod is running: `oc get pods`
- [ ] Get frontend URL: `oc get route frontend-route`
- [ ] **SAVE FRONTEND URL**: _________________________________

### Step 5: Testing
- [ ] Open frontend URL in browser
- [ ] Test user registration
- [ ] Test user login
- [ ] Test event creation
- [ ] Test event viewing
- [ ] Verify data persists in MongoDB Atlas

## 📸 Phase 3 Deliverables

### Deliverable 1: App Dynamic URLs
- [ ] Frontend URL: _________________________________
- [ ] Backend URL: _________________________________

### Deliverable 2: Infrastructure Screenshot
- [ ] Go to OpenShift Console → Developer → Topology
- [ ] Take screenshot showing:
  - [ ] Frontend deployment
  - [ ] Backend deployment
  - [ ] Services
  - [ ] Routes
  - [ ] Connections between components
- [ ] Save screenshot as: `screenshots/topology-view.png`

### Deliverable 3: GitHub Repository Screenshot
- [ ] Go to OpenShift Console → Builds → BuildConfigs
- [ ] Click on `backend-build` or `frontend-build`
- [ ] Take screenshot showing:
  - [ ] GitHub repository URL: https://github.com/salmatarekx/EventPlanner.git
  - [ ] Branch: phase3-testm
- [ ] Save screenshot as: `screenshots/github-repo-config.png`

## 🔍 Final Verification

- [ ] All pods are in "Running" status: `oc get pods`
- [ ] All routes are accessible: `oc get routes`
- [ ] Backend logs show no errors: `oc logs -f deployment/backend`
- [ ] Frontend logs show no errors: `oc logs -f deployment/frontend`
- [ ] Application is fully functional
- [ ] All three deliverables are ready for submission

## 📦 Submission Package

Create a folder with:
- [ ] Document with Frontend URL
- [ ] Document with Backend URL
- [ ] Screenshot: Topology view (infrastructure)
- [ ] Screenshot: GitHub repository configuration
- [ ] (Optional) Additional screenshots of working application

## 🆘 Troubleshooting Reference

If you encounter issues, check:
1. Pod status: `oc get pods`
2. Pod details: `oc describe pod POD_NAME`
3. Pod logs: `oc logs POD_NAME`
4. Build status: `oc get builds`
5. Build logs: `oc logs build/BUILD_NAME`

To rebuild:
```bash
oc start-build backend-build --follow
oc start-build frontend-build --follow
```

## 📚 Documentation Files

- **QUICK_REFERENCE.md** - Quick command reference
- **OPENSHIFT_DEPLOYMENT_GUIDE.md** - Detailed step-by-step guide
- **DEPLOYMENT_SUMMARY.md** - Overview and architecture
- **THIS FILE** - Deployment checklist

---

**Good luck with your deployment! 🚀**

Remember: Take your time, follow each step carefully, and don't hesitate to check the logs if something doesn't work as expected.
