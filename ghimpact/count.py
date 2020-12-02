#!/usr/bin/env python3

from typing import List, Dict, Any

import boost_histogram as bh
import yaml
import click


def sort_count(h1):
    pairs = ((a, b) for a, b in zip(h1.axes[0], h1.view()) if b > 0)
    return sorted(pairs, key=lambda p: (-p[1], p[0]))


@click.command(help="Convert a YAML file into a count of PRs by org and repo")
@click.argument("input_file", type=click.File("r"))
@click.argument("output", type=click.File("w"), default="-")
def count(input_file, output):
    data: List[Dict[str, Any]] = yaml.safe_load(input_file)

    h = bh.Histogram(
        bh.axis.StrCategory([], growth=True),
        bh.axis.StrCategory([], growth=True),
        storage=bh.storage.Int64()
    )

    h.fill(
        [pr["repository_url"].split("/")[-2] for pr in data],
        [pr["repository_url"].split("/")[-1] for pr in data],
    )

    org_totals = h[:, sum]

    for k, v in sort_count(org_totals):
        print(k, v, sep=":", end=" - ", file=output)
        
        strs = (f"{repo}({c})" for repo, c in sort_count(h[bh.loc(k),:]))
        print(*strs, sep=", ", file=output)


if __name__ == "__main__":
    count()
