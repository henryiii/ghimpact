#!/usr/bin/env python3

import sys
import itertools
import json
from pathlib import Path

import hist
import yaml
import click


@click.command(help="Convert a set of YAML file into a json file for d3")
@click.argument("input_files", type=click.File("r"), nargs=-1)
@click.option("--options", type=click.File("r"))
@click.option("--output", type=click.File("w"), default="-")
def d3(input_files, options, output):

    opts = yaml.safe_load(options)
    cats = opts["categories"]
    all_orgs = set(org for cat in cats for org in cat["orgs"])
    filter_repo = set(opts["repos"]) if "repos" in opts else set()

    h = hist.Hist(
        hist.axis.StrCategory([], growth=True, name="author"),
        hist.axis.StrCategory([], growth=True, name="org_repo"),
        storage=hist.storage.Int64(),
    )

    for input_file in input_files:
        author_file = Path(input_file.name)
        print("Reading", author_file, file=sys.stderr)

        data = yaml.safe_load(input_file)
        print("Finished reading", author_file, file=sys.stderr)

        org = (pr["repository_url"].split("/")[-2] for pr in data)
        repo = (pr["repository_url"].split("/")[-1] for pr in data)

        org_repo = [f"{o}:{r}" for o, r in zip(org, repo) if o in all_orgs]

        h.fill(
            author=author_file.stem,
            org_repo=org_repo,
        )

    nodes = []
    links = []

    for org_repo in h.axes["org_repo"]:
        org = org_repo.split(":")[0]
        for cat in cats:
            if org in cat["orgs"]:
                group = cat["value"]
                break
        else:
             raise ValueError(f"That can't happen, {org} is already filtered!")

        nodes.append(dict(id=org_repo, group=group))

    print(f"Built nodes list with {len(nodes)} nodes", file=sys.stderr)

    nodes_ids = [v["id"] for v in nodes]
    lh = hist.Hist(
        hist.axis.StrCategory(nodes_ids, name="source"),
        hist.axis.StrCategory(nodes_ids, name="target"),
        storage=hist.storage.Int64(),
    )

    for a, b in itertools.combinations(nodes_ids, 2):

        for author in h.axes["author"]:
            if (res1 := h[author, a]) > 0 and (res2 := h[author, b] > 0):
                lh.fill(source=a, target=b, weight=res1*res2)

    print("Filled links histogram")

    for source in lh.axes["source"]:
        for target in lh.axes["target"]:
            if (value := lh[source, target]) > 0:
                links.append(dict(source=source, target=target, value=value))

    out_dict = dict(nodes=nodes, links=links)
    j = json.dumps(out_dict, sort_keys=True, indent=2)
    print(j, file=output)
    print("Finished")


if __name__ == "__main__":
    d3()
