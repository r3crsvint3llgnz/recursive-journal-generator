import json

from src import import_handler


def test_lambda_handler_unwraps_sns(monkeypatch):
    processed = []

    def fake_process(record):
        processed.append(record)
        return {
            "bucket": record["s3"]["bucket"]["name"],
            "processed": 1,
            "stored": 1,
            "failures": [],
        }

    monkeypatch.setattr(import_handler, "_process_record", fake_process)

    s3_record = {
        "s3": {
            "bucket": {"name": "test-bucket"},
            "object": {"key": "imports/user/test.json"},
        }
    }

    sns_event = {
        "Records": [
            {
                "EventSource": "aws:sns",
                "Sns": {"Message": json.dumps({"Records": [s3_record]})},
            }
        ]
    }

    response = import_handler.lambda_handler(sns_event, None)

    assert processed, "_process_record should be called"
    assert processed[0]["s3"]["bucket"]["name"] == "test-bucket"
    assert response["processed"] == 1
    assert response["stored"] == 1
