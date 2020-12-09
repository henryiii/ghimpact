#!/usr/bin/env python3

import json
import math
import sys
from typing import Any, List, Dict, Optional
from datetime import datetime
import yaml
import click
from github import Github


def get_items(user, start_date, auth: Optional[str] = None) -> List[Dict[str, Any]]:
    "Run with 0 to get and combine all pages."

    gh = Github(auth)
    gh.per_page = 100

    issues = gh.search_issues(
        "is:pull-request is:merged",
        sort="updated",
        order="asc",
        author=user,
        created=f">{start_date}",
    )

    return list(issue._rawData for issue in issues)


@click.command(help="Collect a user's PRs and produce YAML")
@click.option(
    "--output",
    type=click.File("w"),
    default="-",
    help="Optional output file, stdout otherwise",
)
@click.option("--user", prompt="Username", help="Username to run on")
@click.option(
    "--start-date", default="2019-03-01", help="Only consider PRs after this date"
)
@click.option("--auth", help="A token to use to authenticate")
def get(output, user, start_date, auth):
    items = get_items(user, start_date, auth)
    print(yaml.dump(items, default_flow_style=False), file=output)


if __name__ == "__main__":
    get()
