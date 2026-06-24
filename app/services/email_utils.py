from __future__ import annotations

import re

EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9](?:[a-zA-Z0-9._%+-]*[a-zA-Z0-9])?"
    r"@"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?"
    r"\.[a-zA-Z]{2,}$"
)

# RFC 2606 / reserved — never send real invites here
BLOCKED_EMAIL_DOMAINS = frozenset(
    {
        "example.com",
        "example.net",
        "example.org",
        "test.com",
        "invalid",
        "localhost",
    }
)

DOMAIN_FIXES = {
    "gmailcom": "gmail.com",
    "gmaildotcom": "gmail.com",
    "yahooocom": "yahoo.com",
    "yahoocom": "yahoo.com",
    "hotmailcom": "hotmail.com",
    "outlookcom": "outlook.com",
}

DIGIT_WORDS = {
    "zero": "0",
    "oh": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}


def _convert_spoken_digit_runs(text: str) -> str:
    """singh shashi zero nine eight seven one -> singh shashi 09871"""
    words = text.split()
    out: list[str] = []
    digit_buf: list[str] = []

    def flush_digits() -> None:
        if digit_buf:
            out.append("".join(digit_buf))
            digit_buf.clear()

    for word in words:
        digit = DIGIT_WORDS.get(word.lower())
        if digit is not None:
            digit_buf.append(digit)
        else:
            flush_digits()
            out.append(word)
    flush_digits()
    return " ".join(out)


def normalize_spoken_email(raw: str) -> str:
    """Turn spoken email into a normal address: john at gmail dot com -> john@gmail.com."""
    text = raw.strip().lower()
    text = text.replace("underscore", "_").replace("dash", "-").replace("hyphen", "-")
    text = _convert_spoken_digit_runs(text)

    # Spoken separators before stripping spaces
    text = re.sub(r"\s+at\s+", "@", text, flags=re.I)
    text = re.sub(r"\s+dot\s+", ".", text, flags=re.I)
    text = re.sub(r"\s+point\s+", ".", text, flags=re.I)

    text = re.sub(r"\s*@\s*", "@", text)
    text = re.sub(r"\s*\.\s*", ".", text)
    text = text.replace(" ", "")

    if "@" not in text:
        for bad, good in DOMAIN_FIXES.items():
            if bad in text:
                local, _, domain = text.partition(bad)
                text = f"{local}@{good}"
                break

    local, sep, domain = text.partition("@")
    if sep and domain:
        domain = DOMAIN_FIXES.get(domain.replace(".", ""), domain)
        if "." not in domain and domain in ("gmail", "yahoo", "hotmail", "outlook"):
            domain = f"{domain}.com"
        text = f"{local}@{domain}"

    return text


def validate_email(raw: str) -> dict:
    normalized = normalize_spoken_email(raw)
    if not normalized or "@" not in normalized:
        return {
            "valid": False,
            "normalized": normalized,
            "message": (
                "I couldn't make out a complete email address. "
                "Please ask them to say it again slowly, like 'name at gmail dot com'."
            ),
        }

    domain = normalized.split("@", 1)[1].lower()
    if domain in BLOCKED_EMAIL_DOMAINS:
        return {
            "valid": False,
            "normalized": normalized,
            "message": (
                f"'{normalized}' is not a real inbox. "
                "Ask for their real Gmail or work email address."
            ),
        }

    if not EMAIL_PATTERN.match(normalized):
        return {
            "valid": False,
            "normalized": normalized,
            "message": (
                f"'{normalized}' doesn't look like a valid email. "
                "Read it back to the caller and ask them to confirm or spell it again."
            ),
        }

    local, domain_part = normalized.split("@", 1)
    spoken_back = f"{local} at {domain_part.replace('.', ' dot ')}"
    return {
        "valid": True,
        "normalized": normalized,
        "spoken_back": spoken_back,
        "message": (
            f"Email parsed as {normalized}. "
            f"Read back to caller: '{spoken_back}' and ask 'Is that correct?' "
            "Only book after they say yes."
        ),
    }
