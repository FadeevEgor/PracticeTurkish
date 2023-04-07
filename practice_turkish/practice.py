import typer

from practice_turkish.translation import translation
from practice_turkish.make_csv import make_dictionary as make_csv
from practice_turkish.number import numbers


def main() -> None:
    "Create Typer application and run it."
    app = typer.Typer()
    app.command(help="Practice translation")(translation)
    app.command(help="Create a new CSV dictionary")(make_csv)
    app.command(help="Practice numbers")(numbers)
    app()


if __name__ == "__main__":
    main()
