import typer
from .app.services import dot, solve_linear_2x2

app = typer.Typer(add_completion=False)

@app.command()
def dotv(a: str, b: str):
    """Dot product of two comma-separated vectors."""
    av = [float(x) for x in a.split(",") if x]
    bv = [float(x) for x in b.split(",") if x]
    typer.echo(dot(av, bv))

@app.command()
def solve2x2(a11: float, a12: float, a21: float, a22: float, b1: float, b2: float):
    x,y = solve_linear_2x2(a11,a12,a21,a22,b1,b2)
    typer.echo(f"x={x}, y={y}")

if __name__ == "__main__":
    app()
