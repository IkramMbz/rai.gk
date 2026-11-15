import re
from datetime import datetime

PREFIX = "COMMIT_HISTORY_"
_LINE_RE = re.compile(r"^-\s+\*\*(?P<iso>[^*]+?)\*\*\s+[-—]\s+(?P<title>.+?)\s+_\(by\s+(?P<author>.+?),\s+`(?P<sha>[0-9a-fA-F]{7,40})`\)_$")
_HEX_RE = re.compile(r"[0-9a-fA-F]{7,40}")

def parse_commit_history(archives_dir):
    files = sorted(archives_dir.glob(f"{PREFIX}*.md"))
    if not files:
        raise FileNotFoundError(archives_dir / f"{PREFIX}*.md")
    commits = {}
    for md_path in files:
        branch = md_path.stem[len(PREFIX):]
        for raw in md_path.read_text(encoding="utf-8").splitlines():
            m = _LINE_RE.match(raw.strip())
            if not m:
                continue
            try:
                iso = datetime.fromisoformat(m.group("iso"))
            except ValueError:
                continue
            c = commits.setdefault(m.group("sha"), {
                "iso": iso,
                "title": m.group("title").strip(),
                "author": m.group("author").strip(),
                "sha": m.group("sha"),
                "branches": [],
            })
            if branch not in c["branches"]:
                c["branches"].append(branch)
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
