#!/usr/bin/env python3
"""
log_streak.py

Run this after finishing your daily learning session.
It logs the entry, commits it, and pushes to GitHub,
so your real contribution graph reflects real study days.

Usage:
    python3 log_streak.py
    python3 log_streak.py "Finished loops + started functions"
    python3 log_streak.py --hours 3 "Practiced list comprehensions"
"""

import argparse
import datetime
import subprocess
import sys
from pathlib import Path

LOG_FILE = Path(__file__).parent / "streak.log"


def run(cmd, cwd=None):
    """Run a shell command, return (success, output)."""
    result = subprocess.run(
        cmd, cwd=cwd, shell=True,
        capture_output=True, text=True
    )
    ok = result.returncode == 0
    output = (result.stdout + result.stderr).strip()
    return ok, output


def ensure_git_repo():
    ok, _ = run("git rev-parse --is-inside-work-tree")
    if not ok:
        print("This folder isn't a git repo yet.")
        print("Run these once, then re-run this script:\n")
        print("  git init")
        print("  git remote add origin <your-github-repo-url>")
        print("  git branch -M main")
        print("  git push -u origin main\n")
        sys.exit(1)


def append_log(message, hours):
    today = datetime.date.today().isoformat()
    hours_str = f" ({hours}h)" if hours else ""
    line = f"{today}{hours_str} - {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    return line.strip()


def commit_and_push(message, hours):
    today = datetime.date.today().isoformat()
    hours_str = f" ({hours}h)" if hours else ""
    commit_msg = f"Day log {today}{hours_str}: {message}"

    ok, out = run("git add streak.log")
    if not ok:
        print("git add failed:", out)
        sys.exit(1)

    ok, out = run(f'git commit -m "{commit_msg}"')
    if not ok:
        if "nothing to commit" in out:
            print("Nothing new to commit - did you already log today?")
        else:
            print("git commit failed:", out)
        sys.exit(1)

    ok, out = run("git push")
    if not ok:
        print("git push failed:", out)
        print("Your commit is saved locally - push manually with: git push")
        sys.exit(1)

    print("Pushed to GitHub - success")


def main():
    parser = argparse.ArgumentParser(description="Log a completed study session.")
    parser.add_argument(
        "message", nargs="?", default=None,
        help="What you studied/completed (optional - will prompt if omitted)"
    )
    parser.add_argument(
        "--hours", type=float, default=None,
        help="Hours spent (optional)"
    )
    args = parser.parse_args()

    ensure_git_repo()

    message = args.message
    if message is None:
        message = input("What did you learn today? ").strip()
        if not message:
            message = "completed"

    line = append_log(message, args.hours)
    print(f"Logged: {line}")
    commit_and_push(message, args.hours)


if __name__ == "__main__":
    main()
