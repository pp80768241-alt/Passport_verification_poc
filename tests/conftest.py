import base64
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def synthetic_image_base64() -> str:
    # Minimal synthetic PNG bytes generated for tests only.
    png_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    )
    return base64.b64encode(png_bytes).decode("ascii")


def build_event(body: dict[str, object] | str | None) -> dict[str, object]:
    if isinstance(body, dict):
        body_value: dict[str, object] | str | None = json.dumps(body)
    else:
        body_value = body

    return {
        "version": "2.0",
        "routeKey": "POST /verify-passport",
        "rawPath": "/verify-passport",
        "requestContext": {"http": {"method": "POST", "path": "/verify-passport"}},
        "body": body_value,
        "isBase64Encoded": False,
    }
