import typer
from llm_client import LLMClient
from workflow import Workflow

app = typer.Typer()

@app.command()
def run(prompt: str):
    """
    python3 cli.py "I want an API to manage employee records"
    """
    llm = LLMClient(provider="openai", model="gpt-4o-mini")
    wf = Workflow(llm)
    wf.run_interactive(prompt)

if __name__ == "__main__":
    app()
