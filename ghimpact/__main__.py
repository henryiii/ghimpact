import click

from .get import get
from .count import count

@click.group()
def main():
    pass

main.add_command(get)
main.add_command(count)

if __name__ == "__main__":
    main()


