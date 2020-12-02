import click

from .get import get
from .count import count
from .d3 import d3


@click.group()
def main():
    pass


main.add_command(get)
main.add_command(count)
main.add_command(d3)

if __name__ == "__main__":
    main()
