import json
import re
from datetime import datetime

PREFIX = "COMMIT_HISTORY_"
_HEX_RE = re.compile(r"[0-9a-fA-F]{7,40}")

def parse_commit_history(archives_dir):
    files = sorted(archives_dir.glob(f"{PREFIX}*.jsonl"))
    if not files:
        raise FileNotFoundError(archives_dir / f"{PREFIX}*.jsonl")
    commits = {}
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            try:
                iso = datetime.fromisoformat(d["iso"])
            except (KeyError, TypeError, ValueError):
                continue
            c = commits.setdefault(d["sha"], {
                "iso": iso,
                "title": d.get("title", ""),
                "author": d.get("author", ""),
                "sha": d["sha"],
                "branches": [],
            })
            if d["branch"] not in c["branches"]:
                c["branches"].append(d["branch"])
    return list(commits.values())

def find_commit(stem, commits):
    tokens = [t.lower() for t in _HEX_RE.findall(stem)]
    matches = [
        c for c in commits for t in tokens
        if t.startswith(c["sha"].lower()) or c["sha"].lower().startswith(t)
    ]
    return max(matches, key=lambda c: c["iso"]) if matches else None

def commit_dates_for_archives(archives_dir):
    commits = parse_commit_history(archives_dir)
    return {z.stem: find_commit(z.stem, commits) for z in sorted(archives_dir.glob("*.zip"))}

def date_for_zip(zip_path, archives_dir):
    commit = find_commit(zip_path.stem, parse_commit_history(archives_dir))
    return commit["iso"] if commit else None

def write_all_commits(archives_dir, out_path):
    commits = sorted(parse_commit_history(archives_dir), key=lambda c: c["iso"])
    with out_path.open("w", encoding="utf-8") as f:
        for c in commits:
            line = {**c, "iso": c["iso"].isoformat()}
            f.write(json.dumps(line, ensure_ascii=False, separators=(",", ":")) + "\n")
    return commits
