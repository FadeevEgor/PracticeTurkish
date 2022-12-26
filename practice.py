import typer
from translation import translation


def license():
    with open("LICENSE") as f:
        print(f.read())


if __name__ == "__main__":
    app = typer.Typer()
    translation = app.command(help="Practice translation")(translation)
    license = app.command(help="Show license")(license)
    app()
