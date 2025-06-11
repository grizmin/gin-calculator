# GitHub Actions CI/CD Setup

This repository includes GitHub Actions workflows for automated Docker image building and deployment.

## 🔧 Workflows Available

### 1. **docker-simple.yml** (Recommended)
- **Automatic builds** on push/PR to master/main
- **Manual deployment** to Docker Hub via workflow dispatch
- **Integrated testing** of built images
- **Caching** for faster builds

### 2. **docker.yml** (Advanced)
- More configuration options
- Flexible Docker Hub username handling
- Detailed output information

## 🚀 Setup Instructions

### 1. **Configure Docker Hub Secrets**

In your GitHub repository, go to **Settings > Secrets and variables > Actions** and add:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username | `myusername` |
| `DOCKERHUB_TOKEN` | Docker Hub access token | `dckr_pat_...` |

### 2. **Create Docker Hub Access Token**

1. Go to [Docker Hub](https://hub.docker.com/)
2. Navigate to **Account Settings > Security**
3. Click **New Access Token**
4. Name: `GitHub Actions`
5. Permissions: **Read, Write, Delete**
6. Copy the generated token

## 📋 Usage

### **Automatic Builds**
- Builds trigger automatically on:
  - Push to `master` or `main` branch
  - Pull requests to `master` or `main` branch
- Images are built and tested but **not pushed** to Docker Hub

### **Manual Deployment**
1. Go to **Actions** tab in your GitHub repository
2. Select **"Build and Deploy Docker Image"** workflow
3. Click **"Run workflow"**
4. Configure options:
   - **Image name**: `gin-calculator` (or custom name)
   - **Deploy to Docker Hub**: ✅ Check this box
5. Click **"Run workflow"**

## 🎯 Workflow Features

### **Build Stage**
- ✅ Builds Docker image using Alpine Linux
- ✅ Uses Docker BuildKit for optimization
- ✅ Implements build caching for speed
- ✅ Tests the built image automatically
- ✅ Generates metadata and tags

### **Deploy Stage** (Manual only)
- 🚀 Pushes to Docker Hub with multiple tags
- 🏷️ Tags: `latest` and timestamp (`YYYYMMDD-HHmmss`)
- 📦 Uses your Docker Hub username automatically
- ✅ Provides pull commands in output

### **Testing**
Each build includes automatic testing:
- Starts the container on port 8080
- Waits for application startup
- Tests HTTP response from main page
- Cleans up test containers

## 🏷️ Image Tagging Strategy

### **Automatic Builds**
- `gin-calculator:main` (on main branch)
- `gin-calculator:pr-123` (on pull requests)
- `gin-calculator:20241211-143022` (timestamp)

### **Docker Hub Deployment**
- `username/gin-calculator:latest`
- `username/gin-calculator:20241211-143022`

## 📊 Monitoring

### **Build Status**
- Check the **Actions** tab for build status
- Green ✅ = successful build and test
- Red ❌ = build or test failed

### **Deployment Status**
- Manual deployments show detailed output
- Includes pull commands for easy access
- Shows all pushed tags

## 🔧 Customization

### **Change Default Image Name**
Edit the `IMAGE_NAME` environment variable in the workflow:

```yaml
env:
  IMAGE_NAME: my-custom-gin-calculator
```

### **Add Custom Tests**
Modify the test section in the workflow:

```yaml
- name: Test Docker image
  run: |
    # Add your custom tests here
    docker run --rm $IMAGE_TAG python manage.py test
```

### **Custom Dockerfile**
The workflow uses `./Dockerfile` by default. To use a different file:

```yaml
with:
  file: ./docker/Dockerfile.prod
```

## 🛡️ Security Best Practices

1. **Never commit Docker Hub credentials** to the repository
2. **Use access tokens** instead of passwords
3. **Limit token permissions** to what's needed
4. **Rotate tokens** regularly
5. **Review workflow logs** for sensitive information

## 🐛 Troubleshooting

### **Build Fails**
- Check the **Actions** tab for detailed logs
- Common issues: missing dependencies, syntax errors
- Test locally with: `docker build .`

### **Deployment Fails**
- Verify Docker Hub secrets are correctly set
- Check token permissions
- Ensure repository exists on Docker Hub

### **Tests Fail**
- Application might not be starting correctly
- Check container logs in the workflow output
- Test locally with: `./test-docker.sh`

## 📖 Example Usage

### **Pull and Run from Docker Hub**
```bash
# After successful deployment
docker pull yourusername/gin-calculator:latest
docker run -d -p 8000:8000 yourusername/gin-calculator:latest
```

### **Local Development**
```bash
# Build locally
docker build -t gin-calculator .

# Run locally
docker run -d -p 8000:8000 gin-calculator
```

## 🔄 Workflow Dispatch Parameters

When manually triggering the workflow:

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `image_name` | Docker image name | `gin-calculator` | Yes |
| `deploy_to_dockerhub` | Push to Docker Hub | `false` | Yes |

The workflow will automatically use your `DOCKERHUB_USERNAME` secret for the repository name.
