import json
import re


def parse_json_response(raw: str) -> dict:
    """LLMs occasionally wrap JSON in prose or code fences — extract the first
    {...} block defensively rather than trusting raw output to be valid JSON."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    raise ValueError(f"Could not parse JSON from LLM response: {raw[:300]}")
