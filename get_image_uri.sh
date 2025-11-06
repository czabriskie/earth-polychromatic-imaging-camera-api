#!/bin/bash
# Get ECR image URI for Lambda console setup

REGION=${AWS_REGION:-us-east-1}
REPO_NAME="nasa-epic-downloader"

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || {
    echo "❌ AWS CLI not configured"
    exit 1
})

# Check if repository exists
aws ecr describe-repositories --repository-names $REPO_NAME --region $REGION >/dev/null 2>&1 || {
    echo "❌ Repository '$REPO_NAME' not found"
    echo "💡 Push code to main branch to trigger build"
    exit 1
}

# Output the image URI for easy copy-paste
IMAGE_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest"
echo "📋 Lambda Image URI:"
echo "$IMAGE_URI"