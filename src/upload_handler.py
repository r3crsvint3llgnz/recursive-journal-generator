"""Lambda handler returning pre-signed upload targets for chat exports."""

import json
from typing import Any, Dict

from src.upload_service import create_presigned_post


class UnauthorizedError(Exception):
    pass


def _extract_user_id(event: Dict[str, Any]) -> str:
    identity = event.get("requestContext", {}).get("authorizer", {})
    claims = identity.get("jwt", {}).get("claims") or identity.get("claims")
    if not claims:
        raise UnauthorizedError("Missing identity claims")

    return claims.get("sub") or claims.get("cognito:username")


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
        request_body = event.get("body") or "{}"
        body = json.loads(request_body) if isinstance(request_body, str) else request_body
        content_type = body.get("content_type", "application/json")
        result = create_presigned_post(user_id, content_type=content_type)
    except Exception as exc:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "upload_init_failed", "message": str(exc)}),
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(result),
    }
