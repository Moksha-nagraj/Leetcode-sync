#!/usr/bin/env python3
"""
Syncs recently accepted LeetCode submissions into this repo.

Requires two env vars (set as GitHub Actions secrets):
  LEETCODE_SESSION - value of the LEETCODE_SESSION cookie
  LEETCODE_CSRF    - value of the csrftoken cookie

Keeps track of already-synced submission IDs in .synced_ids.json
so it doesn't recommit the same solution twice.
"""

import os
import json
import re
import sys
import requests

LEETCODE_SESSION = os.environ.get("LEETCODE_SESSION")
LEETCODE_CSRF = os.environ.get("LEETCODE_CSRF")

if not LEETCODE_SESSION or not LEETCODE_CSRF:
    print("Missing LEETCODE_SESSION or LEETCODE_CSRF env vars.")
    sys.exit(1)

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "x-csrftoken": LEETCODE_CSRF,
    "User-Agent": "Mozilla/5.0",
}
COOKIES = {
    "LEETCODE_SESSION": LEETCODE_SESSION,
    "csrftoken": LEETCODE_CSRF,
}

GRAPHQL_URL = "https://leetcode.com/graphql"
SYNCED_IDS_FILE = ".synced_ids.json"

# Map LeetCode's language field to a file extension
LANG_EXTENSIONS = {
    "python3": "py",
    "python": "py",
    "java": "java",
    "cpp": "cpp",
    "c": "c",
    "csharp": "cs",
    "javascript": "js",
    "typescript": "ts",
    "kotlin": "kt",
    "swift": "swift",
    "golang": "go",
    "ruby": "rb",
    "rust": "rs",
    "scala": "scala",
    "php": "php",
}


def load_synced_ids():
    if os.path.exists(SYNCED_IDS_FILE):
        with open(SYNCED_IDS_FILE) as f:
            return set(json.load(f))
    return set()


def save_synced_ids(ids):
    with open(SYNCED_IDS_FILE, "w") as f:
        json.dump(sorted(ids), f, indent=2)


def get_recent_accepted_submissions(limit=20):
    query = """
    query recentAcSubmissions($username: String!, $limit: Int!) {
      recentAcSubmissionList(username: $username, limit: $limit) {
        id
        title
        titleSlug
        timestamp
        lang
      }
    }
    """
    # First get the username from session
    username = get_username()
    resp = requests.post(
        GRAPHQL_URL,
        headers=HEADERS,
        cookies=COOKIES,
        json={"query": query, "variables": {"username": username, "limit": limit}},
    )
    resp.raise_for_status()
    data = resp.json()
    return data["data"]["recentAcSubmissionList"]


def get_username():
    query = """
    query globalData {
      userStatus {
        username
      }
    }
    """
    resp = requests.post(
        GRAPHQL_URL, headers=HEADERS, cookies=COOKIES, json={"query": query}
    )
    resp.raise_for_status()
    data = resp.json()
    username = data["data"]["userStatus"]["username"]
    if not username:
        raise RuntimeError(
            "Could not resolve username — check that LEETCODE_SESSION and "
            "LEETCODE_CSRF are valid and not expired."
        )
    return username


def get_submission_detail(submission_id):
    query = """
    query submissionDetails($submissionId: Int!) {
      submissionDetails(submissionId: $submissionId) {
        code
        lang {
          name
        }
        question {
          questionId
          title
          titleSlug
          difficulty
        }
      }
    }
    """
    resp = requests.post(
        GRAPHQL_URL,
        headers=HEADERS,
        cookies=COOKIES,
        json={"query": query, "variables": {"submissionId": int(submission_id)}},
    )
    resp.raise_for_status()
    data = resp.json()
    return data["data"]["submissionDetails"]


def slugify_folder(difficulty, question_id, title_slug):
    return os.path.join(difficulty, f"{question_id}-{title_slug}")


def main():
    synced_ids = load_synced_ids()
    submissions = get_recent_accepted_submissions()

    new_count = 0
    for sub in submissions:
        sub_id = str(sub["id"])
        if sub_id in synced_ids:
            continue

        detail = get_submission_detail(sub_id)
        if not detail:
            continue

        question = detail["question"]
        lang_name = detail["lang"]["name"]
        ext = LANG_EXTENSIONS.get(lang_name.lower(), "txt")

        folder = slugify_folder(
            question["difficulty"], question["questionId"], question["titleSlug"]
        )
        os.makedirs(folder, exist_ok=True)

        filepath = os.path.join(folder, f"solution.{ext}")
        with open(filepath, "w") as f:
            f.write(detail["code"])

        readme_path = os.path.join(folder, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w") as f:
                f.write(
                    f"# {question['questionId']}. {question['title']}\n\n"
                    f"Difficulty: {question['difficulty']}\n\n"
                    f"https://leetcode.com/problems/{question['titleSlug']}/\n"
                )

        synced_ids.add(sub_id)
        new_count += 1
        print(f"Synced: {question['title']} ({lang_name})")

    save_synced_ids(synced_ids)
    print(f"Done. {new_count} new submission(s) synced.")


if __name__ == "__main__":
    main()
