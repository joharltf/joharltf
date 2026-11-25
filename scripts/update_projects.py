#!/usr/bin/env python3
"""Sync the README projects table with the account's public repositories."""

import html
import json
import os
import re
import sys
import urllib.request

USER = os.environ.get("GITHUB_USER", "joharltf")
TOKEN = os.environ["GITHUB_TOKEN"]
README = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"


def fetch_repos():
    url = (
        f"https://api.github.com/users/{USER}/repos"
        "?per_page=100&type=owner&sort=updated"
    )
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": "profile-projects-sync",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def cell(text):
    clean = (text or "no description").replace("\r", " ").replace("\n", " ").strip()
    return html.escape(clean)


def main():
    repos = [
        repo
        for repo in fetch_repos()
        if repo["name"] != USER and not repo.get("archived", False)
    ]

    blocks = []
    for repo in repos:
        blocks.append(
            f'<p align="center">\n'
            f'  <a href="{repo["html_url"]}"><b>{cell(repo["name"])}</b></a><br />\n'
            f"  <sub>{cell(repo.get('description'))}</sub>\n"
            f"</p>"
        )
    table = "\n\n".join(blocks)

    with open(README, encoding="utf-8") as handle:
        current = handle.read()

    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(current):
        print(f"markers {START} / {END} not found in {README}", file=sys.stderr)
        return 1

    updated = pattern.sub(f"{START}\n{table}\n{END}", current)
    if updated == current:
        print("projects table already up to date")
        return 0

    with open(README, "w", encoding="utf-8") as handle:
        handle.write(updated)
    print(f"projects table updated with {len(repos)} repo(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
