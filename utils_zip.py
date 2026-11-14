import zipfile

def extract_names(zip_path):
    files = []
    dirs = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            name = info.filename
            if info.is_dir() or name.endswith("/"):
                dirs.append(name.rstrip("/").split("/")[-1])
            else:
                files.append(name.split("/")[-1])
    return files, dirs
