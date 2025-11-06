# AWS Lambda Setup Guide - Console Demo

This guide shows how to set up the NASA EPIC image downloader as an AWS Lambda function using the AWS Console. Perfect for classroom demonstrations!

## Overview

We'll create a Lambda function that downloads NASA Earth images and stores them in S3, then set up EventBridge to run it daily.

## Prerequisites

✅ AWS Account with console access
✅ S3 bucket created (we'll use: `my-nasa-epic-images`)
✅ Docker Desktop installed
✅ AWS CLI configured

---

## Step 1: Get Pre-built Docker Image

The Docker image is automatically built and pushed to ECR via GitHub Actions whenever code is pushed to the main branch.

### 1.1 Find Your ECR Repository

1. Go to **Amazon ECR** in AWS Console
2. Look for repository: `nasa-epic-downloader`
3. Click on the repository name
4. Copy the **URI** from the latest image (should end with `:latest`)
5. Example: `123456789012.dkr.ecr.us-east-1.amazonaws.com/nasa-epic-downloader:latest`

> **Note**: If the repository doesn't exist, make sure the GitHub Actions workflow has run successfully after pushing to the main branch.

---

## Step 2: Create IAM Role (Console)

### 2.1 Create Execution Role

1. Go to **IAM** → **Roles**
2. Click **"Create role"**
3. Select **"AWS service"** → **"Lambda"**
4. Click **"Next"**
5. Search and attach these policies:
   - `AWSLambdaBasicExecutionRole`
6. Click **"Next"**
7. Role name: `nasa-epic-lambda-role`
8. Click **"Create role"**

### 2.2 Add S3 Permissions

1. Find your new role: `nasa-epic-lambda-role`
2. Click **"Add permissions"** → **"Create inline policy"**
3. Click **"JSON"** tab
4. Paste this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-nasa-epic-images",
        "arn:aws:s3:::my-nasa-epic-images/*"
      ]
    }
  ]
}
```

5. Click **"Next"**
6. Policy name: `S3AccessPolicy`
7. Click **"Create policy"**

---

## Step 3: Create Lambda Function (Console)

### 3.1 Basic Configuration

1. Go to **AWS Lambda**
2. Click **"Create function"**
3. Select **"Container image"**
4. Function name: `nasa-epic-downloader`
5. Container image URI: `YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/nasa-epic-downloader:latest`
6. Architecture: `x86_64`
7. Execution role: **"Use an existing role"** → `nasa-epic-lambda-role`
8. Click **"Create function"**

### 3.2 Configure Function Settings

1. In your Lambda function, go to **"Configuration"** tab
2. Click **"General configuration"** → **"Edit"**
3. Set:
   - **Timeout**: `15 minutes`
   - **Memory**: `1024 MB`
4. Click **"Save"**

### 3.3 Set Environment Variables

1. Still in **"Configuration"** tab
2. Click **"Environment variables"** → **"Edit"**
3. Add these variables:

| Key          | Value                 |
| ------------ | --------------------- |
| `S3_BUCKET`  | `my-nasa-epic-images` |
| `COLLECTION` | `natural`             |
| `DAYS_BACK`  | `1`                   |

4. Click **"Save"**

---

## Step 4: Test the Lambda Function

### 4.1 Create Test Event

1. In Lambda function, click **"Test"** tab
2. Click **"Create new event"**
3. Event name: `test-natural-images`
4. Event JSON:

```json
{
  "bucket": "my-nasa-epic-images",
  "collection": "natural"
}
```

5. Click **"Save"**

### 4.2 Run Test

1. Click **"Test"** button
2. Wait for execution (may take 1-2 minutes)
3. Check **"Execution results"** for success
4. Check **CloudWatch logs** for details

### 4.3 Verify S3 Upload

1. Go to **Amazon S3**
2. Open bucket: `my-nasa-epic-images`
3. Look for folder structure: `epic/natural/YYYY/MM/DD/`
4. Verify images were uploaded

---

## Step 5: Create EventBridge Schedule (Console)

### 5.1 Create Rule

1. Go to **Amazon EventBridge**
2. Click **"Rules"** → **"Create rule"**
3. Name: `nasa-epic-daily-download`
4. Description: `Download NASA EPIC images daily`
5. Event bus: `default`
6. Rule type: **"Schedule"**
7. Click **"Next"**

### 5.2 Set Schedule

1. Schedule pattern: **"Rate-based schedule"**
2. Rate expression: `cron(0 6 * * ? *)`
   - This runs daily at 6:00 AM UTC
3. Click **"Next"**

### 5.3 Select Target

1. Target type: **"AWS service"**
2. Select service: **"Lambda function"**
3. Function: `nasa-epic-downloader`
4. Payload: **"Constant (JSON text)"**
5. JSON payload:

```json
{
  "bucket": "my-nasa-epic-images",
  "collection": "natural"
}
```

6. Click **"Next"**
7. Click **"Create rule"**

---

## Step 6: Test EventBridge Integration

### 6.1 Manual Trigger

1. In EventBridge, find your rule: `nasa-epic-daily-download`
2. Click **"Actions"** → **"Test rule"**
3. This will immediately trigger your Lambda function
4. Check Lambda logs to verify execution

### 6.2 Verify Permissions

EventBridge should automatically create the required permissions. If there are issues:

1. Go to Lambda function → **"Configuration"** → **"Permissions"**
2. Check **"Resource-based policy statements"**
3. Should see EventBridge permission

---

## Demo Script for Students

### Part 1: Show the Problem (5 minutes)
- Explain NASA EPIC API
- Show manual image download process
- Discuss automation challenges

### Part 2: Lambda Creation (10 minutes)
- Create IAM role with S3 permissions
- Deploy Lambda function from container
- Configure timeout and memory
- Set environment variables

### Part 3: Testing (5 minutes)
- Create test event
- Execute function
- Show CloudWatch logs
- Verify S3 uploads

### Part 4: Automation (10 minutes)
- Create EventBridge rule
- Set cron schedule
- Configure Lambda target
- Test the integration

### Part 5: Monitoring (5 minutes)
- Show CloudWatch metrics
- Demonstrate log analysis
- Discuss cost optimization

---

## Key Teaching Points

🎯 **Serverless Benefits**: No server management, pay-per-use, automatic scaling
🎯 **Event-Driven Architecture**: EventBridge triggers, decoupled components
🎯 **Container Deployment**: Modern Lambda deployment with custom dependencies
🎯 **IAM Security**: Principle of least privilege, role-based permissions
🎯 **Monitoring**: CloudWatch integration, observability best practices

---

## Configuration Variations for Demo

### Different Collections
```json
{"bucket": "my-nasa-epic-images", "collection": "enhanced"}
{"bucket": "my-nasa-epic-images", "collection": "aerosol"}
```

### Date Ranges
```json
{
  "bucket": "my-nasa-epic-images",
  "collection": "natural",
  "start_date": "2024-01-15",
  "end_date": "2024-01-17"
}
```

### Multiple Days
```json
{
  "bucket": "my-nasa-epic-images",
  "collection": "natural",
  "date_range_days": 7,
  "days_back": 7
}
```

---

## Troubleshooting Common Issues

### Lambda Timeout
- Increase timeout to 15 minutes maximum
- Consider date range size

### Permission Denied
- Check IAM role has S3 permissions
- Verify bucket name matches policy

### No Images Downloaded
- EPIC data has 1-2 day processing delay
- Try `days_back: 2` or specific older dates

### Container Issues
- Verify ECR image URI is correct
- Check image was pushed successfully

---

## Cleanup (End of Demo)

1. **Delete EventBridge rule**: Stop automatic execution
2. **Delete Lambda function**: Remove compute resources
3. **Delete ECR repository**: Remove container images
4. **Delete IAM role**: Clean up permissions
5. **Empty S3 bucket**: Remove downloaded files (optional)

This ensures no ongoing costs after the demonstration.