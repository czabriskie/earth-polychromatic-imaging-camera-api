# AWS CodeArtifact CI/CD Setup Guide

This document outlines the AWS permissions, secrets, and variables required to set up the CI/CD pipeline with AWS CodeArtifact publishing.

## 🔐 AWS IAM Permissions Required

Your AWS user/role that runs in the GitHub Actions pipeline needs the following permissions:

### CodeArtifact Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "codeartifact:GetAuthorizationToken",
                "codeartifact:GetRepositoryEndpoint",
                "codeartifact:ReadFromRepository",
                "codeartifact:PublishPackageVersion",
                "codeartifact:PutPackageMetadata",
                "codeartifact:DescribePackageVersion",
                "codeartifact:DescribeRepository",
                "codeartifact:DescribeDomain",
                "codeartifact:ListPackages",
                "codeartifact:ListPackageVersions"
            ],
            "Resource": [
                "arn:aws:codeartifact:*:YOUR_ACCOUNT_ID:domain/YOUR_DOMAIN_NAME",
                "arn:aws:codeartifact:*:YOUR_ACCOUNT_ID:repository/YOUR_DOMAIN_NAME/*",
                "arn:aws:codeartifact:*:YOUR_ACCOUNT_ID:package/YOUR_DOMAIN_NAME/*/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "sts:GetServiceBearerToken"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "sts:AWSServiceName": "codeartifact.amazonaws.com"
                }
            }
        }
    ]
}
```

### Additional Permissions for OIDC (Recommended)
If using GitHub OIDC (recommended for security):
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USERNAME/earth-polychromatic-images:*"
                }
            }
        }
    ]
}
```

## 🗝️ GitHub Secrets Required

Set these in your GitHub repository settings under **Settings > Secrets and variables > Actions**:

### For AWS Access Keys Method (Less Secure)
```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

### For OIDC Method (More Secure - Recommended)
No secrets needed! OIDC uses temporary tokens.

## 📝 GitHub Variables Required

Set these in your GitHub repository settings under **Settings > Secrets and variables > Actions > Variables**:

```
AWS_REGION=us-east-1                           # Your AWS region
AWS_ACCOUNT_ID=123456789012                    # Your AWS account ID
AWS_ROLE_ARN=arn:aws:iam::123456789012:role/GitHubActions-CodeArtifact  # For OIDC only
CODEARTIFACT_DOMAIN=your-domain-name          # Your CodeArtifact domain
CODEARTIFACT_REPOSITORY=your-repo-name        # Your CodeArtifact repository
```

## 🏗️ AWS CodeArtifact Setup

### 1. Create CodeArtifact Domain
```bash
aws codeartifact create-domain \
    --domain your-domain-name \
    --region us-east-1
```

### 2. Create CodeArtifact Repository
```bash
aws codeartifact create-repository \
    --domain your-domain-name \
    --repository your-repo-name \
    --description "Python packages for earth-polychromatic-api" \
    --upstreams repositoryName=pypi-store \
    --region us-east-1
```

### 3. Create PyPI External Connection (Optional)
```bash
aws codeartifact create-repository \
    --domain your-domain-name \
    --repository pypi-store \
    --description "PyPI upstream repository" \
    --external-connections externalConnectionName=public:pypi \
    --region us-east-1
```

## 🎯 OIDC Setup (Recommended)

### 1. Create OIDC Provider in AWS
```bash
aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
    --client-id-list sts.amazonaws.com
```

### 2. Create IAM Role for GitHub Actions
```bash
aws iam create-role \
    --role-name GitHubActions-CodeArtifact \
    --assume-role-policy-document file://trust-policy.json
```

**trust-policy.json:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USERNAME/earth-polychromatic-images:*"
                }
            }
        }
    ]
}
```

### 3. Attach Policy to Role
```bash
aws iam attach-role-policy \
    --role-name GitHubActions-CodeArtifact \
    --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/CodeArtifact-Publish-Policy
```

## 🧪 Testing the Setup

### 1. Test CodeArtifact Access Locally
```bash
# Get auth token
export CODEARTIFACT_AUTH_TOKEN=$(aws codeartifact get-authorization-token \
    --domain your-domain-name \
    --domain-owner 123456789012 \
    --query authorizationToken --output text)

# Configure pip
pip config set global.index-url https://aws:$CODEARTIFACT_AUTH_TOKEN@your-domain-name-123456789012.d.codeartifact.us-east-1.amazonaws.com/pypi/your-repo-name/simple/

# Test upload
twine upload --repository-url https://your-domain-name-123456789012.d.codeartifact.us-east-1.amazonaws.com/pypi/your-repo-name/ \
    --username aws \
    --password $CODEARTIFACT_AUTH_TOKEN \
    dist/*
```

### 2. Verify Package Installation
```bash
pip install earth-polychromatic-api
```

## 🚀 Pipeline Triggers

The pipeline will run on:
- **Push to main/develop**: Runs linting, testing, and building
- **Pull requests**: Runs linting, testing, and building
- **Release published**: Runs full pipeline + publishes to CodeArtifact

## 📋 Checklist

- [ ] AWS CodeArtifact domain created
- [ ] AWS CodeArtifact repository created
- [ ] IAM permissions configured
- [ ] OIDC provider created (if using OIDC)
- [ ] IAM role created for GitHub Actions
- [ ] GitHub repository variables set
- [ ] GitHub repository secrets set (if not using OIDC)
- [ ] Test local CodeArtifact access
- [ ] Create a test release to verify pipeline

## 🔍 Troubleshooting

### Common Issues

1. **403 Forbidden when publishing**
   - Check IAM permissions
   - Verify CodeArtifact domain/repository names
   - Ensure auth token is valid

2. **OIDC authentication failed**
   - Verify trust relationship in IAM role
   - Check GitHub repository name in condition
   - Ensure OIDC provider is correctly configured

3. **Package not found after publishing**
   - Check repository upstream connections
   - Verify package was published successfully
   - Check CodeArtifact repository contents in AWS Console

### Useful Commands

```bash
# List packages in repository
aws codeartifact list-packages \
    --domain your-domain-name \
    --repository your-repo-name

# Get repository endpoint
aws codeartifact get-repository-endpoint \
    --domain your-domain-name \
    --repository your-repo-name \
    --format pypi

# Delete package version (if needed)
aws codeartifact delete-package-versions \
    --domain your-domain-name \
    --repository your-repo-name \
    --package earth-polychromatic-api \
    --format pypi \
    --versions 0.1.0
```