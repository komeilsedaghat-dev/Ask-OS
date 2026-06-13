import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from askos.llm import LLMClient
from askos.executor import CommandExecutor
from askos import cache
from askos import config

app = typer.Typer(
    name="askos",
    help="AI-powered CLI assistant to translate natural language into OS commands.",
    add_completion=False,
)
console = Console()

@app.command()
def ask(
    prompt: str = typer.Argument(
        ...,
        help="The natural language request for the command you want to run.",
    ),
    api_key: str = typer.Option(
        None,
        "--api-key",
        "-k",
        help="OpenAI-compatible API key (overrides OPENAI_API_KEY environment variable).",
    ),
    base_url: str = typer.Option(
        None,
        "--base-url",
        "-u",
        help="OpenAI-compatible API Base URL (overrides OPENAI_BASE_URL environment variable).",
    ),
    model_name: str = typer.Option(
        None,
        "--model",
        "-m",
        help="Model name (overrides OPENAI_MODEL_NAME environment variable).",
    ),
):
    """
    Translate a natural language prompt into an OS command and run it after confirmation.
    """
    console.print()
    console.print(
        Panel(
            f"[bold blue]Input Prompt:[/bold blue] {prompt}",
            title="[bold cyan]Askos AI Assistant[/bold cyan]",
            subtitle="[dim]Step 4: Caching Enabled[/dim]",
            border_style="cyan",
            expand=False,
        )
    )
    
    try:
        resolved_model = model_name or config.get_model_name()
        
        # Check cache before doing any network/LLM client initialization
        cached_command = cache.get_cached_command(prompt, resolved_model)
        
        if cached_command:
            command = cached_command
            was_cached = True
        else:
            # Initialize LLM client and generate command (caching on write)
            console.print("[dim yellow]Connecting to LLM and generating command...[/dim yellow]")
            client = LLMClient(api_key=api_key, base_url=base_url, model_name=resolved_model)
            command, was_cached = client.generate_command(prompt)
        
        console.print()
        title = "[bold green]Proposed Command (Cached)[/bold green]" if was_cached else "[bold green]Proposed Command[/bold green]"
        console.print(
            Panel(
                Text(command, style="bold green"),
                title=title,
                border_style="green",
                expand=False,
            )
        )
        console.print()
        
        # Execute the command with user confirmation
        executor = CommandExecutor()
        exit_code = executor.execute(command)
        raise typer.Exit(code=exit_code)
        
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
