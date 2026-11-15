from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from utils_catalog import sync_catalog
from utils_commits import find_commit, write_all_commits
from utils_records import process_zip, build_public_record, sort_key, write_jsonl

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
    records.sort(key=sort_key)

    write_jsonl(root / "reports-full.jsonl", records)
    write_jsonl(root / "reports-public.jsonl", (build_public_record(i, r) for i, r in enumerate(records)))
    added = sync_catalog(root / "tech-catalog.jsonl", records)
    print(f"Tech catalog: {added} technologies added.")
    print(f"Total records generated: {len(records)}.")

if __name__ == "__main__":
    main()
