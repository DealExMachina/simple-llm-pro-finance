import json
from typing import Any, Tuple


def try_parse_json(text: str) -> Tuple[bool, Any]:
    if text is None:
        return False, "Input is None"
    
    try:
        return True, json.loads(text)
    except Exception:
        # naive repair: strip markdown fences if present
        t = text.strip()
        if t.startswith("```") and t.endswith("```"):
            t = t.strip("`\n ")
        try:
            return True, json.loads(t)
        except Exception as e:
            return False, str(e)


