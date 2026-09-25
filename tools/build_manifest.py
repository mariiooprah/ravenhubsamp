#!/usr/bin/env python3
import hashlib
import json
import pathlib
import subprocess
import urllib.parse


ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW_BASE_URL = "https://raw.githubusercontent.com/mariiooprah/ravenhubsamp/"
LFS_BASE_URL = "https://media.githubusercontent.com/media/mariiooprah/ravenhubsamp/"
EXCLUDED_FILES = {
    ".gitattributes",
    ".gitignore",
    "GTASAsf10.b",
    "README.md",
    "gtasatelem.set",
    "manifest.json",
}
EXCLUDED_PREFIXES = (
    ".github/",
    "SAMP/screenshots/",
    "logcat/",
    "tools/",
)


def tracked_files():
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        path = raw_path.decode("utf-8")
        if path in EXCLUDED_FILES or path.startswith(EXCLUDED_PREFIXES):
            continue
        yield path


def lfs_tracked_files():
    result = subprocess.run(
        ["git", "lfs", "ls-files", "--name-only"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def lfs_pointer_metadata(path):
    if path.stat().st_size > 1024:
        return None
    content = path.read_text(encoding="ascii", errors="ignore")
    if not content.startswith("version https://git-lfs.github.com/spec/v1\n"):
        return None

    oid = None
    size = None
    for line in content.splitlines():
        if line.startswith("oid sha256:"):
            oid = line.removeprefix("oid sha256:")
        elif line.startswith("size "):
            size = int(line.removeprefix("size "))
    if oid and size is not None:
        return oid, size
    raise ValueError(f"Invalid Git LFS pointer: {path}")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_entry(relative_path, lfs_paths, version):
    path = ROOT / relative_path
    lfs_pointer = lfs_pointer_metadata(path)
    if lfs_pointer:
        digest, size = lfs_pointer
    else:
        digest, size = sha256(path), path.stat().st_size

    if relative_path in lfs_paths:
        download_url = LFS_BASE_URL + version + "/" + urllib.parse.quote(relative_path)
    else:
        download_url = None
    entry = {
        "path": relative_path,
        "size": size,
        "sha256": digest,
    }
    if download_url:
        entry["url"] = download_url
    return entry


def main():
    version = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    lfs_paths = lfs_tracked_files()
    files = [
        file_entry(path, lfs_paths, version)
        for path in sorted(tracked_files(), key=str.casefold)
    ]
    manifest = {
        "version": version,
        "baseUrl": RAW_BASE_URL + version + "/",
        "files": files,
    }
    output = ROOT / "manifest.json"
    output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Generated {output.name} with {len(files)} files")


if __name__ == "__main__":
    main()
