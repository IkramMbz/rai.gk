<div align="center">
  <a href="https://github.com/IkramMbz/nakas.gk">
    <img
      src="assets/media/img/rai-gk-banner.png"
      alt="rai.gk Logo"
    >
  </a>

  <h1>rai.gk by Glitch Kids</h1>

  <p>
    <strong>Repository Activity Inspector.</strong>
    <br>
    Recover the full commit history of a GitLab repository in minutes, scan its ZIP archives without extracting them, and generate JSONL reports: a complete private one, a sanitized one safe to embed in a front-end, and an editable technology catalog.
  </p>

  <p>
    <img src="https://img.shields.io/badge/release-v0.4.2-white" alt="Release v0.4.2">
    <a href="https://glitchkids.space/"><img src="https://img.shields.io/badge/Glitch%20Kids-Suite-black" alt="Glitch Kids Suite"></a>
    <a href="https://github.com/IkramMbz/rai.gk/blob/main/LICENSE.md"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License"></a>
    <a href="https://nodejs.org/"><img src="https://img.shields.io/badge/Node.js-%E2%89%A5%2022.13-339933?logo=node.js&logoColor=white" alt="Node.js >= 22.13"></a>
    <a href="https://www.typescriptlang.org/"><img src="https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white" alt="TypeScript"></a>
  </p>

  <p>
    <strong>Tested with</strong><br><br>
    <a href="https://react.dev/"><img src="https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black" alt="React"></a>
    <a href="https://nextjs.org/"><img src="https://img.shields.io/badge/Next.js-000000?logo=nextdotjs&logoColor=white" alt="Next.js"></a>
    <a href="https://vite.dev/"><img src="https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white" alt="Vite"></a>
    <a href="https://astro.build/"><img src="https://img.shields.io/badge/Astro-BC52EE?logo=astro&logoColor=white" alt="Astro"></a>
  </p>

  <p>
    <a href="#installation">Installation</a>&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="#usage">Usage</a>&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="#the-tech-catalog">Tech catalog</a>&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="#data-formats">Data formats</a>&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="CHANGELOG.md">Changelog</a>&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="LICENSE">License</a>
  </p>

  <br>
</div>

**rai.gk** is the first building block of a pipeline designed to give developers credit for work done in private repositories. Client projects, NDAs, GitLab-only projects, deleted repositories. Work that never appears on their public GitHub contribution graph, despite being real, dated and shippable.

The end goal is a "making of" front-end that displays how your app evolved: stack, services and milestones over time. The reference implementation is here: [`https://mo.mbechezi.fr/`](https://mo.mbechezi.fr/).

It works in three steps:

1. **Commit history (GitLab).** A browser script walks through every page of a branch's commit list and exports the complete history (SHA, date, author, title, branch) to a JSONL file.
2. **Archive scan (optional).** A Python script merges every exported history into `all_commits.jsonl`, audits ZIP exports of the repository without extracting them, matches each archive to its commit, and writes `reports-full.jsonl` (private), `reports-public.jsonl` (sanitized) and `tech-catalog.jsonl` (editable).
3. **Front-end.** Copy `reports-public.jsonl` and your annotated `tech-catalog.jsonl` into the front-end's `src/data/` folder.

Run step 1 first: without the commit history, records have no date, author or branch.

## Security: what goes to the front-end

> **Never put `reports-full.jsonl` or `all_commits.jsonl` in the front-end.** Anything imported by a front-end ends up in the bundle and can be downloaded by anyone, even if the UI never displays it.

Only `reports-public.jsonl` and `tech-catalog.jsonl` are meant to be shipped. The public report is built with a whitelist: only the fields below are copied, so a field added to the full report later does not leak by default.

| Field in full report | In public report | Why |
| --- | --- | --- |
| `id`, `name` | No (replaced by `index`) | SHA and ZIP name reveal the namespace and project, and link the portfolio to the private repo |
| `author`, `title` | No | Real names, client names, tickets, secrets pasted in commit messages |
| `branches` | No | Internal branch names |
| `files`, `dirs` | No | Internal tree, client names, sensitive file names (`.env`, `*.pem`...) |
| `docker` values | No (service names only) | `container_name` describes your infrastructure |
| `npm` | Yes, minus `PRIVATE_SCOPES` | Your stack. Set private scopes in `scripts/utils_records.py` |
| `python`, `counts` | Yes | Stack and numbers |
| `date` | Yes, reduced to `YYYY-MM-DD` | Time and timezone dropped |

`tech-catalog.jsonl` is also public once it is in the front-end, **including everything you write in `reason`**. Do not put client names, internal project names or anything under NDA in it.

Before publishing, review both files: even a library name can be confidential for a client under NDA. Add `archives/`, `all_commits.jsonl` and `reports-full.jsonl` to your `.gitignore`.

Readable milestone titles and explanations are not taken from commit messages: write them yourself, keyed by `index` in the front-end's annotations, or as a `reason` in the tech catalog.

## Installation

Just skip this part ! No third-party dependency is required; the project only relies on the Python standard library. The browser script runs directly in the console. No virtual environment is needed either.

## Project structure

```
.
├── scripts/              # main.py, utils_*.py, gitlab-commits-to-json.js
├── archives/             # your ZIPs and COMMIT_HISTORY_*.jsonl files
├── all_commits.jsonl     # every commit, deduplicated by SHA, oldest first (private)
├── reports-full.jsonl    # one complete record per archive (private)
├── reports-public.jsonl  # sanitized records, safe for the front-end
├── tech-catalog.jsonl    # every detected technology + your annotations (for the front-end)
└── CHANGELOG.md          # release history
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

### Step 2: Build the commit list, the reports and the tech catalog

1. Optionally, download the repository ZIPs from GitLab (one per commit or branch state you want to analyze) and place them in `archives/`, next to the `COMMIT_HISTORY_*.jsonl` files. The ZIP file name must contain the commit SHA, which is the case for GitLab's default export names.
2. If some of your npm packages are private (`@client/...`), list their scopes in `PRIVATE_SCOPES` at the top of `scripts/utils_records.py`.
3. Run:

   ```bash
   python scripts/main.py
   ```

This produces:
- `all_commits.jsonl`: all commits from every `COMMIT_HISTORY_*.jsonl`, deduplicated by SHA, sorted oldest to newest, with the `branches` of each commit merged. Generated even without any ZIP.
- `reports-full.jsonl`: one complete record per ZIP archive, sorted by date (undated last). **Private.**
- `reports-public.jsonl`: the same records reduced to the whitelist above.
- `tech-catalog.jsonl`: every technology found in the data, with its source and editable annotations. See below.

Without any `COMMIT_HISTORY_*.jsonl`, `all_commits.jsonl` is not created and records are still generated, but `date`, `author`, `title` and `branches` stay empty.

### Step 3: Feed the front-end

Copy `reports-public.jsonl` and `tech-catalog.jsonl` into the front-end's `src/data/` folder ([`<FRONT_APP_REPO_URL>`](<FRONT_APP_REPO_URL>)), replacing the default example data. Do not copy any other file.

The front-end is read-only: it never edits or deletes anything. All annotations are made in `tech-catalog.jsonl`, by hand.

## The tech catalog

### Why it exists

`reports-public.jsonl` only knows raw package names (`react`, `flask`, `db`). It cannot know **why** you chose a technology, how important it is, or how it should be grouped. The catalog is the place where you add that, once, and it is kept across every regeneration.

The front-end uses it to:
- display a technology's name, category tag and reason when you click its logo in the cloud;
- group and sort the "all technologies" list (by category, by importance);
- decide what is shown at all: **a technology that is not in the catalog is not displayed**.

### How it is generated

`main.py` builds it right after the reports, from **every** technology found in the data (`npm`, `python`, `docker`, across all snapshots). One line per technology:

```json
{"name":"react","slug":"react","source":"npm","category":"Frontend","reason":"","importance":0}
```

| Field | Filled by | Description |
| --- | --- | --- |
| `name` | generated | Raw name as found in the data |
| `slug` | generated | Normalized name (lowercase, `-` separators) |
| `source` | generated | Where it was found: `npm`, `python` or `docker` |
| `category` | **you** | Free text (Frontend, Backend, Database, DevOps...). Default `Frontend` |
| `reason` | **you** | Why this technology is used. Empty by default, nothing is ever generated |
| `importance` | **you** | A number you define, used by the relevance sort. Default `0` |

The sync is **append-only**:
- New technologies are added at the end, after three empty lines, so you can spot them.
- Existing lines are never rewritten, so your annotations survive every run.
- The key is `source` + `slug`: `redis` found in npm and in docker gives two lines.
- If you delete a line, the technology disappears from the front-end. If it is still detected, it is **re-added at the end at the next run**.
- Running it twice in a row changes nothing.

### What you have to do

1. Run `python scripts/main.py`.
2. Open `tech-catalog.jsonl` and **clean it**: it contains everything, including noise (`@types/*`, eslint plugins, build tooling). Delete the lines you do not want to show.
3. For the lines you keep, set `category` (the default `Frontend` is wrong for most backend, database and docker entries), `reason` and `importance`.
4. Copy the file into the front-end's `src/data/`.
5. After each new run, look at the lines appended after the three empty lines and do the same.

### What you could forget

- **Keep a single source of truth.** `main.py` reads and appends to the `tech-catalog.jsonl` at the root of rai.gk. If you edit the copy in the front-end and then run `main.py`, the sync starts from the old root file and a later copy back to the front-end **overwrites your annotations**. Either edit the root file and copy it over, or copy the front-end's file back to the root before every run.
- **Back it up.** It holds manual work that cannot be regenerated. Do not delete it to "reset" it, and version it (it is not in the `.gitignore` list above).
- **Keep it valid JSONL.** One JSON object per line, double quotes, no trailing comma, quotes escaped inside `reason`. The blank lines are fine. A broken line is skipped with a warning and the technology is then considered missing, so it gets appended again as a duplicate.
- **`reason` is public** once the file is in the front-end bundle. No client names or confidential details.
- **Deleting is not permanent.** To hide a technology for good, there is no flag: it comes back at the next run if the data still contains it. Delete it again, or remove the package from the data.
- **`slug` is not guaranteed to be a [Simple Icons](https://simpleicons.org) slug.** The front-end matches logos on its side. A technology without a matching icon is simply not displayed in the cloud.
- **Docker entries are service names** (`db`, `web`), not products. Their usefulness depends on how you named your services. Rename or remove them by hand.
- **Private scopes are excluded** (`PRIVATE_SCOPES`), since this file goes to the front-end. If you add a scope later, delete the already generated lines yourself, the sync never removes anything.
- **Never rely on the sort for file order.** The front-end sorts a copy. The order of the file stays chronological by first detection.

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

### Commit history (private)

`archives/COMMIT_HISTORY_<branch>.jsonl`, one line per commit:

```json
{"sha":"a1b2c3d4...","iso":"2025-03-12T14:02:11+01:00","author":"...","title":"...","branch":"main"}
```

### All commits (private)

`all_commits.jsonl`, one line per unique SHA. Same fields, but `branch` becomes a `branches` list:

```json
{"iso":"2025-03-12T14:02:11+01:00","title":"...","author":"...","sha":"a1b2c3d4...","branches":["main","development"]}
```

### Full record (private)

`reports-full.jsonl`, one line per archive. `id` is the commit SHA when the archive matches a commit, otherwise the archive name. Shown indented here for readability:

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

### Public record (front-end)

`reports-public.jsonl`, one line per archive, in chronological order. `index` replaces `id`, and `docker` is a list of service names only:

```json
{"index":0,"date":"2025-03-12","counts":{"files":1200,"unique_files":340,"dirs":210,"unique_dirs":95},"npm":["react","next"],"python":["flask"],"docker":["db"]}
```

### Tech catalog (front-end)

`tech-catalog.jsonl`, one line per technology and source. See [The tech catalog](#the-tech-catalog).

## Customization

- `scripts/utils_exclusions.py`: hide more files from records. Hidden files are still counted in `counts.files`. Excluded by default: fonts, images and videos (by extension), source maps and `.frm` files, names ending with `_fsm` or `_vm`, purely numeric names.
- `PRIVATE_SCOPES` in `scripts/utils_records.py`: npm scopes removed from the public report and from the tech catalog.
- `DEFAULTS` in `scripts/utils_catalog.py`: default `category`, `reason` and `importance` of new catalog entries.
- To expose another field in the public report, add it explicitly in `build_public_record` (`scripts/utils_records.py`) (whitelist).

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for the full release history. Latest release: **v0.5.0**.

## License

MIT. See [`LICENSE`](LICENSE).
