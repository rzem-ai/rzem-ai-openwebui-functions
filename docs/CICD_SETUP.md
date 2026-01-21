# CI/CD Setup Guide

This guide explains how to set up automated deployment of your OpenWebUI functions using GitHub Actions.

## Overview

The CI/CD pipeline automatically deploys your functions to OpenWebUI whenever you push changes to the `main` branch. It:

- Triggers on commits to the `main` branch that modify files in the `functions/` directory
- Deploys all Python function files to your OpenWebUI instance
- Creates new functions or updates existing ones
- Provides deployment logs as artifacts
- Can be manually triggered via GitHub Actions UI

## Prerequisites

Before setting up the pipeline, you need:

1. **OpenWebUI Instance**: A self-hosted OpenWebUI instance with a publicly accessible URL
2. **API Key**: An API key from your OpenWebUI instance
3. **GitHub Repository**: This repository with admin access to configure secrets

## Step 1: Get Your OpenWebUI API Key

1. Log in to your OpenWebUI instance as an admin
2. Go to **Settings** → **Account** (or **Admin Panel** → **Settings**)
3. Navigate to the **API Keys** section
4. Click **Create API Key**
5. Give it a name (e.g., "GitHub Actions Deployment")
6. Copy the generated API key (you won't be able to see it again)

## Step 2: Configure GitHub Secrets

GitHub Secrets securely store sensitive information like your API key.

### Adding Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following two secrets:

#### Secret 1: OPENWEBUI_URL

- **Name**: `OPENWEBUI_URL`
- **Value**: Your OpenWebUI instance URL (e.g., `https://openwebui.example.com`)
- **Note**: Do NOT include a trailing slash

#### Secret 2: OPENWEBUI_API_KEY

- **Name**: `OPENWEBUI_API_KEY`
- **Value**: The API key you generated in Step 1

## Step 3: Test the Pipeline

### Option 1: Manual Trigger

1. Go to **Actions** tab in your GitHub repository
2. Click on **Deploy Functions to OpenWebUI** workflow
3. Click **Run workflow** → **Run workflow**
4. Wait for the workflow to complete
5. Check the logs to verify deployment

### Option 2: Commit to Main Branch

1. Make a change to any file in the `functions/` directory
2. Commit and push to the `main` branch:
   ```bash
   git add functions/
   git commit -m "Update function"
   git push origin main
   ```
3. Go to the **Actions** tab to monitor the deployment

## How It Works

### Workflow Trigger

The workflow (`.github/workflows/deploy.yml`) triggers when:

- Code is pushed to the `main` branch
- The changes include files in `functions/**/*.py`, `scripts/deploy.py`, or the workflow file itself
- The workflow is manually triggered via the GitHub Actions UI

### Deployment Process

1. **Checkout**: Downloads your repository code
2. **Setup Python**: Installs Python 3.11
3. **Install Dependencies**: Installs required Python packages (requests)
4. **Deploy Functions**: Runs the deployment script
   - Scans the `functions/` directory for Python files
   - Extracts function metadata (ID, name, description)
   - Checks if each function exists in OpenWebUI
   - Creates new functions or updates existing ones
5. **Upload Logs**: Saves deployment logs as artifacts (available for 30 days)

### Deployment Script

The deployment script (`scripts/deploy.py`) handles:

- **Authentication**: Uses your API key to authenticate with OpenWebUI
- **Function Discovery**: Finds all `.py` files in the `functions/` directory
- **Metadata Extraction**: Parses function ID, name, and description from the Python files
- **API Calls**: Creates or updates functions via the OpenWebUI API
- **Logging**: Provides detailed logs for troubleshooting

## Function File Requirements

For the deployment script to work correctly, your function files should follow this structure:

```python
class YourFunctionName:
    """
    Your function description
    """

    id = "your-function-id"  # Required: Unique identifier
    name = "Display Name"    # Optional: Display name in UI
    description = "Brief description"  # Optional: Description

    # ... rest of your function code
```

### Metadata Detection

The script automatically extracts:

- **ID**: From the `id` attribute, or generates from filename if not found
- **Name**: From the `name` attribute, or uses the class name if not found
- **Description**: From the `description` attribute, or generates a default if not found

## Troubleshooting

### Deployment Fails with Authentication Error

**Problem**: Error like "401 Unauthorized" or "403 Forbidden"

**Solutions**:
- Verify your `OPENWEBUI_API_KEY` secret is correct
- Ensure the API key hasn't expired
- Check that the API key has admin permissions
- Regenerate the API key if necessary

### Deployment Fails with Connection Error

**Problem**: Error like "Connection refused" or "Timeout"

**Solutions**:
- Verify your `OPENWEBUI_URL` is correct and accessible
- Ensure there's no trailing slash in the URL
- Check that your OpenWebUI instance is running
- Verify firewall rules allow GitHub Actions IPs (if applicable)

### Function Not Showing in OpenWebUI

**Problem**: Deployment succeeds but function doesn't appear

**Solutions**:
- Check the deployment logs for errors
- Verify the function has a valid `id` attribute
- Log in to OpenWebUI and check Settings → Functions
- Refresh your OpenWebUI browser page
- Check OpenWebUI server logs for errors

### Function ID Conflicts

**Problem**: Error about duplicate function IDs

**Solutions**:
- Ensure each function file has a unique `id` attribute
- Check for duplicate files with the same function ID
- Remove or rename conflicting functions

### Viewing Deployment Logs

1. Go to **Actions** tab in GitHub
2. Click on the failed workflow run
3. Click on the **deploy** job
4. Expand the **Deploy functions to OpenWebUI** step
5. Review the logs
6. Download the **deployment-logs** artifact for detailed logs

## Advanced Configuration

### Customizing the Workflow

Edit `.github/workflows/deploy.yml` to:

- **Change trigger branch**: Modify `branches: [main]` to your desired branch
- **Add environment**: Deploy to different environments (dev, staging, prod)
- **Add validation**: Run tests or linting before deployment
- **Add notifications**: Send Slack/Discord notifications on deployment

### Deploying to Multiple Instances

To deploy to multiple OpenWebUI instances:

1. Create additional secret pairs (e.g., `OPENWEBUI_URL_DEV`, `OPENWEBUI_API_KEY_DEV`)
2. Duplicate the deploy step in the workflow
3. Use different environment variables for each instance

Example:

```yaml
- name: Deploy to Production
  env:
    OPENWEBUI_URL: ${{ secrets.OPENWEBUI_URL_PROD }}
    OPENWEBUI_API_KEY: ${{ secrets.OPENWEBUI_API_KEY_PROD }}
  run: python scripts/deploy.py

- name: Deploy to Development
  env:
    OPENWEBUI_URL: ${{ secrets.OPENWEBUI_URL_DEV }}
    OPENWEBUI_API_KEY: ${{ secrets.OPENWEBUI_API_KEY_DEV }}
  run: python scripts/deploy.py
```

### Local Testing

You can test the deployment script locally:

```bash
# Install dependencies
pip install requests

# Set environment variables
export OPENWEBUI_URL="https://your-openwebui-instance.com"
export OPENWEBUI_API_KEY="your-api-key"

# Run the deployment script
python scripts/deploy.py
```

## Security Best Practices

1. **Never commit API keys**: Always use GitHub Secrets
2. **Rotate API keys**: Periodically regenerate and update your API keys
3. **Limit permissions**: Use API keys with minimum required permissions
4. **Monitor deployments**: Review deployment logs regularly
5. **Use branch protection**: Require reviews before merging to main

## Getting Help

If you encounter issues:

1. Check the deployment logs in GitHub Actions
2. Review the [OpenWebUI API documentation](https://docs.openwebui.com/)
3. Verify your OpenWebUI instance is accessible and running
4. Open an issue in this repository with deployment logs

## Next Steps

- Set up branch protection rules for the main branch
- Add pre-deployment tests to validate function syntax
- Configure notifications for deployment failures
- Document your custom functions in the repository
