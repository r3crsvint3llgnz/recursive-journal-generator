import json

import pytest

from src import import_pipeline


@pytest.fixture
def sample_conversation():
    return {
        "id": "conv-123",
        "title": "Sample",
        "create_time": 1700000000,
        "mapping": {
            "root": {"id": "root", "message": None, "parent": None, "children": ["u1"]},
            "u1": {
                "id": "u1",
                "message": {
                    "id": "u1",
                    "author": {"role": "user"},
                    "create_time": 1700000000,
                    "content": {"content_type": "text", "parts": ["How are you?"]},
                },
                "parent": "root",
                "children": ["a1"],
            },
            "a1": {
                "id": "a1",
                "message": {
                    "id": "a1",
                    "author": {"role": "assistant"},
                    "create_time": 1700000001,
                    "content": {"content_type": "text", "parts": ["Doing well"]},
                },
                "parent": "u1",
                "children": [],
            },
        },
    }


def test_extract_user_and_import_from_key():
    user_id, import_id = import_pipeline.extract_user_and_import_from_key(
        "imports/user-42/20240101T101010Z.json"
    )
    assert user_id == "user-42"
    assert import_id == "20240101T101010Z"


def test_coerce_conversations_from_dict(sample_conversation):
    convs = import_pipeline.coerce_conversations(sample_conversation)
    assert len(convs) == 1
    assert convs[0]["id"] == "conv-123"


def test_build_conversation_items(sample_conversation):
    items, failures = import_pipeline.build_conversation_items([sample_conversation], "user-42", "import-1")
    assert not failures
    assert items[0]["user_id"] == "user-42"
    assert items[0]["import_id"] == "import-1"
    assert items[0]["conversation_id"] == "conv-123"
    assert items[0]["sort_key"].startswith(items[0]["date"])


def test_parse_json_payload_valid():
    body = json.dumps({"hello": "world"}).encode("utf-8")
    data = import_pipeline.parse_json_payload(body)
    assert data["hello"] == "world"


def test_parse_json_payload_invalid():
    with pytest.raises(ValueError):
        import_pipeline.parse_json_payload(b"not json")
