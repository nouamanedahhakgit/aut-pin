"""Parse multi-line Groq keys from generate-article payload (mirrors multi-domain-clean/keyutil)."""


def normalize_api_key_paste(raw):
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
