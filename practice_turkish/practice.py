import typer
from translation import translation
from number import numbers


def license() -> str:
    "Returns the content of `LICENSE` file."
    with open("LICENSE") as f:
        print(f.read())


def main() -> None:
    "Create Typer application and run it."
    app = typer.Typer()
    translation = app.command(help="Practice translation")(translation)
    numbers = app.command(help="Practice numbers")(numbers)
    license = app.command(help="Show license")(license)
    app()


if __name__ == "__main__":
    main()
