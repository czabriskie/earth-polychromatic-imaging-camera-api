# Demo Checklist - NASA EPIC Lambda Setup

## Pre-Demo Setup (5 minutes before class)

### ✅ Prerequisites Check
- [ ] Code pushed to main branch (triggers ECR image build)
- [ ] GitHub Actions workflow completed successfully
- [ ] AWS Console access ready
- [ ] S3 bucket created: `my-nasa-epic-images` (or similar)
- [ ] Run `./get_image_uri.sh` to get ECR image URI

### ✅ Quick Verification
```bash
# Verify ECR image exists
./get_image_uri.sh

# Should output something like:
# 123456789012.dkr.ecr.us-east-1.amazonaws.com/nasa-epic-downloader:latest
```

---

## Live Demo Script (30 minutes)

### 📖 Introduction (3 minutes)
- "Today we're building a serverless image downloader"
- Show NASA EPIC website: https://epic.gsfc.nasa.gov/
- Explain the automation challenge

### 🔧 Part 1: IAM Role Setup (5 minutes)
**Navigate to:** IAM → Roles → Create role

1. **Service:** Lambda
2. **Policies:** `AWSLambdaBasicExecutionRole`
3. **Role name:** `nasa-epic-lambda-role`
4. **Add S3 policy** (show JSON):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Action": ["s3:*"],
       "Resource": [
         "arn:aws:s3:::my-nasa-epic-images",
         "arn:aws:s3:::my-nasa-epic-images/*"
       ]
     }]
   }
   ```

### 🚀 Part 2: Lambda Function Creation (8 minutes)
**Navigate to:** Lambda → Create function

1. **Type:** Container image
2. **Name:** `nasa-epic-downloader`
3. **Image URI:** `[paste from get_image_uri.sh]`
4. **Role:** `nasa-epic-lambda-role`

**Configure:**
- **Timeout:** 15 minutes
- **Memory:** 1024 MB
- **Environment variables:**
  - `S3_BUCKET` = `my-nasa-epic-images`
  - `COLLECTION` = `natural`
  - `DAYS_BACK` = `1`

### 🧪 Part 3: Testing (7 minutes)
**Create test event:**
```json
{
  "bucket": "my-nasa-epic-images",
  "collection": "natural"
}
```

**Execute and show:**
- CloudWatch logs
- Function execution time
- S3 bucket contents

### ⏰ Part 4: Automation with EventBridge (5 minutes)
**Navigate to:** EventBridge → Rules → Create rule

1. **Name:** `nasa-epic-daily`
2. **Schedule:** `cron(0 6 * * ? *)` (6 AM UTC daily)
3. **Target:** Lambda function
4. **Payload:**
   ```json
   {"bucket": "my-nasa-epic-images", "collection": "natural"}
   ```

### 📊 Part 5: Monitoring (2 minutes)
**Show:**
- Lambda metrics
- CloudWatch logs
- Cost estimation

---

## Key Demo Points to Emphasize

### 💡 **Serverless Benefits**
- "No servers to manage, pay only when it runs"
- "Automatically scales from 0 to 1000 concurrent executions"

### 💡 **Event-Driven Architecture**
- "EventBridge decouples the scheduler from the function"
- "Easy to change schedules without touching code"

### 💡 **Container Deployment**
- "Modern Lambda supports containers up to 10GB"
- "Brings your own dependencies, any language"

### 💡 **Security Best Practices**
- "IAM roles with minimal permissions"
- "No hardcoded credentials in code"

### 💡 **Observability**
- "Built-in CloudWatch integration"
- "Distributed tracing with X-Ray (if enabled)"

---

## Student Q&A - Common Questions

### **Q: How much does this cost?**
**A:** Very little! Lambda free tier = 1M requests/month. This runs once daily = ~30 requests/month. Essentially free.

### **Q: What if the function fails?**
**A:** Configure dead letter queues, retry logic, or SNS notifications for failures.

### **Q: Can we run this more frequently?**
**A:** Yes, but NASA EPIC only updates 8-10 times per day, so hourly is practical maximum.

### **Q: How do we update the code?**
**A:** Push to GitHub → Actions builds new image → Update Lambda to use new image URI.

### **Q: Can we process the images?**
**A:** Absolutely! Add image processing libraries to the container, or trigger another service.

---

## Demo Cleanup (End of Class)

### 🧹 Resources to Delete
1. **EventBridge rule** (to stop automatic execution)
2. **Lambda function** (main cost driver)
3. **IAM role** (security cleanup)
4. **S3 bucket contents** (storage costs)

### 🧹 Keep for Next Demo
- ECR repository (images rebuild automatically)
- S3 bucket (reusable)

---

## Troubleshooting During Demo

### **ECR Image Not Found**
- Check GitHub Actions: https://github.com/czabriskie/earth-polychromatic-imaging-camera-api/actions
- Run workflow manually if needed

### **Lambda Timeout**
- "This is normal for first run - container cold start"
- Show CloudWatch logs for actual processing time

### **No Images Downloaded**
- "NASA EPIC has 1-2 day processing delay"
- Use `days_back: 2` or specific older date

### **Permission Errors**
- Double-check S3 bucket name in IAM policy
- Verify role is attached to Lambda function