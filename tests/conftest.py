import types
import sys

if 'boto3' not in sys.modules:
  boto3_stub = types.SimpleNamespace(resource=lambda *args, **kwargs: types.SimpleNamespace(Table=lambda name: None), client=lambda *args, **kwargs: None)
  sys.modules['boto3'] = boto3_stub

if 'botocore' not in sys.modules:
  botocore_stub = types.SimpleNamespace(exceptions=types.SimpleNamespace(ClientError=Exception))
  sys.modules['botocore'] = botocore_stub
  sys.modules['botocore.exceptions'] = botocore_stub.exceptions
