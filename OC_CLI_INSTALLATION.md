# ✅ OpenShift CLI (oc) Installation Complete!

## 📍 Installation Details

- **Version**: 4.20.8
- **Location**: `C:\Users\moied\oc-cli\oc.exe`
- **PATH**: Added to user environment variables

## 🚀 How to Use

### Option 1: Use Full Path (Works Immediately)
```powershell
& "$env:USERPROFILE\oc-cli\oc.exe" version
```

### Option 2: Use Short Command (After Restarting Terminal)
After you **close and reopen** your terminal/PowerShell:
```powershell
oc version
```

## 🔄 Restart Your Terminal

**IMPORTANT**: To use the `oc` command directly (without the full path), you need to:
1. Close this PowerShell/Terminal window
2. Open a new PowerShell/Terminal window
3. The `oc` command will now work from anywhere

## ✅ Verify Installation

After restarting your terminal, run:
```powershell
oc version --client
```

You should see:
```
Client Version: 4.20.8
Kustomize Version: v5.6.0
```

## 🎯 Next Steps - Login to OpenShift

### Step 1: Get Your OpenShift Cluster
Sign up for one of these:
- **Red Hat Developer Sandbox** (Free): https://developers.redhat.com/developer-sandbox
- **OpenShift Online**: https://www.openshift.com/products/online/
- Your university/organization's OpenShift cluster

### Step 2: Get Login Command
1. Go to your OpenShift Web Console
2. Click on your username (top-right corner)
3. Click **"Copy login command"**
4. Click **"Display Token"**
5. Copy the `oc login` command

### Step 3: Login
The command will look like this:
```powershell
oc login --token=sha256~XXXXXXXXXXXXX --server=https://api.cluster.openshift.com:6443
```

Paste and run it in your terminal.

## 📚 Common oc Commands

### Login & Project Management
```powershell
# Login to OpenShift
oc login --token=YOUR_TOKEN --server=YOUR_SERVER

# Create a new project
oc new-project eventplanner

# Switch to a project
oc project eventplanner

# List all projects
oc projects
```

### Deployment Commands
```powershell
# Apply YAML configuration
oc apply -f backend-deployment.yaml

# Start a build
oc start-build backend-build --follow

# Get all resources
oc get all

# Get pods
oc get pods

# Get routes (URLs)
oc get routes

# Get services
oc get services
```

### Monitoring & Debugging
```powershell
# View logs (follow mode)
oc logs -f deployment/backend

# Describe a resource
oc describe pod POD_NAME

# Get pod details
oc get pods -o wide

# Check build status
oc get builds
```

### Cleanup Commands
```powershell
# Delete a resource
oc delete -f backend-deployment.yaml

# Delete a specific pod
oc delete pod POD_NAME

# Delete entire project
oc delete project eventplanner
```

## 🔧 Troubleshooting

### If `oc` command not found after restart:
Run with full path:
```powershell
& "$env:USERPROFILE\oc-cli\oc.exe" version
```

### To manually add to PATH for current session:
```powershell
$env:Path += ";$env:USERPROFILE\oc-cli"
oc version
```

### To verify PATH is set:
```powershell
$env:Path -split ';' | Select-String "oc-cli"
```

## 📖 Documentation

- **OpenShift CLI Reference**: https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html
- **oc Command Reference**: https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/developer-cli-commands.html

## ✨ You're Ready!

Now you can proceed with the OpenShift deployment following the **DEPLOYMENT_CHECKLIST.md** file!

---

**Installation Date**: 2025-12-26  
**oc Version**: 4.20.8  
**Status**: ✅ Ready to use
