# Conversation Import Pipeline (MVP)

This document explains how ChatGPT JSON exports move from the web client into normalized conversation records.

## 1. Flow Overview
1. **Upload** – The frontend requests a pre-signed URL from `/imports/upload-url`. The Lambda reads the authenticated user ID, generates a key under `imports/<user_id>/<import_id>.json`, and returns the S3 target plus form fields. The client uploads directly via the provided POST fields.
2. **S3 Event Trigger** – When the object lands in the bucket, S3 emits an event that invokes `ConversationImportFunction`.
3. **Normalization** – The Lambda downloads the JSON, iterates each conversation, and reuses `parse_conversation` to extract metadata, transcript, and clean text.
4. **Storage** – Normalized entries are written to the `RIJG-Conversations` DynamoDB table with per-user partition keys so downstream services can query imports quickly.
5. **Status Updates** – The handler returns a summary payload that can be surfaced in CloudWatch logs (total processed, skipped, failures). A future iteration can push these metrics to a notification topic for the UI.

## 2. AWS Resources
- `RawConversationBucket` – Stores uploaded exports. Versioning disabled for MVP, but server-side encryption is on by default. Objects must use the `imports/<user_id>/...` prefix so the handler can infer the owner.
- `UploadRequestFunction` – API-driven Lambda defined in `src/upload_handler.py`. Generates pre-signed URLs for authenticated users.
- `ConversationImportFunction` – Python Lambda defined in `src/import_handler.py`. Triggered by S3 `ObjectCreated:*` events.
- `RIJG-Conversations` table – DynamoDB table keyed by `user_id` (partition) and `sort_key` (format: `date#conversation_id`). Stores normalized metadata plus raw/transcript fields for later rendering.

## 3. Data Model
Example item:
```
{
  "user_id": "user-123",
  "sort_key": "2025-01-10#689a7dbf-fcf4-832b-81b3-c31df0b4b921",
  "conversation_id": "689a7dbf-fcf4-832b-81b3-c31df0b4b921",
  "import_id": "20250110T153000Z",
  "title": "Recursive prompting plan",
  "date": "2025-01-10",
  "time": "15:30",
  "transcript": "**User:** ...",
  "raw_text": "User: ...",
  "status": "parsed",
  "created_at": "2025-01-10T15:31:04Z"
}
```

## 4. Error Handling
- If the JSON payload is invalid, the handler logs the failure and raises so the event is retried.
- Individual conversation failures are logged and skipped while the batch continues processing. Failed conversation IDs are returned in the summary.
- If the object key does not contain a user ID (missing prefix), the event is rejected to avoid orphaned data.

## 5. TODO Hooks
- ~~Add an API route to mint pre-signed URLs tied to the authenticated user ID.~~ ✅ Implemented via `/imports/upload-url`.
- Persist import job status so the frontend can show progress.
- Support ZIP archives (currently JSON only).
- Optional: Move transcripts to S3 and store references once we exceed Dynamo item limits.
