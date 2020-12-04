#!/usr/bin/env python3

import sys
import itertools
import json
from pathlib import Path
from typing import List, Dict, Any

import hist  # type: ignore
import yaml
import click


@click.command(help="Convert a set of YAML file into a json file for d3")
@click.argument("input_files", type=click.File("r"), nargs=-1)
@click.option("--options", type=click.File("r"))
@click.option("--output", type=click.File("w"), default="-")
@click.option("--people/--no-people", default=False)
def d3(input_files: List[Any], options: Any, output: Any, people: bool) -> None:

    opts = yaml.safe_load(options)
    cats = opts["categories"]
    all_orgs = set(org for cat in cats for org in cat["orgs"])
    filter_repos = set(opts["repos"]) if "repos" in opts else set()

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

        org_repo = [
            f"{o}:{r}"
            for o, r in zip(org, repo)
            if o in all_orgs and (not filter_repos or r in filter_repos)
        ]

        h.fill(
            author=author_file.stem,
            org_repo=org_repo,
        )

    nodes = get_nodes(h, cats)
    print(f"Built nodes list with {len(nodes)} nodes")

    if not people:
        links = get_people_links(h, nodes)
        print("Filled links histogram")
        out_dict = dict(nodes=nodes, links=links)

    else:
        people_nodes = get_people_nodes(h)
        links = repo_people_links(h)
        out_dict = dict(nodes=nodes + people_nodes, links=links)

    j = json.dumps(out_dict, sort_keys=True, indent=2)
    print(j, file=output)

    print("Finished")


def get_nodes(h: hist.Hist, cats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    nodes = []
    for org_repo in h.axes["org_repo"]:
        org = org_repo.split(":")[0]
        for cat in cats:
            if org in cat["orgs"]:
                group = cat["value"]
                break
        else:
            raise ValueError(f"That can't happen, {org} is already filtered!")

        nodes.append(dict(id=org_repo, group=group))

    return nodes


def get_people_nodes(h: hist.Hist) -> List[Dict[str, int]]:
    return [{"id": a, "group": 0} for a in h.axes["author"]]


def repo_people_links(h: hist.Hist):
    return [
        dict(source=author, target=org_repo, value=value)
        for author in h.axes["author"]
        for org_repo in h.axes["org_repo"]
        if (value := h[author, org_repo]) > 0
    ]


def get_people_links(h: hist.Hist, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    nodes_ids = [v["id"] for v in nodes]

    lh = hist.Hist(
        hist.axis.StrCategory(nodes_ids, name="source"),
        hist.axis.StrCategory(nodes_ids, name="target"),
        storage=hist.storage.Int64(),
    )

    for a, b in itertools.combinations(nodes_ids, 2):
        for author in h.axes["author"]:
            if (res1 := h[author, a]) > 0 and (res2 := h[author, b] > 0):
                lh.fill(source=a, target=b)

    return [
        dict(source=source, target=target, value=value)
        for source in lh.axes["source"]
        for target in lh.axes["target"]
        if (value := lh[source, target]) > 0
    ]


if __name__ == "__main__":
    d3()
