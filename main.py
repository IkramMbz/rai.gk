from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils_zip import extract_names
from utils_exclusions import is_excluded
from utils_tech import scan_tech
from utils_commits import commit_dates_for_archives

def build_report(name, files, dirs, npm_deps, docker_services, python_deps, commit=None):
    visible_files = sorted({f for f in files if not is_excluded(f)})
    unique_dirs = sorted(set(dirs))
    date_line = f"Repository date: {commit['iso'].isoformat()}" if commit else "Repository date:"
    branch_line = f"Branch: {', '.join(commit['branches'])}" if commit else "Branch:"
    lines = [f"# {name}", "", date_line, branch_line, ""]
    lines.append(f"- Files found (including duplicates): {len(files)}")
    lines.append(f"- Unique files (after deduplication): {len(visible_files)}")
    lines.append(f"- Directories found (including duplicates): {len(dirs)}")
    lines.append(f"- Unique directories (after deduplication): {len(unique_dirs)}")
    lines.append("")
    if npm_deps:
        lines.append("## NPM Dependencies:")
        lines.extend(npm_deps)
        lines.append("")
    if docker_services:
        lines.append("## Docker Services:")
        for svc, container in docker_services.items():
            lines.append(f"{svc} ({container})" if container else svc)
        lines.append("")
    if python_deps:
        lines.append("## Python Dependencies:")
        lines.extend(python_deps)
        lines.append("")
    lines.append("## Directories:")
    lines.extend(unique_dirs)
    lines.append("")
    lines.append("## Files:")
    lines.extend(visible_files)
    return "\n".join(lines)

def process_zip(zip_path, reports_dir, commit=None):
    files, dirs = extract_names(zip_path)
    dirs = [d for d in dirs if d != zip_path.stem]
    npm_deps, docker_services, python_deps = scan_tech(zip_path)
    report = build_report(zip_path.stem, files, dirs, npm_deps, docker_services, python_deps, commit)
    filename = f"{commit['sha']}.md" if commit else f"{zip_path.stem}.md"
    (reports_dir / filename).write_text(report, encoding="utf-8")

def main():
    script_dir = Path(__file__).resolve().parent
    reports_dir = script_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    archives_dir = script_dir / "archives"
    zip_files = sorted(archives_dir.glob("*.zip"))
    if not zip_files:
        print(0)
        return
    try:
        commit_map = commit_dates_for_archives(archives_dir)
    except FileNotFoundError:
        commit_map = {}
    with ThreadPoolExecutor(max_workers=min(32, len(zip_files))) as executor:
        futures = [executor.submit(process_zip, z, reports_dir, commit_map.get(z.stem)) for z in zip_files]
        for future in as_completed(futures):
            future.result()
    print(f"Total reports generated: {len(zip_files)}.")

if __name__ == "__main__":
    main()
