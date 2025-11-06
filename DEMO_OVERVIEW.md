# 🎯 NASA EPIC Lambda - Complete Console Demo Setup

## What We Built

✅ **Automated Docker Build**: GitHub Actions builds and pushes Lambda container to ECR
✅ **Console-First Setup**: Everything else done in AWS Console for educational visibility
✅ **Complete Documentation**: Step-by-step guides for demo and student learning
✅ **Helper Scripts**: Easy tools to get image URIs and verify setup

---

## Quick Start for Your Demo

### 1. Trigger the Build (One-time)
```bash
# Push code to trigger ECR build
git add .
git commit -m "Add Lambda container and demo setup"
git push origin main
```

### 2. Get the Image URI
```bash
# After GitHub Actions completes
./get_image_uri.sh
# Copy the output URI for Lambda setup
```

### 3. Follow the Demo Script
- Use `DEMO_CHECKLIST.md` for live demo
- Use `CONSOLE_SETUP_GUIDE.md` for detailed steps
- Everything else is done in AWS Console

---

## Files Created

### 📦 **Lambda Container**
- `Dockerfile.lambda` - Container for Lambda runtime
- `lambda_handler.py` - Lambda function code with full configuration

### 🔄 **CI/CD Integration**
- `.github/workflows/ci-cd.yml` - Updated with ECR build job
- Builds on every push to main branch
- Creates ECR repository automatically
- Sets lifecycle policy (keeps last 10 images)

### 📚 **Demo Documentation**
- `CONSOLE_SETUP_GUIDE.md` - Complete step-by-step console setup
- `DEMO_CHECKLIST.md` - Live demo script with timing and talking points
- `README_LAMBDA.md` - Technical documentation for advanced users

### 🛠 **Helper Tools**
- `get_image_uri.sh` - Gets ECR image URI for Lambda setup
- Clean console output for easy copy-paste

---

## CI/CD Pipeline Features

### **Automated ECR Management**
- Creates ECR repository if missing
- Pushes both tagged (`git-sha`) and `latest` versions
- Sets image lifecycle policy (cleanup old images)
- Only runs on `main` branch pushes and releases

### **Security & Best Practices**
- Uses OIDC for AWS authentication (no stored credentials)
- Leverages existing AWS environment variables
- Follows principle of least privilege

### **Developer Experience**
- Clear output in GitHub Actions logs with copy-paste URI
- Automatic cleanup of old images
- No manual Docker commands needed

---

## Demo Flow for Students

### **Phase 1: Show the Problem** ⏰ 3 min
- NASA provides satellite images via API
- Manual download is tedious and error-prone
- Need automation for daily updates

### **Phase 2: Build the Solution** ⏰ 20 min
1. **IAM Role** (5 min) - Security first approach
2. **Lambda Function** (8 min) - Serverless compute
3. **Testing** (7 min) - Verify it works

### **Phase 3: Automate** ⏰ 5 min
- **EventBridge** - Event-driven scheduling
- **Monitoring** - Observability best practices

### **Phase 4: Discuss** ⏰ 2 min
- Cost analysis (essentially free!)
- Scalability (automatic)
- Maintenance (minimal)

---

## Key Learning Objectives

### 🎓 **Serverless Architecture**
Students learn hands-on serverless benefits:
- No infrastructure management
- Pay-per-use pricing model
- Automatic scaling and availability

### 🎓 **Event-Driven Design**
Demonstrate loose coupling:
- EventBridge schedules independently
- Lambda executes business logic
- S3 provides durable storage

### 🎓 **Modern DevOps Practices**
Show professional workflows:
- Container-based deployments
- GitOps with automated builds
- Infrastructure as code principles

### 🎓 **AWS Security Best Practices**
Emphasize security-first approach:
- IAM roles with minimal permissions
- No hardcoded credentials
- Audit trails via CloudWatch

---

## Next Steps After Demo

### **For Advanced Students**
- Add image processing (resize, watermark)
- Implement error handling and notifications
- Add multiple collection support
- Create CloudFormation/CDK templates

### **For Production Use**
- Add monitoring and alerting
- Implement retry logic and dead letter queues
- Add cost optimization strategies
- Set up cross-region backup

---

## Support During Demo

### **If GitHub Actions Fails**
- Check repository secrets and variables
- Manually run workflow from Actions tab
- Use local `build_and_push.sh` as backup

### **If ECR Repository Missing**
- Verify AWS permissions for GitHub Actions
- Check environment variables in GitHub settings
- Repository should auto-create on first push

### **If Lambda Creation Fails**
- Double-check image URI format
- Verify ECR repository exists
- Ensure IAM role has proper trust policy

---

## Student Takeaways

By the end of this demo, students will understand:

✅ **Serverless computing** fundamentals and benefits
✅ **Event-driven architecture** patterns
✅ **AWS security** with IAM roles and policies
✅ **Modern CI/CD** with GitHub Actions and containers
✅ **Cost optimization** strategies for cloud workloads
✅ **Monitoring and observability** best practices

Perfect for cloud computing, DevOps, or software engineering courses! 🚀