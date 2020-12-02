## GH Impact

Measure the impact a user has by counting PRs.

This is a [Poetry](https://python-poetry.org/docs/basic-usage/) project.
Install poetry using `pip install poetry` or `brew install peotry` if you use
homebrew.

Run the following to prepare a virtual environment:

```bash
poetry install
```

Then, make a yaml file for a specific user, giving a start date:

```bash
poetry run ghimpact get --user henryiii --output henryiii.yml --start-date 2019-03-01
```

This will use the GH API - don't run too many times per hour or you will be
blocked for an hour. Next, convert the raw data into counts:

```bash
poetry run ghimpact count henryiii.yml
```


## Bonus: setup

To make a package like this one, use:

```bash
poetry new ghimpact
# Answer the prompts as requested
cd ghimact
gh repo create
```

Almost everything will be ready for you.
