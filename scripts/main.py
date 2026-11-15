import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from utils_zip import extract_names
from utils_exclusions import is_excluded
from utils_tech import scan_tech
from utils_commits import parse_commit_history, find_commit, write_all_commits

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

def process_zip(zip_path, commit=None):
    files, dirs = extract_names(zip_path)
    dirs = [d for d in dirs if d != zip_path.stem]
    npm_deps, docker_services, python_deps = scan_tech(zip_path)
    return build_record(zip_path.stem, files, dirs, npm_deps, docker_services, python_deps, commit)

def main():
    root = Path(__file__).resolve().parent.parent
    archives_dir = root / "archives"
    try:
        commits = write_all_commits(archives_dir, root / "all_commits.jsonl")
        print(f"Total commits: {len(commits)}.")
    except FileNotFoundError:
        commits = []
    zip_files = sorted(archives_dir.glob("*.zip"))
    if not zip_files:
        return
    with ThreadPoolExecutor(max_workers=min(32, len(zip_files))) as executor:
        records = list(executor.map(lambda z: process_zip(z, find_commit(z.stem, commits)), zip_files))
    with (root / "reports.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"Total records generated: {len(records)}.")

if __name__ == "__main__":
    main()
