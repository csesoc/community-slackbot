from app import app
from app.seeders import run_seeders

@app.cli.command("seed")
def seed():
    print("Running Seeders")
    run_seeders()

app.cli.add_command(seed)