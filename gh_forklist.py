#!/usr/bin/env -S uv run --script
# -*- coding: utf-8 -*-
#
# /// script
# requires-python = ">=3.12"
# dependencies = [
# "pandas",
# ]
# [tool.uv]
# exclude-newer = "2025-08-01T00:00:00Z"
#
# ///

import sys
import argparse
import subprocess
import json
import pandas as pd
from datetime import datetime


base_args = [
    "gh",
    "api",
    "--method",
    "GET",
    "-H",
    "Accept: application/vnd.github+json",
    "-H",
    "X-GitHub-Api-Version: 2026-03-10",
]


def gh_cli_api(endpoint_args, exit_on_api_error: bool = False):

    result = None

    try:
        result = subprocess.run(
            base_args + endpoint_args,
            encoding="utf-8",
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error output: {e.stderr}")
        if exit_on_api_error:
            sys.exit(1)
    except FileNotFoundError:
        print("The command executable was not found")
        sys.exit(1)

    return result


def generate_forklist(repo: str, branch: str, include_identical: bool):

    repo_ls = repo.split("/")

    repo_endpoint = f"repos/{repo_ls[0]}/{repo_ls[1]}"
    forks_endpoint = repo_endpoint + "/forks"

    if branch is None:
        default_branch_result = gh_cli_api([repo_endpoint], exit_on_api_error=True)
        branch = json.loads(default_branch_result.stdout)["default_branch"]

    forks_result = gh_cli_api(
        ["--paginate", "-f", "sort=stargazers", forks_endpoint], exit_on_api_error=True
    )

    fork_fields_1 = [
        "full_name",
        "default_branch",
        "stargazers_count",
        "forks_count",
        "open_issues_count",
        "size",
        "created_at",
        "updated_at",
        "pushed_at",
    ]

    df = pd.json_normalize(json.loads(forks_result.stdout), max_level=0)[fork_fields_1]

    df[["created_at", "updated_at", "pushed_at"]] = df[
        ["created_at", "updated_at", "pushed_at"]
    ].apply(pd.to_datetime)

    def get_fork_details(fork_repo: str, upstream_owner: str, branch: str):

        comp_endpoint = f"/repos/{fork_repo}/compare/master...{upstream_owner}:{branch}"

        details_result = gh_cli_api(["-f", "per_page=1", comp_endpoint])

        try:
            response = json.loads(details_result.stdout)
            out = {
                "status": response["status"],
                "ahead_by": response["ahead_by"],
                "behind_by": response["behind_by"],
            }
        except Exception as e:
            out = {"status": pd.NA, "ahead_by": pd.NA, "behind_by": pd.NA}
            print("Error", e)

        print(fork_repo, ":", repr(out))

        return pd.Series(out)

    df_status = df["full_name"].apply(
        func=get_fork_details, upstream_owner=repo_ls[0], branch=branch
    )

    df = df.join(df_status)

    filename = (
        "forks_" + repo_ls[1] + "_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".csv"
    )

    if include_identical:
        df.to_csv(filename, index=False)
    else:
        df[df.status != "identical"].to_csv(filename, index=False)


def build_parser() -> argparse.ArgumentParser:

    PROG_NAME = "gh_forklist"

    p = argparse.ArgumentParser(
        prog=PROG_NAME,
        description="Simple Github CLI wrapper to list the forks of a target Github repository with commit divergence details saved to a .csv file. Requires Github CLI executable `gh` in path with authentication set up.",
    )

    p.add_argument("repo", metavar="REPO", help="The target Github repository in owner/repo format")

    p.add_argument(
        "-b",
        metavar="BRANCH",
        help="The relevant branch of the target repository. If unspecified, uses the default one.",
    )

    p.add_argument(
        "--include-identical",
        action="store_true",
        help="Include identical/unchanged forks in the list, which are by default discarded.",
    )

    return p


def main(argv=None) -> int:

    parser = build_parser()
    args = parser.parse_args(argv)

    generate_forklist(args.repo, args.b, args.include_identical)

    return 0


if __name__ == "__main__":
    sys.exit(main())
