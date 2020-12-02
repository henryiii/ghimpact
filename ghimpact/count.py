#!/usr/bin/env python3

from typing import List, Dict, Any
from collections import Counter

import yaml
import click


# def fromtime(item: str) -> datetime:
#    return datetime.strptime(item, "%Y-%m-%dT%H:%M:%SZ") if item else None
# def ofromtime(item: str) -> Optional[datetime]:
#     return fromtime(item) if item else None

def sort_count(counter):
    return sorted(counter.items(), key=lambda it: (-it[1], it[0]))


@click.command(help="Convert a YAML file into a count of PRs by org and repo")
@click.argument("input_file", type=click.File("r"))
@click.argument("output", type=click.File("w"), default="-")
def count(input_file, output):
    data: List[Dict[str, Any]] = yaml.safe_load(input_file)

    orgs = Counter(pr["repository_url"].split("/")[-2] for pr in data)
    for k, v in sort_count(orgs):
        print(k, v, sep=":", end=" - ", file=output)
        
        repos = Counter(pr["repository_url"].split("/")[-1] for pr in data if pr["repository_url"].split("/")[-2] == k)
        strs = (f"{repo}({repo_count})" for repo, repo_count in sort_count(repos))
        print(*strs, sep=", ", file=output)

if __name__ == "__main__":
    count()
