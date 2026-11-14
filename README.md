<div align="center">
  <h1>rai.gk</h1>

  <p>
    <strong>Repository Archive Inspector.</strong>
    <br>
    Scan GitHub & GitLab's ZIP archives without extracting them, and generate per-archive Markdown reports ready to feed into an AI model.
  </p>

  <p>
    <img src="https://img.shields.io/badge/release-v0.1.0-white" alt="Release v0.1.0">
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

Downloading a ZIP export is the fastest way to capture a snapshot of a private codebase at a specific point in time.

This first tool reads that snapshot. It audits ZIP archives without extracting them to disk, reading only their central directory metadata. No decompression, keeping it fast even across large numbers of archives.

For each archive, it generates a standalone Markdown report to feed into an AI model for technology and content analysis: frameworks, running services, declared dependencies, file structure, etc.

This provides the raw material for a later step: turning private development history into a dated, legitimate record of the work actually done.

## What it extracts

| Source                    | Extracted data                                                  |
| -------------------------- | ---------------------------------------------------------------- |
| Archive content            | Every file name and every folder name, duplicates kept as-is     |
| `package.json`              | All `dependencies` and `devDependencies` names, deduplicated     |
| `docker-compose.yml` / `.yaml`, `compose.yml` / `.yaml` | All service names, with `container_name` when declared |
| `requirements.txt`          | All Python package names, deduplicated                           |

File names matching extensions in `utils_exclusions.py` (fonts, images, videos) are hidden from the report's file list, but still counted in the totals.

## Installation

Just skip this part ! No third-party dependency is required; the project only relies on the Python standard library. No virtual environment is needed either.

## Usage

Place your ZIP archives in an `archives/` folder at the project root, then run:

```bash
python main.py
```

Each archive produces one Markdown report in `reports/`, and the console prints only the total number of archives processed.

## Report contents

Each generated `reports/<archive-name>.md` file contains, in this order:

1. The archive name as title
2. A manually editable date line where the original repository's commit date (associated with the downloaded ZIP) must be entered, formatted as DD-MM-YYYY.
3. File and folder counts, before and after deduplication
4. NPM dependencies (from every `package.json` found)
5. Docker services (from every compose file found)
6. Python dependencies (from every `requirements.txt` found)
7. The full list of folder names
8. The full list of file names (excluded extensions filtered out)

## Customization

Extend `utils_exclusions.py` to hide additional file extensions from reports without affecting the file counts.

## License

MIT. See [`LICENSE`](LICENSE).