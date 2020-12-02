#!/usr/bin/env python3

import requests
import json
import math
import sys
from typing import Any, List, Dict
from datetime import datetime
import yaml
import click


def get_items(user, start_date, page: int = 0)-> List[Dict[str, Any]]:
    "Run with 0 to get and combine all pages."

    base = "https://api.github.com/search/issues"

    query = "+".join([
        "is:pull-request",
        f"author:{user}",
        f"created:>{start_date}",
        "is:merged",
    ])

    params = dict(
        q=query,
        per_page=100,
        page=page or 1,
        sort="updated",
        order="asc",
    )

    query_str = base + "?" + "&".join(f"{k}={v}" for k, v in params.items())

    obj = requests.get(query_str)
    j = json.loads(obj.content)
    try:
        total_count = j["total_count"]
        results = j["items"]
    except KeyError:
        print(j)
        raise

    if page == 0 and total_count > 100:
        total = int(math.ceil(total_count / 100))
        for i in range(2, total + 1):
            print(f"Loading page {i} of {total}", file=sys.stderr)
            results += get_items(user, start_date, i)

    return results

@click.command(help="Collect a user's PRs and produce YAML")
@click.option("--output", type=click.File("w"), default="-", help="Optional output file, stdout otherwise")
@click.option("--user", prompt="Username", help="Username to run on")
@click.option("--start-date", default="2019-03-01", help="Only consider PRs after this date")
def get(output, user, start_date):
    items = get_items(user, start_date)
    print(yaml.dump(items, default_flow_style=False), file=output)


if __name__ == "__main__":
    get()
