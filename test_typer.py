import typer
import asyncio

app = typer.Typer()


@app.command()
async def main():
    """
    A simple async command.
    """
    print("Inside async main")
    await asyncio.sleep(1)
    print("Finished async main")


if __name__ == "__main__":
    app()
