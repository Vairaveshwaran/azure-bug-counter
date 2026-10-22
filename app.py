from flask import Flask, render_template, request
from dotenv import load_dotenv
import requests
import os
import socket
from datetime import datetime

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

app = Flask(__name__)

AZURE_ORG = os.getenv("AZURE_ORG")
AZURE_PROJECT = os.getenv("AZURE_PROJECT")
AZURE_PAT = os.getenv("AZURE_PAT")


# ============================================================
# FORCE IPV4
# ============================================================

original_getaddrinfo = socket.getaddrinfo


def getaddrinfo_ipv4(*args, **kwargs):
    results = original_getaddrinfo(*args, **kwargs)

    return [
        result
        for result in results
        if result[0] == socket.AF_INET
    ]


socket.getaddrinfo = getaddrinfo_ipv4


# ============================================================
# AZURE DEVOPS PROJECT GROUPS
# ============================================================

PROJECT_GROUPS = {
    "Bug - Proj 1": 5,
    "Bug - Proj 2": 6,
    "Bug - Proj 3": 7,
    "Bug - Proj 4": 8
}


# ============================================================
# AZURE GET REQUEST
# ============================================================

def azure_get(url):

    response = requests.get(
        url,
        auth=("", AZURE_PAT),
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# GET CHILD WORK ITEMS
# ============================================================

def get_child_bug_ids(parent_id):

    url = (
        f"https://dev.azure.com/{AZURE_ORG}/"
        f"{AZURE_PROJECT}/_apis/wit/workitems/"
        f"{parent_id}"
        f"?$expand=relations&api-version=7.1"
    )

    data = azure_get(url)

    child_ids = []

    for relation in data.get("relations", []):

        if relation.get("rel") == "System.LinkTypes.Hierarchy-Forward":

            child_url = relation.get("url", "")

            child_id = child_url.rstrip("/").split("/")[-1]

            if child_id.isdigit():

                child_ids.append(int(child_id))

    return child_ids


# ============================================================
# GET WORK ITEM REVISION HISTORY
# ============================================================

def get_bug_revisions(bug_id):

    url = (
        f"https://dev.azure.com/{AZURE_ORG}/"
        f"{AZURE_PROJECT}/_apis/wit/workitems/"
        f"{bug_id}/revisions?api-version=7.1"
    )

    data = azure_get(url)

    return data.get("value", [])


# ============================================================
# COUNT UNIQUE BUGS
# ============================================================

def count_bugs(parent_id, start_date, end_date):

    # Get all child work items under the selected project
    child_bug_ids = get_child_bug_ids(parent_id)

    # Set is used so one bug is counted only once
    unique_bugs = set()

    # Convert selected dates to date objects
    start = datetime.strptime(
        start_date,
        "%Y-%m-%d"
    ).date()

    end = datetime.strptime(
        end_date,
        "%Y-%m-%d"
    ).date()

    # Check every child work item
    for bug_id in child_bug_ids:

        # Get complete revision history
        revisions = get_bug_revisions(bug_id)

        for revision in revisions:

            fields = revision.get("fields", {})

            state = fields.get("System.State")

            changed_date = fields.get(
                "System.ChangedDate"
            )

            # Ignore revisions without a changed date
            if not changed_date:
                continue

            # Convert Azure timestamp to date
            changed_date_only = datetime.fromisoformat(
                changed_date.replace("Z", "+00:00")
            ).date()

            # In this Azure project, the Active board state
            # is represented as "Doing".
            #
            # We also support "Active" and "Reopened"
            # as required by the assignment.

            active_states = [
                "Doing",
                "Active",
                "Reopened"
            ]

            # Check state and date range
            if (
                state in active_states
                and start <= changed_date_only <= end
            ):

                # Add bug ID to set.
                # Duplicate revisions won't create duplicates.
                unique_bugs.add(bug_id)

                # This bug has already matched,
                # so no need to check more revisions.
                break

    return len(unique_bugs)


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        project_groups=PROJECT_GROUPS.keys(),
        result=None,
        error=None
    )


# ============================================================
# BUG COUNT
# ============================================================

@app.route("/count", methods=["POST"])
def count():

    project_name = request.form.get("project")

    start_date = request.form.get(
        "start_date"
    )

    end_date = request.form.get(
        "end_date"
    )

    # --------------------------------------------------------
    # Validate required fields
    # --------------------------------------------------------

    if (
        not project_name
        or not start_date
        or not end_date
    ):

        return render_template(
            "index.html",
            project_groups=PROJECT_GROUPS.keys(),
            result=None,
            error="Please select project and dates."
        )

    # --------------------------------------------------------
    # Validate date range
    # --------------------------------------------------------

    if start_date > end_date:

        return render_template(
            "index.html",
            project_groups=PROJECT_GROUPS.keys(),
            result=None,
            error="Start date cannot be after end date."
        )

    try:

        # Get parent work item ID
        parent_id = PROJECT_GROUPS[project_name]

        # Calculate unique bug count
        bug_count = count_bugs(
            parent_id,
            start_date,
            end_date
        )

        # Show result
        return render_template(
            "index.html",
            project_groups=PROJECT_GROUPS.keys(),
            result=bug_count,
            selected_project=project_name,
            start_date=start_date,
            end_date=end_date,
            error=None
        )

    except Exception as e:

        return render_template(
            "index.html",
            project_groups=PROJECT_GROUPS.keys(),
            result=None,
            selected_project=project_name,
            start_date=start_date,
            end_date=end_date,
            error=f"Azure request failed: {e}"
        )


# ============================================================
# START FLASK APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(debug=True)