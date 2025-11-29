"""Utilities for generating pre-signed uploads for chat exports."""

import os
from datetime import datetime, timezone
from typing import Tuple

import boto3

s3_client = boto3.client("s3")
UPLOAD_BUCKET = os.environ.get("RAW_CONVERSATION_BUCKET")


def build_import_key(user_id: str, prefix: str = "imports") -> Tuple[str, str]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    import_id = timestamp
    key = f"{prefix}/{user_id}/{import_id}.json"
    return key, import_id


def create_presigned_post(user_id: str, content_type: str = "application/json") -> dict:
    if not UPLOAD_BUCKET:
        raise ValueError("RAW_CONVERSATION_BUCKET env var is not set")

    key, import_id = build_import_key(user_id)

    conditions = [
        {"Content-Type": content_type},
        ["content-length-range", 1, 50 * 1024 * 1024],
    ]

    presigned = s3_client.generate_presigned_post(
        Bucket=UPLOAD_BUCKET,
        Key=key,
        Fields={"Content-Type": content_type},
        Conditions=conditions,
        ExpiresIn=900,
    )

    return {
        "import_id": import_id,
        "bucket": UPLOAD_BUCKET,
        "key": key,
        "presigned": presigned,
    }
