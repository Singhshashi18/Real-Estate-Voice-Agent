"""Print token.json as one-line GOOGLE_TOKEN_JSON for cloud deploy."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
token_path = ROOT / "token.json"

if not token_path.exists():
    print("Run python scripts/setup_google_auth.py first.", file=sys.stderr)
    sys.exit(1)

data = json.loads(token_path.read_text(encoding="utf-8"))
one_line = json.dumps(data, separators=(",", ":"))
print("Add to Render/Railway as env var GOOGLE_TOKEN_JSON:")
print(one_line)
