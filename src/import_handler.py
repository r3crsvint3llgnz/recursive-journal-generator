"""Lambda handler for processing uploaded conversation exports."""

import json
import os
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

from src.import_pipeline import (
    build_conversation_items,
    coerce_conversations,
    extract_user_and_import_from_key,
    parse_json_payload,
)

s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
conversation_table = dynamodb.Table(
    os.environ.get("CONVERSATION_TABLE_NAME", "RIJG-Conversations")
)


def _process_record(record: Dict[str, Any]) -> Dict[str, Any]:
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    user_id, import_id = extract_user_and_import_from_key(key)

    try:
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        payload = parse_json_payload(obj["Body"].read())
    except ClientError as exc:
        raise RuntimeError(f"Unable to fetch object s3://{bucket}/{key}: {exc}") from exc

    conversations = coerce_conversations(payload)
    items, failures = build_conversation_items(conversations, user_id, import_id)

    with conversation_table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

    return {
        "bucket": bucket,
        "key": key,
        "user_id": user_id,
        "import_id": import_id,
        "processed": len(conversations),
        "stored": len(items),
        "failures": failures,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    records = event.get("Records", [])
    if not records:
        raise ValueError("No records to process")

    summaries = []
    for record in records:
        summary = _process_record(record)
        summaries.append(summary)
        print(json.dumps(summary))  # Structured log for observability

    total_processed = sum(s["processed"] for s in summaries)
    total_stored = sum(s["stored"] for s in summaries)
    all_failures = [failure for s in summaries for failure in s["failures"]]

    return {
        "processed": total_processed,
        "stored": total_stored,
        "failures": all_failures,
        "records": summaries,
    }
