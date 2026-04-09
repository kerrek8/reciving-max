import html
import json

MAX_LEN = 4000


def format_payload(payload: dict) -> list[str]:
    raw = json.dumps(payload, indent=2, ensure_ascii=False)
    escaped = html.escape(raw)

    return [escaped[i:i + MAX_LEN] for i in range(0, len(escaped), MAX_LEN)]