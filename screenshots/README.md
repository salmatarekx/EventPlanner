# Screenshots Directory

This directory is for storing Phase 3 deliverable screenshots.

## Required Screenshots

### 1. topology-view.png
- **Source**: OpenShift Console → Developer → Topology
- **Content**: Shows infrastructure and connections between:
  - Frontend deployment
  - Backend deployment
  - Services
  - Routes
  - Visual connections between all components

### 2. github-repo-config.png
- **Source**: OpenShift Console → Builds → BuildConfigs → (backend-build or frontend-build)
- **Content**: Shows:
  - GitHub repository URL: https://github.com/salmatarekx/EventPlanner.git
  - Branch: phase3-testm
  - Build source configuration

## How to Take Screenshots

### For Topology View:
1. Login to OpenShift Web Console
2. Switch to **Developer** perspective (top-left dropdown)
3. Click on **Topology** in the left sidebar
4. Wait for all components to load
5. Take a full screenshot (use Windows + Shift + S or Snipping Tool)
6. Save as `topology-view.png` in this directory

### For GitHub Repo Configuration:
1. In OpenShift Web Console, stay in **Developer** perspective
2. Click on **Builds** in the left sidebar
3. Click on **BuildConfigs** tab
4. Click on either `backend-build` or `frontend-build`
5. Scroll to the **Source** section
6. Take a screenshot showing the Git repository details
7. Save as `github-repo-config.png` in this directory

## Optional Screenshots

You may also want to capture:
- `running-application.png` - Screenshot of the working application
- `pods-running.png` - Screenshot of `oc get pods` showing all pods running
- `routes.png` - Screenshot of `oc get routes` showing the URLs

---

**Note**: Make sure screenshots are clear and readable before submission!
