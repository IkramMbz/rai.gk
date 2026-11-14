import json
import re
import zipfile

NPM_FILE = "package.json"
DOCKER_FILES = {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}
PYTHON_FILE = "requirements.txt"

SERVICE_RE = re.compile(r"^(\s+)([\w.\-]+):\s*$")
CONTAINER_RE = re.compile(r"container_name:\s*[\"']?([\w.\-]+)[\"']?")
REQ_RE = re.compile(r"^([A-Za-z0-9_.\-]+)")

def _docker_services(content):
    services = {}
    service_indent = None
    current = None
    in_services = False
    for line in content.splitlines():
        stripped = line.strip()
        if not in_services:
            if stripped == "services:":
                in_services = True
            continue
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip(" "))
        match = SERVICE_RE.match(line)
        if service_indent is None and match:
            service_indent = indent
        if match and indent == service_indent:
            current = match.group(2)
            services[current] = None
        elif indent < service_indent:
            in_services = False
            current = None
        elif current:
            cmatch = CONTAINER_RE.search(line)
            if cmatch:
                services[current] = cmatch.group(1)
    return services

def _npm_names(content):
    names = set()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return names
    for key in ("dependencies", "devDependencies"):
        value = data.get(key)
        if isinstance(value, dict):
            names.update(value.keys())
    return names

def _python_names(content):
    names = set()
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "-")):
            continue
        match = REQ_RE.match(line)
        if match:
            names.add(match.group(1))
    return names

def scan_tech(zip_path):
    npm, docker, python = set(), {}, set()
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            base = info.filename.split("/")[-1]
            content = None
            if base == NPM_FILE:
                content = zf.read(info).decode("utf-8", "ignore")
                npm.update(_npm_names(content))
            elif base in DOCKER_FILES:
                content = zf.read(info).decode("utf-8", "ignore")
                docker.update(_docker_services(content))
            elif base == PYTHON_FILE:
                content = zf.read(info).decode("utf-8", "ignore")
                python.update(_python_names(content))
    return sorted(npm), docker, sorted(python)
