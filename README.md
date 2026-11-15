<div align="center">
  <h1>rai.gk</h1>

  <p>
    <strong>Repository Activity Inspector.</strong>
    <br>
    Recover the full commit history of a GitLab repository in minutes, then scan its ZIP archives without extracting them and generate JSONL records ready to feed into an AI model.
  </p>

  <p>
    <img src="https://img.shields.io/badge/release-v0.3.0-white" alt="Release v0.3.0">
    <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License">
  </p>

  <p>
    <strong>Detects</strong><br><br>
    <img src="https://img.shields.io/badge/Node.js-339933?logo=node.js&logoColor=white" alt="Node.js">
    <img src="https://img.shields.io/badge/npm-CB3837?logo=npm&logoColor=white" alt="npm">
    <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker">
  </p>

  <p>
    <a href="#installation">Installation</a>&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="#usage">Usage</a>&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="#data-formats">Data formats</a>&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="LICENSE">License</a>
  </p>

  <br>
</div>

**rai.gk** is the first building block of a pipeline designed to give developers credit for work done in private repositories. Client projects, NDAs, GitLab-only projects, deleted repositories. Work that never appears on their public GitHub contribution graph, despite being real, dated and shippable.

It works in two steps:

1. **Commit history (GitLab).** A browser script walks through every page of a branch's commit list and exports the complete history (SHA, date, author, title, branch) to a JSONL file.
2. **Archive scan (optional).** A Python script merges every exported history into `all_commits.jsonl`, then audits ZIP exports of the repository without extracting them, matches each archive to its commit, and writes one record per archive to `reports.jsonl`.

Run step 1 first: without the commit history, records have no date, author or branch, and the context fed to the LLM is incomplete.

This provides the raw material for a later step: turning private development history into a dated, legitimate record of the work actually done.

## Installation

Just skip this part ! No third-party dependency is required; the project only relies on the Python standard library. The browser script runs directly in the console. No virtual environment is needed either.

## Project structure

```
.
├── scripts/            # main.py, utils_*.py, gitlab-commits-to-json.js
├── archives/           # your ZIPs and COMMIT_HISTORY_*.jsonl files
├── all_commits.jsonl   # every commit, deduplicated by SHA, oldest first
└── reports.jsonl       # one record per archive
```

## Usage

### Step 1: Export the commit history from GitLab

1. Open the commits page of your project with 100 commits per page (replace the placeholder with your own project):

   ```
   https://gitlab.com/<namespace>/<project>/-/commits/main?ref_type=heads&page_size=100
   ```

2. Open the browser developer tools (right click → Inspect → **Console**).
3. Paste the content of `scripts/gitlab-commits-to-json.js` and press Enter.
   If the browser blocks pasting, type `allow pasting` in the console, press Enter, then paste again.
4. Most repositories have several branches. Set the branch to export at the top of the script:

   ```js
   const BRANCH_NAME = 'main';
   ```

   If you are not already on that branch's commits page, the script navigates to it. Re-run it once the page has loaded.
5. The script clicks through every page with random 3-6 second pauses, then downloads `COMMIT_HISTORY_<branch>.jsonl`.
6. Repeat for each branch you want, then move all the `COMMIT_HISTORY_*.jsonl` files into `archives/` (at the project root).

Notes:
- Progress is saved in `localStorage`, so an interrupted run resumes where it stopped.
- You can export at any time from the console with `window.__commitScrape.download()`.
- The real branch name is stored in each line (`"branch"`). Only the file name replaces `/` with `_` (`feature/foo` → `COMMIT_HISTORY_feature_foo.jsonl`).

### Step 2: Build the commit list and scan the archives

1. Optionally, download the repository ZIPs from GitLab (one per commit or branch state you want to analyze) and place them in `archives/`, next to the `COMMIT_HISTORY_*.jsonl` files. The ZIP file name must contain the commit SHA, which is the case for GitLab's default export names.
2. Run:

   ```bash
   python scripts/main.py
   ```

This produces:
- `all_commits.jsonl`: all commits from every `COMMIT_HISTORY_*.jsonl`, deduplicated by SHA, sorted oldest to newest, with the `branches` of each commit merged. Generated even without any ZIP.
- `reports.jsonl`: one record per ZIP archive.

Without any `COMMIT_HISTORY_*.jsonl`, `all_commits.jsonl` is not created and records are still generated, but `date`, `author`, `title` and `branches` stay empty.

## What it extracts

| Source                    | Extracted data                                                  |
| -------------------------- | ---------------------------------------------------------------- |
| GitLab commit list         | SHA, authored date, author and title of every commit, per branch |
| Archive content            | Every file name and folder name (names only, not full paths)     |
| `package.json`              | All `dependencies` and `devDependencies` names, deduplicated     |
| `docker-compose.yml` / `.yaml`, `compose.yml` / `.yaml` | All service names, with `container_name` when declared |
| `requirements.txt`          | All Python package names, deduplicated                           |

## Data formats

Everything is JSONL: one JSON object per line. Lists and dicts stay native (no flattening, no loss), and files can be streamed, appended to and concatenated without reparsing.

### Commit history

`archives/COMMIT_HISTORY_<branch>.jsonl`, one line per commit:

```json
{"sha":"a1b2c3d4...","iso":"2025-03-12T14:02:11+01:00","author":"...","title":"...","branch":"main"}
```

### All commits

`all_commits.jsonl`, one line per unique SHA. Same fields, but `branch` becomes a `branches` list:

```json
{"iso":"2025-03-12T14:02:11+01:00","title":"...","author":"...","sha":"a1b2c3d4...","branches":["main","development"]}
```

### Record

`reports.jsonl`, one line per archive. `id` is the commit SHA when the archive matches a commit, otherwise the archive name. Shown indented here for readability:

```json
{
  "id": "a1b2c3d4",
  "name": "project-main-a1b2c3d4",
  "date": "2025-03-12T14:02:11+01:00",
  "author": "...",
  "title": "...",
  "branches": ["main", "development"],
  "counts": { "files": 1200, "unique_files": 340, "dirs": 210, "unique_dirs": 95 },
  "npm": ["react", "next"],
  "docker": { "db": "postgres_container" },
  "python": ["flask"],
  "dirs": ["src", "components"],
  "files": ["page.tsx", "layout.tsx"]
}
```

`counts.files` and `counts.dirs` include everything in the archive. `unique_files` and `unique_dirs` match the deduplicated lists, after exclusions for files.

For LLM input, send a reduced view (only the fields you need) rather than the full records, since file and dir lists dominate the token cost.

## Customization

Edit `scripts/utils_exclusions.py` to hide more files from records. Hidden files are still counted in `counts.files`. The following are excluded by default:

- Fonts, images and videos, by extension
- Source maps and `.frm` files
- Names ending with `_fsm` or `_vm`
- Purely numeric names (`1214`, `1232`...)

## License

MIT. See [`LICENSE`](LICENSE).