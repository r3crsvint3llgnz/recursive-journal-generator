# recursive-journal-generator

Recursive Intelligence Journal Generator (RIJG) is an automated serverless pipeline that distills raw LLM conversation logs into high-signal, first-person Markdown journal entries for Obsidian. Powered by Python, AWS Lambda, and Gemini/Bedrock.

## Project Docs
- `docs/PRODUCT_REQUIREMENTS.md` – Product requirements + MVP scope.
- `docs/FRONTEND_SETUP.md` – Amplify React shell setup instructions.
- `docs/IMPORT_PIPELINE.md` – ChatGPT export import flow, resources, and data model.

## Key Directories
- `src/` – Lambda handlers, conversation parsing, template rendering, Gemini integration.
- `frontend/` – Amplify-ready React shell for uploads and journaling.
- `templates/` – Obsidian Markdown template consumed by the renderer.

## Getting Started
1. **Backend:** Use the SAM template (`template.yaml`) to deploy Lambda functions, DynamoDB tables, and the S3 uploads bucket.
2. **Frontend:** Follow `docs/FRONTEND_SETUP.md` to initialize Amplify, configure Cognito auth, and run `npm run dev`.
3. **Import Pipeline:** Request a pre-signed upload target from `/imports/upload-url` (requires Cognito-authenticated caller), upload the export to the `RawConversationBucket`, and let the `ConversationImportFunction` normalize data into DynamoDB.
