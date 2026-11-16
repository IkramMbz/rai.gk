import json
import re
from utils_records import PRIVATE_SCOPES

SOURCES = ("npm", "python", "docker")
DEFAULTS = {"category": "Frontend", "reason": "", "importance": 0}

def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def detect(records):
    found = {}
    for r in records:
        for source in SOURCES:
            for name in r[source]:
                if source == "npm" and name.startswith(PRIVATE_SCOPES):
                    continue
                slug = slugify(name)
                if slug:
                    found.setdefault((source, slug), name)
    return found

def read_known(path):
    known = set()
    if not path.is_file():
        return known
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            key = (row["source"], row["slug"])
        except (json.JSONDecodeError, KeyError):
            print(f"tech-catalog: malformed line {n}, skipped.")
            continue
        if key in known:
            print(f"tech-catalog: duplicate {key} (line {n}), first one kept.")
        known.add(key)
    return known

def sync_catalog(path, records):
    known = read_known(path)
    missing = {k: n for k, n in detect(records).items() if k not in known}
    if not missing:
        return 0
    lines = "".join(
        json.dumps({"name": name, "slug": slug, "source": source, **DEFAULTS}, ensure_ascii=False) + "\n"
        for (source, slug), name in missing.items()
    )
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    with path.open("a", encoding="utf-8") as f:
        if existing.strip():
            f.write(("" if existing.endswith("\n") else "\n") + "\n\n\n")
        f.write(lines)
    return len(missing)
