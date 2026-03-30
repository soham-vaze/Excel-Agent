def normalize_string(s: str) -> str:
    return s.strip().lower()

def match_value(a: str, b: str) -> bool:
    return normalize_string(a) == normalize_string(b)