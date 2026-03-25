"""API key parsing (multi-line Groq keys, etc.)."""


def normalize_api_key_paste(raw):
    """Strip paste artifacts (newlines, quotes, Bearer) from a single key."""
    if raw is None:
        return ""
    s = str(raw).strip()
    if not s:
        return ""
    s = s.splitlines()[0].strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        s = s[1:-1].strip()
    low = s.lower()
    if low.startswith("authorization:"):
        s = s.split(":", 1)[-1].strip()
        low = s.lower()
    if low.startswith("bearer "):
        s = s[7:].strip()
    return s


def parse_groq_api_keys(raw):
    """
    Parse one or more Groq API keys from DB / profile field.
    Accepts newline-separated and/or comma-separated lines; returns non-empty normalized strings.
    """
    if raw is None:
        return []
    if isinstance(raw, list):
        out = []
        for x in raw:
            n = normalize_api_key_paste(x)
            if n:
                out.append(n)
        return out
    text = str(raw).replace("\r\n", "\n").replace("\r", "\n")
    out = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        for part in line.split(","):
            n = normalize_api_key_paste(part)
            if n:
                out.append(n)
    return out
