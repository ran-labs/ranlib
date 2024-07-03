import typer


app = typer.Typer()


# ran setup
@app.command()
def setup(integration: str = "none"):
    """Integration can either be github or gitlab"""
    pass


# ran install
@app.command()
def install():
    pass


# ran use
@app.command()
def use(paper_impl_id: str):
    pass


@app.command()
def remove(paper_impl_id: str):
    pass


def generate_lockfile():
    pass


# ran savestate
@app.command()
def savestate():
    generate_lockfile()


# ran lock
@app.command()
def lock():
    generate_lockfile()


# ran loadstate
@app.command()
def loadstate():
    pass


# ran push
@app.command()
def push():
    pass


# Start Typer CLI
if __name__ == "__main__":
    app()
