#!/bin/bash
# Complete fix for CloudFormation stack deletion
# Updates IAM policy with correct permissions and retries deletion

set -e

STACK_NAME="RIJG-MVP"
REGION="us-east-2"
ROLE_NAME="RIJG-MVP-BucketNotificationHandlerRole-Lxk9rBqorWH5"
BUCKET_NAME="rijg-mvp-rawconversationbucket-02po9m9cfieg"
POLICY_NAME="AllowBucketNotificationsDelete"

echo "=========================================="
echo "Complete CloudFormation Stack Deletion Fix"
echo "=========================================="
echo ""

# Step 1: Update the IAM policy with the correct permission
echo "Step 1: Updating IAM policy with s3:PutBucketNotification permission..."
echo "  The current policy is missing the 's3:PutBucketNotification' action"
echo "  (it only has 's3:PutBucketNotificationConfiguration')"
echo ""

aws iam put-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-name "$POLICY_NAME" \
  --region "$REGION" \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "s3:PutBucketNotificationConfiguration",
          "s3:GetBucketNotificationConfiguration",
          "s3:PutBucketNotification"
        ],
        "Resource": "arn:aws:s3:::'"$BUCKET_NAME"'"
      }
    ]
  }'

echo "✓ Policy updated successfully"
echo ""

# Step 2: Verify the policy now includes all required actions
echo "Step 2: Verifying updated policy..."
ACTIONS=$(aws iam get-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-name "$POLICY_NAME" \
  --region "$REGION" \
  --query 'PolicyDocument.Statement[0].Action' \
  --output json)

echo "  Current actions in policy:"
echo "$ACTIONS" | jq -r '.[]' | sed 's/^/    - /'
echo ""

if echo "$ACTIONS" | grep -q "s3:PutBucketNotification"; then
    echo "✓ Policy includes required s3:PutBucketNotification action"
else
    echo "✗ Policy still missing s3:PutBucketNotification action"
    exit 1
fi
echo ""

# Step 3: Wait for IAM propagation
echo "Step 3: Waiting for IAM propagation (90 seconds)..."
echo "  IAM policy changes can take 1-2 minutes to propagate globally"
for i in {90..1}; do
    printf "\r  Waiting: %02d seconds remaining..." "$i"
    sleep 1
done
printf "\r  Waiting: Complete!                    \n"
echo ""

# Step 4: Attempt stack deletion
echo "Step 4: Attempting stack deletion..."
aws cloudformation delete-stack \
  --stack-name "$STACK_NAME" \
  --region "$REGION"

echo "✓ Delete-stack command submitted"
echo ""

# Step 5: Wait for deletion to complete
echo "Step 5: Waiting for deletion to complete..."
echo "  This may take several minutes..."
echo ""

if aws cloudformation wait stack-delete-complete \
  --stack-name "$STACK_NAME" \
  --region "$REGION" 2>&1; then
    echo ""
    echo "✓✓✓ SUCCESS! Stack deleted successfully with corrected IAM policy."
    echo ""
    echo "Next steps:"
    echo "1. Update template.yaml with the fix (see TROUBLESHOOTING_GUIDE.md)"
    echo "2. Redeploy: sam build && sam deploy --guided"
    exit 0
else
    echo ""
    echo "✗ Stack deletion still failed. Checking latest error..."
    echo ""
    
    # Get latest failure reason
    LATEST_ERROR=$(aws cloudformation describe-stack-events \
      --stack-name "$STACK_NAME" \
      --region "$REGION" \
      --max-items 1 \
      --query 'StackEvents[?ResourceStatus==`DELETE_FAILED`] | [0].ResourceStatusReason' \
      --output text)
    
    echo "  Latest error: $LATEST_ERROR"
    echo ""
    
    # Try manual bucket notification cleanup as final fallback
    echo "Step 6: Attempting manual bucket notification cleanup..."
    if aws s3api put-bucket-notification-configuration \
      --bucket "$BUCKET_NAME" \
      --notification-configuration '{}' \
      --region "$REGION"; then
        echo "✓ Bucket notification cleared manually"
        echo ""
        echo "Step 7: Final deletion attempt..."
        
        aws cloudformation delete-stack \
          --stack-name "$STACK_NAME" \
          --region "$REGION"
        
        if aws cloudformation wait stack-delete-complete \
          --stack-name "$STACK_NAME" \
          --region "$REGION" 2>&1; then
            echo ""
            echo "✓✓✓ SUCCESS! Stack deleted after manual cleanup."
            exit 0
        fi
    fi
    
    echo ""
    echo "✗ Unable to delete stack automatically."
    echo ""
    echo "Manual steps required:"
    echo "1. Check AWS Console for detailed error messages"
    echo "2. Try deleting the BucketNotificationCustom resource manually"
    echo "3. If needed, contact AWS Support"
    exit 1
fi
