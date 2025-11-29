#!/bin/bash
# CloudFormation Stack Deletion Fix Script
# Resolves IAM propagation issues with BucketNotificationHandler

set -e

STACK_NAME="RIJG-MVP"
REGION="us-east-2"
ROLE_NAME="RIJG-MVP-BucketNotificationHandlerRole-Lxk9rBqorWH5"
BUCKET_NAME="rijg-mvp-rawconversationbucket-02po9m9cfieg"
POLICY_NAME="AllowBucketNotificationsDelete"

echo "=========================================="
echo "CloudFormation Stack Deletion Fix"
echo "=========================================="
echo ""

# Step 1: Verify the policy exists
echo "Step 1: Verifying IAM policy is attached..."
if aws iam get-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "$POLICY_NAME" \
    --region "$REGION" > /dev/null 2>&1; then
    echo "✓ Policy '$POLICY_NAME' is attached to role"
    echo ""
    echo "Policy details:"
    aws iam get-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-name "$POLICY_NAME" \
        --region "$REGION" \
        --query 'PolicyDocument' \
        --output json
    echo ""
else
    echo "✗ Policy not found. This script expects the policy to already be attached."
    echo "  Please attach the policy first and re-run this script."
    exit 1
fi

# Step 2: Wait for IAM propagation
echo "Step 2: Waiting for IAM propagation (60 seconds)..."
echo "  IAM changes can take up to 2 minutes to propagate globally."
for i in {60..1}; do
    printf "\r  Waiting: %02d seconds remaining..." "$i"
    sleep 1
done
printf "\r  Waiting: Complete!                    \n"
echo ""

# Step 3: Check current stack status
echo "Step 3: Checking current stack status..."
STACK_STATUS=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].StackStatus' \
    --output text 2>/dev/null || echo "DOES_NOT_EXIST")

echo "  Current status: $STACK_STATUS"
echo ""

if [ "$STACK_STATUS" = "DOES_NOT_EXIST" ]; then
    echo "✓ Stack does not exist - no deletion needed!"
    exit 0
fi

# Step 4: Attempt stack deletion
echo "Step 4: Attempting stack deletion..."
echo "  This will try to delete the stack normally first."
echo ""

if aws cloudformation delete-stack \
    --stack-name "$STACK_NAME" \
    --region "$REGION"; then
    echo "✓ Delete-stack command submitted"
    echo ""
    echo "Step 5: Waiting for deletion to complete..."
    echo "  This may take several minutes..."
    echo ""
    
    if aws cloudformation wait stack-delete-complete \
        --stack-name "$STACK_NAME" \
        --region "$REGION" 2>&1; then
        echo ""
        echo "✓✓✓ SUCCESS! Stack deleted successfully."
        exit 0
    else
        echo ""
        echo "✗ Stack deletion failed. Checking error..."
        echo ""
    fi
else
    echo "✗ Failed to submit delete-stack command"
    exit 1
fi

# Step 6: If deletion failed, check the error
echo "Step 6: Analyzing deletion failure..."
FAILURE_REASON=$(aws cloudformation describe-stack-events \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --max-items 1 \
    --query 'StackEvents[?ResourceStatus==`DELETE_FAILED`] | [0].ResourceStatusReason' \
    --output text)

echo "  Failure reason: $FAILURE_REASON"
echo ""

# Step 7: Manual notification cleanup if still AccessDenied
if [[ "$FAILURE_REASON" == *"AccessDenied"* ]] || [[ "$FAILURE_REASON" == *"PutBucketNotification"* ]]; then
    echo "Step 7: AccessDenied detected - clearing bucket notification manually..."
    echo "  This bypasses the custom resource that's failing."
    echo ""
    
    if aws s3api put-bucket-notification-configuration \
        --bucket "$BUCKET_NAME" \
        --notification-configuration '{}' \
        --region "$REGION"; then
        echo "✓ Bucket notification configuration cleared"
        echo ""
        
        echo "Step 8: Retrying stack deletion..."
        aws cloudformation delete-stack \
            --stack-name "$STACK_NAME" \
            --region "$REGION"
        
        echo "  Waiting for deletion..."
        if aws cloudformation wait stack-delete-complete \
            --stack-name "$STACK_NAME" \
            --region "$REGION" 2>&1; then
            echo ""
            echo "✓✓✓ SUCCESS! Stack deleted after manual cleanup."
            exit 0
        else
            echo ""
            echo "✗ Still failed. Manual intervention required."
            echo ""
            echo "Next steps:"
            echo "1. Check CloudFormation console for specific errors"
            echo "2. Try deleting individual resources manually"
            echo "3. Contact AWS Support if the issue persists"
            exit 1
        fi
    else
        echo "✗ Failed to clear bucket notification"
        echo "  You may need to do this manually in the AWS console."
        exit 1
    fi
else
    echo "Step 7: Different error detected (not AccessDenied)"
    echo "  Please review the error above and take appropriate action."
    echo ""
    echo "  Common fixes:"
    echo "  - Delete resources manually that are blocking stack deletion"
    echo "  - Check for resources with deletion protection enabled"
    echo "  - Verify all dependencies are resolved"
    exit 1
fi
