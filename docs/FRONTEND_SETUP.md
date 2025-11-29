# Frontend Setup – Amplify Shell

This document explains how to bootstrap and run the Amplify-powered React shell inside `frontend/`.

## 1. Prerequisites
- Node.js 18+
- Amplify CLI (`npm install -g @aws-amplify/cli`)
- AWS credentials with permissions to provision Cognito, AppSync/API Gateway, and hosting resources

## 2. Install Dependencies
```bash
cd frontend
npm install
```

Create a `.env.local` (or use `VITE_` vars in your CI) defining the API Gateway base URL that exposes the Lambda routes:

```bash
echo "VITE_API_BASE_URL=https://example.execute-api.us-east-1.amazonaws.com/Prod" > .env.local
```
This value powers the pre-signed upload flow on the dashboard.

## 3. Initialize Amplify Backend
```bash
amplify init
```
Recommended answers:
- **Default editor:** your choice
- **Type:** `javascript`
- **Framework:** `react`
- **Source directory:** `src`
- **Build command:** `npm run build`
- **Start command:** `npm run dev`

## 4. Add Authentication
```bash
amplify add auth
```
Choose the `Default configuration with Social Provider` option if you want Google sign-in like the placeholder UI, or select email/password for MVP. After configuration, run `amplify push` to create the Cognito resources. The CLI generates an `aws-exports.js` file—copy/replace the placeholder located at `frontend/src/aws-exports.js`.

## 5. Optional Hosting
To take advantage of Amplify Hosting:
```bash
amplify add hosting
amplify publish
```

## 6. Running Locally
```bash
npm run dev
```
Visit `http://localhost:5173`.

## 7. Next Steps
1. Wire API routes for imports and journal generation.
2. Replace dashboard placeholders with live data from DynamoDB/Lambda.
3. Implement chat UI + Markdown preview components per PRD.
