import typer

from practice_turkish.translation import translation
from practice_turkish.make_csv import make_dictionary as make_csv
from practice_turkish.number import numbers


def license() -> str:
    "Returns the content of `LICENSE` file."
    with open("LICENSE") as f:
        print(f.read())


def main() -> None:
    "Create Typer application and run it."
    app = typer.Typer()
    translation_ = app.command(help="Practice translation")(translation)
    make_csv_ = app.command(help="Create a new CSV dictionary")(make_csv)
    numbers_ = app.command(help="Practice numbers")(numbers)
    license_ = app.command(help="Show license")(license)
    app()


if __name__ == "__main__":
    main()
