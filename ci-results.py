import os
import shutil
from pathlib import Path
from contextlib import contextmanager

from anybadge import Badge
from git import Repo


CI = os.environ.get("CI", False)

GIT_USER = "stefanhoelzl"
GIT_REPO_NAME = "fancy-dict"
GIT_AUTHENTICATION = ""
if CI:
    GIT_AUTHENTICATION = "{}:x-oauth-basic@".format(
        os.environ.get("GITHUB_TOKEN")
    )
GIT_REPO_URL = "https://{}github.com/{}/{}.git"\
    .format(GIT_AUTHENTICATION, GIT_USER, GIT_REPO_NAME)

RESULTS_BRANCH = "ci-results"
MASTER_BRANCH = "master"

RESULTS_FILE = "testresults.tap"
COV_REPORT = "covhtml"

DESTINATION = Path(RESULTS_BRANCH) / os.environ.get("TRAVIS_BRANCH", "debug")
CREATED_FILES = []


def get_test_counts():
    passed = 0
    failed = 0
    skipped = 0
    with open(RESULTS_FILE, "r") as result_file:
        for line in result_file.readlines():
            if "# SKIP" in line:
                skipped += 1
            elif line.startswith("ok"):
                passed += 1
            elif line.startswith("not ok"):
                failed += 1
    return {
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
    }


def create_test_results_badge():
    results = get_test_counts()
    value = ", ".join("{} {}".format(name, count)
                      for name, count in results.items() if count)
    color = "green"
    if results["failed"]:
        color = "red"
    elif results["skipped"]:
        color = "orange"
    badge = Badge('tests', value, default_color=color)
    badge_path = Path(DESTINATION) / "tests.svg"
    badge.write_badge(str(badge_path), overwrite=True)
    CREATED_FILES.append(str(badge_path.absolute()))


def copy_test_results():
    copied_file = Path(DESTINATION) / RESULTS_FILE
    Path(copied_file).write_text(Path(RESULTS_FILE).read_text())
    CREATED_FILES.append(str(copied_file.absolute()))


def copy_coverage_report():
    dest = Path(DESTINATION, COV_REPORT)
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(COV_REPORT, dest)
    CREATED_FILES.append(str(dest.absolute()))


@contextmanager
def push_created_files():
    shutil.rmtree(RESULTS_BRANCH, ignore_errors=True)
    repo = Repo.clone_from(GIT_REPO_URL, RESULTS_BRANCH, branch=RESULTS_BRANCH)
    DESTINATION.mkdir(exist_ok=True)
    yield
    repo.index.add(CREATED_FILES)
    repo.index.commit("Build {}".format(
        os.environ.get("TRAVIS_BUILD_NUMBER", "debug"))
    )
    if CI:
        repo.remote("origin").push()


if __name__ == "__main__":
    with push_created_files():
        create_test_results_badge()
        copy_test_results()
        copy_coverage_report()
