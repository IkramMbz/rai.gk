import json
from datetime import datetime
from utils_zip import extract_names
from utils_exclusions import is_excluded
from utils_tech import scan_tech

# npm scopes to hide from the public report, e.g. ("@client/", "@acme/")
PRIVATE_SCOPES = ()

def build_record(name, files, dirs, npm_deps, docker_services, python_deps, commit=None):
    visible_files = sorted({f for f in files if not is_excluded(f)})
    unique_dirs = sorted(set(dirs))
    return {
        "id": commit["sha"] if commit else name,
        "name": name,
        "date": commit["iso"].isoformat() if commit else None,
        "author": commit["author"] if commit else None,
        "title": commit["title"] if commit else None,
        "branches": commit["branches"] if commit else [],
        "counts": {
            "files": len(files),
            "unique_files": len(visible_files),
            "dirs": len(dirs),
            "unique_dirs": len(unique_dirs),
        },
        "npm": npm_deps,
        "docker": docker_services,
        "python": python_deps,
        "dirs": unique_dirs,
        "files": visible_files,
    }

def build_public_record(index, r):
    return {
        "index": index,
        "date": r["date"][:10] if r["date"] else None,
        "npm": [p for p in r["npm"] if not p.startswith(PRIVATE_SCOPES)],
        "python": r["python"],
        "docker": sorted(r["docker"]),
    }

def process_zip(zip_path, commit=None):
    files, dirs = extract_names(zip_path)
    dirs = [d for d in dirs if d != zip_path.stem]
    npm_deps, docker_services, python_deps = scan_tech(zip_path)
    return build_record(zip_path.stem, files, dirs, npm_deps, docker_services, python_deps, commit)

def sort_key(r):
    return (r["date"] is None, datetime.fromisoformat(r["date"]) if r["date"] else datetime.min)

def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
