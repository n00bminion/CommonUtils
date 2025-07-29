import os
import shutil
from pathlib import Path
import importlib.resources as pkg_resources

GITHUB_WORKFLOW_DIR = Path(".github", "workflows")
YAML_DIR = Path(pkg_resources.files(__name__), "yaml")


def add_github_action_folder():
    if not os.path.exists(GITHUB_WORKFLOW_DIR):
        os.makedirs(GITHUB_WORKFLOW_DIR)


def add_github_action_scheduler():
    """Add a GitHub Action Scheduler file to the repository if it does not exist."""

    add_github_action_folder()

    scheduler_file = "github-action-scheduler.yaml"

    if not os.path.isfile(GITHUB_WORKFLOW_DIR / scheduler_file):
        shutil.copy(
            src=YAML_DIR / scheduler_file,
            dst=GITHUB_WORKFLOW_DIR / scheduler_file,
        )


if __name__ == "__main__":
    add_github_action_scheduler()
