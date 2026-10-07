#!/usr/bin/env python3
"""
sync_shipped.py - fills the "Recently shipped" table in README.md from real GitHub data.

Stdlib only. For every public, non-fork repo tagged with the topic `shipped`,
it shows the latest GitHub Release (tag + date). If a repo has no release yet,
it says so honestly and falls back to the last push date.
Nothing is invented and nothing is a live counter, so the file only changes
when you actually ship something.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

USER = os.environ["PROFILE_USER"]
TOKEN = os.environ.get("GITHUB_TOKEN", "")
README = os.environ.get("README_PATH", "README.md")
API = "https://api.github.com"


def gh(path, params=None):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": f"{USER}-profile-sync"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def day(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%d %b %Y")


def build_table():
    repos = gh(f"/users/{USER}/repos", {"per_page": 100, "sort": "pushed", "type": "owner"}) or []
    shipped = [
        r for r in repos
        if "shipped" in (r.get("topics") or []) and not r["fork"] and not r["private"]
        and r["name"].lower() != USER.lower()
    ]
    if not shipped:
        return "_Tag a repo with the topic `shipped` and it appears here._"
    rows = ["| Project | Latest release | Updated |", "|---|---|---|"]
    for r in shipped:
        rel = gh(f"/repos/{USER}/{r['name']}/releases/latest")
        if rel:
            tag = f"[{rel['tag_name']}]({rel['html_url']})"
            when = day(rel.get("published_at") or r["pushed_at"])
        else:
            tag, when = "no release yet", day(r["pushed_at"])
        rows.append(f"| [{r['name']}]({r['html_url']}) | {tag} | {when} |")
    return "\n".join(rows)


def main():
    with open(README, encoding="utf-8") as f:
        text = f.read()
    pat = re.compile(r"(<!--START_SECTION:shipped-->)(.*?)(<!--END_SECTION:shipped-->)", re.DOTALL)
    if not pat.search(text):
        sys.exit("marker 'shipped' not found in README")
    new = pat.sub(lambda m: f"{m.group(1)}\n{build_table()}\n{m.group(3)}", text)
    if new != text:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new)
        print("README updated.")
    else:
        print("No changes.")


if __name__ == "__main__":
    main()
