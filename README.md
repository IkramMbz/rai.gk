<div align="center">
  <h1>rai.gk</h1>

  <p>
    <strong>Repository Activity Inspector.</strong>
    <br>
    Recover the full commit history of a GitLab repository in minutes, then scan its ZIP archives without extracting them and generate per-archive Markdown reports ready to feed into an AI model.
  </p>

  <p>
    <img src="https://img.shields.io/badge/release-v0.2.0-white" alt="Release v0.2.0">
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
    <a href="#report-contents">Report contents</a>&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="LICENSE">License</a>
  </p>

  <br>
</div>

**rai.gk** is the first building block of a pipeline designed to give developers credit for work done in private repositories. Client projects, NDAs, GitLab-only projects, deleted repositories. Work that never appears on their public GitHub contribution graph, despite being real, dated and shippable.

It works in two steps:

1. **Commit history (GitLab).** A browser script walks through every page of a branch's commit list and exports the complete history (date, author, title, SHA) to a Markdown file.
2. **Archive scan (optional, for deeper analysis).** A Python script audits ZIP exports of the repository without extracting them, and matches each archive to its commit to add the exact date and branch(es) to the report.

Running step 1 first matters: without the commit history, the reports have no dates or branches, and the information fed to the LLM is incomplete.

This provides the raw material for a later step: turning private development history into a dated, legitimate record of the work actually done.

## Installation

Just skip this part ! No third-party dependency is required; the project only relies on the Python standard library. The browser script runs directly in the console. No virtual environment is needed either.

## Project structure

```
.
├── scripts/      # main.py, utils_*.py, gitlab-commits-history.js
├── archives/     # your ZIPs and COMMIT_HISTORY_*.md files
└── reports/      # generated reports
```

## Usage

### Step 1: Export the commit history from GitLab

1. Open the commits page of your project with 100 commits per page (replace the placeholder with your own project):

   ```
   https://gitlab.com/<namespace>/<project>/-/commits/main?ref_type=heads&page_size=100
   ```

2. Open the browser developer tools (right click → Inspect → **Console**).
3. Paste the content of `scripts/gitlab-commits-history.js` and press Enter.
   If the browser blocks pasting, type `allow pasting` in the console, press Enter, then paste again.
4. Most repositories have several branches. Set the branch to export at the top of the script:

   ```js
   const BRANCH_NAME = 'main';
   ```

   If you are not already on that branch's commits page, the script navigates to it. Re-run it once the page has loaded.
5. The script clicks through every page with random 3-6 second pauses, then downloads `COMMIT_HISTORY_<branch>.md`.
6. Repeat for each branch you want, then move all the `COMMIT_HISTORY_*.md` files into the `archives/` (folder at the project root).

Notes:
- Progress is saved in `localStorage`, so an interrupted run resumes where it stopped.
- You can export at any time from the console with `window.__commitScrape.download()`.
- A `/` in a branch name becomes `_` in the file name (`feature/foo` → `COMMIT_HISTORY_feature_foo.md`).

### Step 2: Scan the repository archives (optional)

1. Download the repository ZIPs from GitLab (one per commit or branch state you want to analyze) and place them in `archives/`, next to the `COMMIT_HISTORY_*.md` files. The ZIP file name must contain the commit SHA, which is the case for GitLab's default export names.
2. Run:

   ```bash
   python scripts/main.py
   ```

Each archive produces one Markdown report in `reports/`, and the console prints only the total number of archives processed.

If no `COMMIT_HISTORY_*.md` file is found, reports are still generated but the date and branch lines stay empty.

## What it extracts

| Source                    | Extracted data                                                  |
| -------------------------- | ---------------------------------------------------------------- |
| GitLab commit list         | SHA, authored date, author and title of every commit, per branch |
| Archive content            | Every file name and folder name (names only, not full paths)     |
| `package.json`              | All `dependencies` and `devDependencies` names, deduplicated     |
| `docker-compose.yml` / `.yaml`, `compose.yml` / `.yaml` | All service names, with `container_name` when declared |
| `requirements.txt`          | All Python package names, deduplicated                           |

## Report contents

Each generated report is named `reports/<commit-sha>.md` when the archive matches a commit, otherwise `reports/<archive-name>.md`. It contains, in this order:

1. The archive name as title
2. The repository date (ISO 8601), taken from the matching commit
3. The branch(es) containing that commit, comma-separated (for example `main, development`)
4. File and folder counts, before and after deduplication
5. NPM dependencies (from every `package.json` found)
6. Docker services (from every compose file found)
7. Python dependencies (from every `requirements.txt` found)
8. The list of unique folder names, sorted
9. The list of unique file names, sorted (excluded files filtered out)

"Files found" counts every file in the archive. "Unique files" counts the files left after exclusions and deduplication, so it matches the list shown in the report.

## Customization

Edit `scripts/utils_exclusions.py` to hide more files from the reports. Hidden files are still counted in "Files found". The following are excluded by default:

- Fonts, images and videos, by extension
- Source maps and `.frm` files
- Names ending with `_fsm` or `_vm`
- Purely numeric names (`1214`, `1232`...)

## License

MIT. See [`LICENSE`](LICENSE).