import hashlib
import os
import json
from datetime import datetime


BASELINE_FILE = "baseline.json"
LOG_FILE = "integrity.log"
EXCLUSIONS_FILE = "exclusions.json"


def load_exclusions():

    if not os.path.exists(EXCLUSIONS_FILE):

        return {
            "files": [],
            "folders": []
        }

    try:

        with open(
            EXCLUSIONS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            exclusions = json.load(file)

    except (
        OSError,
        json.JSONDecodeError
    ):

        return {
            "files": [],
            "folders": []
        }

    if "files" not in exclusions:
        exclusions["files"] = []

    if "folders" not in exclusions:
        exclusions["folders"] = []

    return exclusions


def calculate_hash(filepath):

    sha256 = hashlib.sha256()

    with open(filepath, "rb") as file:

        while True:

            chunk = file.read(4096)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def scan_folder(folder):

    file_hashes = {}

    exclusions = load_exclusions()

    excluded_files = set(
        exclusions.get("files", [])
    )

    excluded_folders = set(
        exclusions.get("folders", [])
    )

    for root, directories, files in os.walk(folder):

        # Remove excluded folders
        directories[:] = [
            directory
            for directory in directories
            if directory not in excluded_folders
        ]

        for filename in files:

            # Skip excluded files
            if filename in excluded_files:
                continue

            filepath = os.path.abspath(
                os.path.join(
                    root,
                    filename
                )
            )

            try:

                file_hash = calculate_hash(
                    filepath
                )

                file_hashes[
                    filepath
                ] = file_hash

            except PermissionError:

                print(
                    f"Permission denied: {filepath}"
                )

            except OSError:

                print(
                    f"Unable to read: {filepath}"
                )

    return file_hashes


def create_baseline(folder):

    print("\nScanning folder...\n")

    file_hashes = scan_folder(folder)

    with open(
        BASELINE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            file_hashes,
            file,
            indent=4
        )

    print(
        "Baseline created successfully!"
    )

    print(
        f"{len(file_hashes)} files recorded.\n"
    )


def write_log(event, filepath):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    try:

        with open(
            LOG_FILE,
            "a",
            encoding="utf-8"
        ) as log:

            log.write(
                f"{timestamp} - "
                f"{event} - "
                f"{filepath}\n"
            )

    except OSError:

        print(
            "Unable to write to security log."
        )


def check_integrity(folder):

    if not os.path.exists(
        BASELINE_FILE
    ):

        return None

    try:

        with open(
            BASELINE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            baseline = json.load(file)

    except (
        OSError,
        json.JSONDecodeError
    ):

        return None

    current_files = scan_folder(
        folder
    )

    modified = []
    added = []
    deleted = []
    unchanged = []

    for filepath in current_files:

        if filepath not in baseline:

            added.append(filepath)

        elif (
            current_files[filepath]
            != baseline[filepath]
        ):

            modified.append(filepath)

        else:

            unchanged.append(filepath)

    for filepath in baseline:

        if filepath not in current_files:

            deleted.append(filepath)

    for filepath in modified:

        write_log(
            "MODIFIED",
            filepath
        )

    for filepath in added:

        write_log(
            "ADDED",
            filepath
        )

    for filepath in deleted:

        write_log(
            "DELETED",
            filepath
        )

    total_changes = (
        len(modified)
        + len(added)
        + len(deleted)
    )

    return {
        "modified": modified,
        "added": added,
        "deleted": deleted,
        "unchanged": unchanged,
        "total_changes": total_changes
    }


def view_logs():

    if not os.path.exists(
        LOG_FILE
    ):

        print(
            "\nNo logs found.\n"
        )

        return

    print(
        "\n========== SECURITY LOG ==========\n"
    )

    with open(
        LOG_FILE,
        "r",
        encoding="utf-8"
    ) as log:

        contents = log.read()

    print(contents)

    print(
        "==================================\n"
    )

