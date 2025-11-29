# Recursive Journal Generator – Product Requirements

## 1. Vision & Goals
- Convert exported or live LLM conversations into reflective, first-person journal entries compatible with Obsidian.
- Provide a guided chat experience where tuned models prompt users to explore feelings, insights, and actions.
- Auto-tag and link outputs for personal knowledge management while protecting user privacy.

## 2. Target Users & Core Scenarios
1. **Importer-Analyst** – Uploads prior ChatGPT/Claude exports to backfill their vault with summarized entries.
2. **Active Journaler** – Chats with a reflective AI companion, then exports Markdown directly into Obsidian.
3. **Insight Seeker** – Filters entries by tag/topic to spot trends and reference past decisions.
4. **Privacy-Conscious User** – Wants transparency, deletion controls, and confidence their conversations stay private.

## 3. Functional Requirements
### 3.1 Conversation Import
- Accept JSON/ZIP exports from major chat providers; validate schema and show import summary (count, size, sample titles).
- Parse tree-structured mappings into chronological transcripts; retain timestamps, speaker roles, and source IDs.
- Enqueue processing jobs (e.g., SQS → Lambda) that convert each conversation into normalized records stored per user.

### 3.2 Chat Front End
- Amplify-hosted SPA with panels for chat, conversation list, tag browser, and Markdown preview.
- Allow users to pick a Bedrock model profile (e.g., coach, analyst) and switch temperature/tone presets.
- Support commands during chat (`/tag`, `/bookmark`, `/summarize`) to shape final journal output.
- Provide inline feedback prompts that encourage reflection (“How did that make you feel?”) without sounding generic.

### 3.3 Journal Generation & Templates
- Render Markdown using the existing `templates/obsidian_journal.md` contract: YAML front matter, discovery section, tag cloud, continuity notes, collapsible transcript.
- Auto-generate tags/topics via LLM or heuristics but allow manual edits before export.
- Export options: download `.md`, copy to clipboard, or push to connected Obsidian vault/sync folder.

### 3.4 Knowledge & Insights
- Tag/topic filters, timeline view, and highlight cards (recurring themes, mood trends, open loops).
- Regenerate entries with alternate prompts (e.g., “short summary,” “action-focused version”).

### 3.5 Privacy & Security
- Per-user authentication via Cognito; conversations bucketed by user with KMS encryption.
- In-transit TLS everywhere; redact logs by default.
- Explicit consent toggles for retaining raw transcripts vs derived journals; one-click deletion cascades.
- No training/fine-tuning on user data unless they opt in; document retention limits.

## 4. Technical Architecture
- **Frontend:** AWS Amplify-hosted React app leveraging Amplify Auth/Storage/Data for API calls.
- **APIs:** API Gateway → Lambda (Python) orchestrating import parsing, Bedrock calls, template rendering.
- **Model Processing:** Amazon Bedrock (preferred models: Claude 3 Sonnet for depth, Haiku for speed). Prompt templates enforce journaling voice and JSON schema.
- **Storage:** DynamoDB for conversations/journal metadata, S3 for raw exports + rendered Markdown, optional OpenSearch for search/analytics.
- **Automation:** Step Functions for import workflows; EventBridge for scheduled insights.

## 5. MVP Scope
1. User auth + secure onboarding flow.
2. Single-provider import (ChatGPT JSON) with batch processing and basic status UI.
3. Chat interface with one tuned Bedrock model profile and markdown preview.
4. Markdown export (download + copy) using existing template, including auto-tagging + manual edit.
5. Basic tag filtering list view.
6. Privacy controls: view/delete data, clear policy copy.

## 6. Success Metrics
- ≥80% of imported conversations successfully convert to Markdown without manual fixes.
- Median generation latency <5 seconds per conversation.
- ≥70% of early testers report that prompts “encourage deeper reflection.”
- Zero P1 privacy incidents; all deletion requests honored within minutes.

## 7. Risks & Mitigations
- **Template packaging issues:** ensure templates live within deployed artifact (mirror in `src/templates`).
- **Credit/accounting race conditions:** enforce atomic decrements in DynamoDB.
- **Model tone drift:** maintain regression prompts + evaluation suite; allow quick prompt updates.
- **Vendor costs:** batch imports, cache tag suggestions, support local/offline processing fallback.

## 8. Open Questions
1. Should we integrate directly with Obsidian (plugin or URI handler) in MVP or rely on manual copy/export?
2. How will we handle non-text attachments from chat exports (images, files)?
3. Do we store only summaries when users disable raw transcript retention?
4. Which taxonomy powers tag suggestions (user-defined vs auto-generated vs hybrid)?
