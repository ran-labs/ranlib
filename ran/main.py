import typer


app = typer.Typer()


# ran setup
@app.command()
def setup(integration: str = "none", override: bool = False):
    """Integration can either be github or gitlab"""
    # If not already setup, setup project in current directory

    # Use existing (if there exists one) by default, unless override is True

    # if there does not exist one, or if override is True, do a full initialization

    # By the end of this portion, there should be a .ran/ directory and a ran.toml file

    # Setup github or gitlab integration for ran (register to RAN registry)
    if integration == "github":
        pass
    elif integration == "gitlab":
        pass


# ran install
@app.command()
def install():
    pass


# ran use
@app.command()
def use(paper_impl_id: str):
    pass


# ran remove
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
