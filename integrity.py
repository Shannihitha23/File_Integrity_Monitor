
import hashlib
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MONITORED_DIR = BASE_DIR / "monitored_files"
BASELINE_FILE = BASE_DIR / "baseline.json"


def calculate_hash(file_path):
    """Calculate the SHA-256 fingerprint of a file."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def scan_files():
    """Hash regular files inside the monitored folder."""
    MONITORED_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    for path in MONITORED_DIR.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue

        relative_path = path.relative_to(MONITORED_DIR).as_posix()
        results[relative_path] = calculate_hash(path)

    return results


def create_baseline():
    """Save the current file fingerprints."""
    current_files = scan_files()

    BASELINE_FILE.write_text(
        json.dumps(current_files, indent=4),
        encoding="utf-8"
    )

    return len(current_files)


def check_integrity():
    """Compare current files with the saved baseline."""
    if not BASELINE_FILE.exists():
        return None

    baseline = json.loads(
        BASELINE_FILE.read_text(encoding="utf-8")
    )
    current = scan_files()
    report = []

    for name in sorted(set(baseline) | set(current)):
        if name not in current:
            status = "MISSING"
        elif name not in baseline:
            status = "NEW"
        elif baseline[name] != current[name]:
            status = "MODIFIED"
        else:
            status = "UNCHANGED"

        report.append({
            "filename": name,
            "status": status
        })

    return report
