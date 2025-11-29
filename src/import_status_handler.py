"""Lambda handler to list recent import jobs for a user."""

import json
import os
from typing import Any, Dict

import boto3
from boto3.dynamodb.conditions import Key

conversation_table = boto3.resource("dynamodb").Table(
    os.environ.get("CONVERSATION_TABLE_NAME", "RIJG-Conversations")
)


class UnauthorizedError(Exception):
    pass


def _extract_user_id(event: Dict[str, Any]) -> str:
    identity = event.get("requestContext", {}).get("authorizer", {})
    claims = identity.get("jwt", {}).get("claims") or identity.get("claims")
    if not claims:
        raise UnauthorizedError("Missing identity claims")

    return claims.get("sub") or claims.get("cognito:username")


def _fetch_recent_imports(user_id: str, limit: int = 5):
    response = conversation_table.query(
        KeyConditionExpression=Key("user_id").eq(user_id),
        ProjectionExpression="import_id, title, #st",
        ExpressionAttributeNames={"#st": "status"},
        Limit=limit,
        ScanIndexForward=False,
    )
    items = response.get("Items", [])
    # Deduplicate by import_id while preserving order
    seen = set()
    deduped = []
    for item in items:
        import_id = item.get("import_id")
        if import_id in seen:
            continue
        seen.add(import_id)
        deduped.append(item)
    return deduped


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        user_id = _extract_user_id(event)
    except UnauthorizedError as exc:
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "unauthorized", "message": str(exc)}),
        }

    try:
        results = _fetch_recent_imports(user_id)
    except Exception as exc:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "import_status_failed", "message": str(exc)}),
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"imports": results}),
    }
