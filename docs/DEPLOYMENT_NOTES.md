# Deployment Notes

## Cleanup Between Attempts
- If CloudFormation rolls back, delete the stack with `aws cloudformation delete-stack --stack-name RIJG-MVP --region us-east-2`.
- Empty and delete the SAM-managed bucket (`aws-sam-cli-managed-default-*`) if the delete fails due to existing objects.
- The raw conversation bucket is created with a random suffix; remove it (and clear its notification configuration) before rerunning `sam deploy`.

## Parameters
- `GeminiApiKey` – currently passed via `sam deploy --guided`. Plan to move this into Secrets Manager and reference it from Lambda.
- `UserPoolArn` / `UserPoolAudience` – use the Cognito User Pool ARN and app client ID from Amplify. Keep `samconfig.toml` updated.

## Template Notes
- `BucketNotificationHandler` requires `AWSLambdaBasicExecutionRole` plus explicit `s3:PutBucketNotificationConfiguration` and `s3:GetBucketNotificationConfiguration` permissions. Without them, the custom resource fails and the stack rolls back.
- `BucketNotificationCustom` depends on both `ConversationImportBucketPermission` and `BucketNotificationHandler` to ensure the bucket exists and the handler role is ready.

## Frontend After Deployment
- Update/create `frontend/.env.local` with `VITE_API_BASE_URL=<JournalApiUrl root>`.
- Replace `frontend/src/aws-exports.js` with Amplify’s generated config so the React app points at the correct region/user pool.
- From `frontend/`, run `npm install` (first time) and `npm run dev` to launch Vite locally.

## Smoke Test Checklist
1. `cd frontend && npm run dev`.
2. Sign in via Amplify.
3. Upload a sample ChatGPT export.
4. Confirm `/imports/status` shows the new import and DynamoDB entries exist.
