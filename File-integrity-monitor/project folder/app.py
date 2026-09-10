from flask import Flask, render_template, request, redirect, url_for, flash
from integrity_monitor import (
    create_baseline,
    check_integrity,
    load_exclusions
)
from datetime import datetime
import os
import json
import secrets


app = Flask(__name__)

# Generate a secret key for Flask sessions
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    secrets.token_hex(32)
)


latest_status = None
latest_results = None
latest_scan_time = None
latest_folder = None


def get_safe_folder(folder):
    """
    Validate and clean a folder path.
    """

    if not folder:
        return None

    folder = folder.strip()

    if not os.path.isdir(folder):
        return None

    return os.path.abspath(folder)


@app.route("/")
def home():

    exclusions = load_exclusions()

    return render_template(
        "index.html",
        status=latest_status,
        results=latest_results,
        scan_time=latest_scan_time,
        folder=latest_folder,
        exclusions=exclusions
    )


@app.route("/create-baseline", methods=["POST"])
def create_baseline_route():

    folder = request.form.get("folder", "")
    folder = get_safe_folder(folder)

    if not folder:

        flash(
            "Invalid folder. Please enter a valid folder path.",
            "error"
        )

        return redirect(url_for("home"))

    try:

        create_baseline(folder)

        flash(
            "Baseline created successfully!",
            "success"
        )

    except PermissionError:

        flash(
            "Permission denied while scanning the folder.",
            "error"
        )

    except OSError:

        flash(
            "An error occurred while accessing the folder.",
            "error"
        )

    return redirect(url_for("home"))


@app.route("/check-integrity", methods=["POST"])
def check_integrity_route():

    global latest_status
    global latest_results
    global latest_scan_time
    global latest_folder

    folder = request.form.get("folder", "")
    folder = get_safe_folder(folder)

    if not folder:

        flash(
            "Invalid folder. Please enter a valid folder path.",
            "error"
        )

        return redirect(url_for("home"))

    try:

        results = check_integrity(folder)

    except PermissionError:

        flash(
            "Permission denied while scanning the folder.",
            "error"
        )

        return redirect(url_for("home"))

    except (OSError, json.JSONDecodeError):

        flash(
            "Unable to complete the integrity check.",
            "error"
        )

        return redirect(url_for("home"))

    if results is None:

        flash(
            "No baseline found. Please create a baseline first.",
            "error"
        )

        return redirect(url_for("home"))

    if results["total_changes"] > 0:

        status = "changes"

    else:

        status = "secure"

    latest_status = status
    latest_results = results
    latest_scan_time = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )
    latest_folder = folder

    return render_template(
        "results.html",
        results=results,
        status=status,
        scan_time=latest_scan_time,
        folder=latest_folder
    )


@app.route("/status")
def status():

    exclusions = load_exclusions()

    return render_template(
        "index.html",
        status=latest_status,
        results=latest_results,
        scan_time=latest_scan_time,
        folder=latest_folder,
        exclusions=exclusions
    )


@app.route("/view-logs")
def view_logs_route():

    if not os.path.exists("integrity.log"):

        return render_template(
            "logs.html",
            logs=""
        )

    try:

        with open(
            "integrity.log",
            "r",
            encoding="utf-8"
        ) as log:

            logs = log.read()

    except OSError:

        flash(
            "Unable to read the security logs.",
            "error"
        )

        logs = ""

    return render_template(
        "logs.html",
        logs=logs
    )


@app.route("/clear-logs", methods=["POST"])
def clear_logs():

    try:

        with open(
            "integrity.log",
            "w",
            encoding="utf-8"
        ) as log:

            log.write("")

        flash(
            "Security logs cleared successfully!",
            "success"
        )

    except OSError:

        flash(
            "Unable to clear the security logs.",
            "error"
        )

    return redirect(url_for("view_logs_route"))


@app.route("/add-exclusion", methods=["POST"])
def add_exclusion():

    exclusion = request.form.get(
        "exclusion",
        ""
    ).strip()

    exclusion_type = request.form.get(
        "type",
        ""
    ).strip()

    # Reject empty values
    if not exclusion:

        flash(
            "Please enter a file or folder name.",
            "error"
        )

        return redirect(url_for("home"))

    # Limit extremely long input
    if len(exclusion) > 255:

        flash(
            "The exclusion name is too long.",
            "error"
        )

        return redirect(url_for("home"))

    # Only allow the two expected types
    if exclusion_type not in [
        "files",
        "folders"
    ]:

        flash(
            "Invalid exclusion type.",
            "error"
        )

        return redirect(url_for("home"))

    exclusions = load_exclusions()

    if "files" not in exclusions:
        exclusions["files"] = []

    if "folders" not in exclusions:
        exclusions["folders"] = []

    # Prevent duplicate exclusions
    if exclusion in exclusions[exclusion_type]:

        flash(
            f"{exclusion} is already excluded.",
            "error"
        )

        return redirect(url_for("home"))

    exclusions[exclusion_type].append(
        exclusion
    )

    try:

        with open(
            "exclusions.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                exclusions,
                file,
                indent=4
            )

    except OSError:

        flash(
            "Unable to save the exclusion.",
            "error"
        )

        return redirect(url_for("home"))

    flash(
        f"{exclusion} added to exclusions. "
        "Please recreate your baseline before the next integrity check.",
        "success"
    )

    return redirect(url_for("home"))


@app.route("/remove-exclusion", methods=["POST"])
def remove_exclusion():

    exclusion = request.form.get(
        "exclusion",
        ""
    ).strip()

    exclusion_type = request.form.get(
        "type",
        ""
    ).strip()

    if not exclusion:

        flash(
            "Invalid exclusion.",
            "error"
        )

        return redirect(url_for("home"))

    if exclusion_type not in [
        "files",
        "folders"
    ]:

        flash(
            "Invalid exclusion type.",
            "error"
        )

        return redirect(url_for("home"))

    if not os.path.exists(
        "exclusions.json"
    ):

        flash(
            "No exclusions found.",
            "error"
        )

        return redirect(url_for("home"))

    try:

        with open(
            "exclusions.json",
            "r",
            encoding="utf-8"
        ) as file:

            exclusions = json.load(file)

    except (
        OSError,
        json.JSONDecodeError
    ):

        flash(
            "Unable to read exclusions.",
            "error"
        )

        return redirect(url_for("home"))

    if exclusion in exclusions.get(
        exclusion_type,
        []
    ):

        exclusions[
            exclusion_type
        ].remove(exclusion)

        try:

            with open(
                "exclusions.json",
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    exclusions,
                    file,
                    indent=4
                )

        except OSError:

            flash(
                "Unable to save the updated exclusions.",
                "error"
            )

            return redirect(url_for("home"))

        flash(
            f"{exclusion} removed from exclusions. "
            "Please recreate your baseline before the next integrity check.",
            "success"
        )

    else:

        flash(
            f"{exclusion} was not found in exclusions.",
            "error"
        )

    return redirect(url_for("home"))


# Disable detailed error pages for users
@app.errorhandler(404)
def page_not_found(error):

    return """
    <h1>404 - Page Not Found</h1>
    <p>The requested page does not exist.</p>
    <a href="/">Return to Dashboard</a>
    """, 404


@app.errorhandler(500)
def internal_error(error):

    return """
    <h1>500 - Internal Server Error</h1>
    <p>An unexpected error occurred.</p>
    <a href="/">Return to Dashboard</a>
    """, 500


if __name__ == "__main__":

    # Debug mode is disabled for safer operation
    app.run(
        debug=False,
        host="127.0.0.1",
        port=5000
    )
