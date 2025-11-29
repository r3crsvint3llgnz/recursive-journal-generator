# CloudFormation Stack Deletion Troubleshooting Guide

## Problem Summary

The CloudFormation stack `RIJG-MVP` is failing to delete due to an IAM permission issue with the custom resource that manages S3 bucket notifications.

### Error Details

```
ResourceStatusReason: "Received response status [FAILED] from custom resource.
Message returned: An error occurred (AccessDenied) when calling the
PutBucketNotificationConfiguration operation: User: arn:aws:sts::843475473749:
assumed-role/RIJG-MVP-BucketNotificationHandlerRole-Lxk9rBqorWH5/RIJG-MVP-
BucketNotificationHandler-6UqGUmaWJx9N is not authorized to perform:
s3:PutBucketNotification on resource: "arn:aws:s3:::rijg-mvp-rawconversationbucket-02po9m9cfieg"
```

## Root Cause

1. The `BucketNotificationHandler` Lambda function needs permission to both **create** and **delete** S3 bucket notifications
2. During stack deletion, the custom resource handler tries to remove the notification configuration
3. The original IAM policy only granted permissions for creation, not deletion
4. An inline policy `AllowBucketNotificationsDelete` was added, but IAM changes take time to propagate (typically 1-2 minutes, sometimes longer)

## Solution

### Automated Fix (Recommended)

Run the provided script which handles all steps automatically:

```bash
cd /home/cntry/Projects/recursive-journal-generator
./fix_stack_deletion.sh
```

The script will:

1. ✓ Verify the IAM policy is attached
2. ⏱ Wait 60 seconds for IAM propagation
3. 🔍 Check stack status
4. 🗑️ Attempt normal stack deletion
5. 🔧 If that fails, manually clear the bucket notification and retry
6. ✅ Report success or provide next steps

### Manual Fix (Alternative)

If you prefer to run commands manually:

#### Step 1: Verify Policy Attachment

```bash
aws iam get-role-policy \
  --role-name RIJG-MVP-BucketNotificationHandlerRole-Lxk9rBqorWH5 \
  --policy-name AllowBucketNotificationsDelete \
  --region us-east-2
```

#### Step 2: Wait for IAM Propagation

Wait at least 2-3 minutes after the policy was attached to ensure global propagation.

#### Step 3: Retry Stack Deletion

```bash
aws cloudformation delete-stack --stack-name RIJG-MVP --region us-east-2
aws cloudformation wait stack-delete-complete --stack-name RIJG-MVP --region us-east-2
```

#### Step 4: If Still Failing - Manual Cleanup

Clear the bucket notification configuration manually to bypass the custom resource:

```bash
aws s3api put-bucket-notification-configuration \
  --bucket rijg-mvp-rawconversationbucket-02po9m9cfieg \
  --notification-configuration '{}' \
  --region us-east-2
```

Then retry deletion:

```bash
aws cloudformation delete-stack --stack-name RIJG-MVP --region us-east-2
aws cloudformation wait stack-delete-complete --stack-name RIJG-MVP --region us-east-2
```

## Template Fix for Future Deployments

The issue stems from the template's `BucketNotificationHandler` function having insufficient permissions. Update `template.yaml`:

### Current (Problematic) Policy:

```yaml
BucketNotificationHandler:
  Type: AWS::Serverless::Function
  Properties:
    Policies:
      - AWSLambdaBasicExecutionRole
      - Statement:
          - Effect: Allow
            Action:
              - s3:PutBucketNotificationConfiguration
              - s3:GetBucketNotificationConfiguration
            Resource: !GetAtt RawConversationBucket.Arn
```

### Recommended Fix:

Add `s3:PutBucketNotification` (without "Configuration" suffix) which is the action required during deletion:

```yaml
BucketNotificationHandler:
  Type: AWS::Serverless::Function
  Properties:
    Policies:
      - AWSLambdaBasicExecutionRole
      - Statement:
          - Effect: Allow
            Action:
              - s3:PutBucketNotificationConfiguration
              - s3:GetBucketNotificationConfiguration
              - s3:PutBucketNotification # Add this line
            Resource: !GetAtt RawConversationBucket.Arn
```

## After Successful Deletion

Once the stack is deleted:

1. **Update template.yaml** with the fix above
2. **Redeploy the stack**:
   ```bash
   cd /home/cntry/Projects/recursive-journal-generator
   sam build
   sam deploy --guided
   ```
3. **Verify** the new deployment creates and deletes cleanly

## Prevention

To prevent this issue in future stacks:

1. Always grant both creation and deletion permissions for custom resources
2. Test stack deletion in a dev environment before production deployment
3. Consider using AWS CDK's `BucketNotifications` construct which handles permissions automatically
4. Document custom resource IAM requirements in your template comments

## Additional Resources

- [AWS S3 Bucket Notifications Documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html)
- [IAM Policy Propagation Times](https://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_general.html#troubleshoot_general_eventual-consistency)
- [CloudFormation Custom Resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html)

## Status Tracking

- [x] Issue identified: AccessDenied on s3:PutBucketNotification
- [x] Inline policy attached to role
- [ ] IAM propagation wait complete
- [ ] Stack deletion retry
- [ ] Template fixed for future deployments
- [ ] Stack redeployed with corrected permissions
