"""Custom resource handler to wire S3 bucket notifications to a Lambda."""

import json
from urllib import request

import boto3

s3 = boto3.client("s3")


def _send_response(event, context, status, data=None, reason=None):
    response_body = {
        "Status": status,
        "Reason": reason or "See CloudWatch Logs for details.",
        "PhysicalResourceId": event.get("PhysicalResourceId", context.log_stream_name),
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
        "Data": data or {},
    }

    encoded = json.dumps(response_body).encode("utf-8")
    req = request.Request(event["ResponseURL"], data=encoded, method="PUT")
    req.add_header("Content-Type", "application/json")
    req.add_header("Content-Length", str(len(encoded)))
    request.urlopen(req)


def lambda_handler(event, context):
    request_type = event.get("RequestType")
    props = event.get("ResourceProperties", {})
    bucket = props.get("BucketName")
    lambda_arn = props.get("LambdaArn")

    try:
        if request_type in ("Create", "Update"):
            s3.put_bucket_notification_configuration(
                Bucket=bucket,
                NotificationConfiguration={
                    "LambdaFunctionConfigurations": [
                        {
                            "LambdaFunctionArn": lambda_arn,
                            "Events": ["s3:ObjectCreated:*"]
                        }
                    ]
                },
            )
        elif request_type == "Delete":
            s3.put_bucket_notification_configuration(
                Bucket=bucket,
                NotificationConfiguration={},
            )

        _send_response(event, context, "SUCCESS", {"Bucket": bucket})
    except Exception as exc:  # pragma: no cover
        _send_response(event, context, "FAILED", reason=str(exc))
        raise
