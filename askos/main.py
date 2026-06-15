import sys
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
    add_completion=True,
)
cache_app = typer.Typer(help="Manage the local SQLite command query cache.")
app.add_typer(cache_app, name="cache")

profile_app = typer.Typer(help="Manage configuration profiles.")
app.add_typer(profile_app, name="profile")

console = Console()

def execute_ask_flow(prompt: str, api_key: str, base_url: str, model_name: str, explain: bool = False):
    """
    Main flow for translating prompt -> command -> confirming execution -> offering correction.
    """
    console.print()
    console.print(
        Panel(
            f"[bold blue]Input Prompt:[/bold blue] {prompt}",
            title="[bold cyan]Askos AI Assistant[/bold cyan]",
            subtitle="[dim]Safe AI Execution[/dim]",
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
        
        # Scan for safety issues
        from askos.safety import SafetyScanner
        scanner = SafetyScanner()
        safety_warnings = scanner.scan(command)
        
        console.print()
        if safety_warnings:
            warning_text = ""
            for item in safety_warnings:
                level = item["level"]
                desc = item["warning"]
                color = "red" if level in ("HIGH", "CRITICAL") else "yellow"
                warning_text += f"[bold {color}]⚠️  [{level}] {desc}[/bold {color}]\n"
            
            console.print(
                Panel(
                    warning_text.strip(),
                    title="[bold red]⚠️ SAFETY WARNING ⚠️[/bold red]",
                    border_style="red",
                    expand=False,
                )
            )
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

        # If --explain flag is set, generate and display step-by-step explanation
        if explain:
            console.print("[dim yellow]Generating command explanation...[/dim yellow]")
            client = LLMClient(api_key=api_key, base_url=base_url, model_name=resolved_model)
            
            from rich.live import Live
            from rich.markdown import Markdown
            
            explanation_chunks = []
            panel = Panel(
                "",
                title="[bold yellow]Command Explanation[/bold yellow]",
                border_style="yellow",
                expand=False,
            )
            
            with Live(panel, console=console, refresh_per_second=10) as live:
                for chunk in client.explain_command_stream(command):
                    explanation_chunks.append(chunk)
                    markdown_text = "".join(explanation_chunks)
                    panel.renderable = Markdown(markdown_text)
                    live.update(panel)
            console.print()
        
        # Execute the command with user confirmation
        executor = CommandExecutor()
        exit_code, output = executor.execute(command)
        
        # Log execution
        cache.log_execution(prompt, command, exit_code)
        
        # Loop for iterative self-correction on failure (up to 3 retries)
        retry_count = 0
        max_retries = 3
        current_command = command
        
        while exit_code != 0 and exit_code != 130 and retry_count < max_retries:
            console.print()
            correct = typer.confirm(
                f"[bold yellow]⚠ Command failed (Attempt {retry_count + 1}/{max_retries}). Would you like the AI to generate a corrected version?[/bold yellow]",
                default=True
            )
            if not correct:
                break
                
            retry_count += 1
            console.print("[dim yellow]Analyzing error output and generating correction...[/dim yellow]")
            client = LLMClient(api_key=api_key, base_url=base_url, model_name=resolved_model)
            
            # Incorporate previous failure context if we are on a subsequent retry
            if retry_count > 1:
                augmented_prompt = (
                    f"Original prompt: {prompt}\n"
                    f"Correction attempt {retry_count - 1} failed. Please try to generate a different, working command."
                )
            else:
                augmented_prompt = prompt
                
            corrected_command = client.generate_correction(augmented_prompt, current_command, output)
            
            console.print()
            console.print(
                Panel(
                    Text(corrected_command, style="bold green"),
                    title=f"[bold yellow]Proposed Corrected Command (Attempt {retry_count})[/bold yellow]",
                    border_style="yellow",
                    expand=False,
                )
            )
            console.print()
            
            # Execute the corrected command
            exit_code, output = executor.execute(corrected_command)
            cache.log_execution(prompt + f" (correction-{retry_count})", corrected_command, exit_code)
            current_command = corrected_command

        raise typer.Exit(code=exit_code)
        
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

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
        help="OpenAI-compatible API key (overrides environment config).",
    ),
    base_url: str = typer.Option(
        None,
        "--base-url",
        "-u",
        help="OpenAI-compatible API Base URL (overrides environment config).",
    ),
    model_name: str = typer.Option(
        None,
        "--model",
        "-m",
        help="Model name (overrides environment config).",
    ),
    explain: bool = typer.Option(
        False,
        "--explain",
        "-e",
        help="Generate a step-by-step explanation of the proposed command before execution.",
    ),
):
    """
    Translate a natural language prompt into an OS command and run it safely.
    """
    execute_ask_flow(prompt, api_key, base_url, model_name, explain)

@app.callback()
def callback():
    """
    Askos: AI-powered CLI assistant to safely execute terminal commands.
    """
    pass

@app.command()
def configure():
    """
    Interactively configure your global OpenAI-compatible credentials.
    """
    console.print("\n[bold cyan]🔧 Ask-OS Interactive Configuration[/bold cyan]\n")
    
    current_key = config.get_api_key()
    current_url = config.get_base_url()
    current_model = config.get_model_name()
    
    masked_key = f"...{current_key[-6:]}" if len(current_key) > 6 else ""
    
    api_key = typer.prompt(
        "OpenAI-compatible API Key",
        default=masked_key,
        hide_input=True,
    )
    if api_key == masked_key:
        api_key = current_key
        
    base_url = typer.prompt(
        "API Base URL",
        default=current_url,
    )
    
    model_name = typer.prompt(
        "Default Model Name",
        default=current_model,
    )
    
    config.save_global_config(api_key, base_url, model_name)
    
    console.print()
    console.print("[bold green]✓ Global configuration updated successfully![/bold green]")
    console.print(f"[dim]Settings saved to: {config.GLOBAL_CONFIG_FILE}[/dim]\n")

@cache_app.command(name="clear")
def cache_clear():
    """
    Clear all cached query prompts.
    """
    import os
    from askos.cache import CACHE_FILE
    if CACHE_FILE.exists():
        try:
            os.remove(CACHE_FILE)
            console.print("[bold green]✓ Query cache cleared successfully.[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Failed to clear cache:[/bold red] {e}")
    else:
        console.print("[yellow]Cache is already empty.[/yellow]")

@cache_app.command(name="stats")
def cache_stats():
    """
    View cache database size and statistics.
    """
    import sqlite3
    from askos.cache import CACHE_FILE, init_cache
    if not CACHE_FILE.exists():
        console.print("[yellow]No cache database initialized yet. Run some commands first![/yellow]")
        return
        
    init_cache()
    try:
        with sqlite3.connect(CACHE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM command_cache")
            count = cursor.fetchone()[0]
            
        size_kb = CACHE_FILE.stat().st_size / 1024
        
        console.print()
        console.print(
            Panel(
                f"[bold]Cached Prompts:[/bold] {count}\n"
                f"[bold]Database Size:[/bold] {size_kb:.2f} KB\n"
                f"[bold]Location:[/bold] {CACHE_FILE}",
                title="[bold cyan]Cache Statistics[/bold cyan]",
                expand=False,
            )
        )
        console.print()
    except Exception as e:
        console.print(f"[bold red]Failed to retrieve stats:[/bold red] {e}")

@app.command()
def history(
    limit: int = typer.Option(
        10,
        "--limit",
        "-l",
        help="Number of history records to display.",
    )
):
    """
    View command execution history.
    """
    records = cache.get_history(limit)
    if not records:
        console.print("[yellow]No execution history found yet.[/yellow]")
        return
        
    from rich.table import Table
    table = Table(title="[bold cyan]Ask-OS Command Execution History[/bold cyan]")
    table.add_column("Date/Time", style="dim")
    table.add_column("Prompt", style="blue")
    table.add_column("Command Executed", style="green")
    table.add_column("Status", justify="center")
    
    for prompt, command, exit_code, date_str in records:
        status = "[green]✓ Success[/green]" if exit_code == 0 else f"[red]✗ Failed ({exit_code})[/red]"
        if exit_code == 130:
            status = "[yellow]Cancelled[/yellow]"
        table.add_row(date_str, prompt, command, status)
        
    console.print()
    console.print(table)
    console.print()

@profile_app.command(name="list")
def profile_list():
    """
    List all available profiles.
    """
    profiles = config.list_profiles()
    active = config.get_active_profile()
    
    console.print("\n[bold cyan]🔧 Ask-OS Profiles[/bold cyan]\n")
    for p in profiles:
        if p == active:
            console.print(f"  [bold green]* {p} (active)[/bold green]")
        else:
            console.print(f"    {p}")
    console.print()

@profile_app.command(name="use")
def profile_use(
    name: str = typer.Argument(..., help="Name of the profile to switch to.")
):
    """
    Switch the active profile.
    """
    profiles = config.list_profiles()
    if name not in profiles:
        console.print(f"[bold red]Error:[/bold red] Profile '{name}' does not exist.")
        console.print("Use 'askos profile list' to see all profiles, or 'askos profile create' to make one.")
        raise typer.Exit(code=1)
        
    config.set_active_profile(name)
    console.print(f"\n[bold green]✓ Switched active profile to '{name}'[/bold green]\n")

@profile_app.command(name="create")
def profile_create(
    name: str = typer.Argument(..., help="Name of the new profile to create.")
):
    """
    Create a new configuration profile.
    """
    profiles = config.list_profiles()
    if name in profiles:
        console.print(f"[yellow]Profile '{name}' already exists. Re-configuring...[/yellow]\n")
    else:
        console.print(f"\n[bold cyan]🔧 Creating new profile: '{name}'[/bold cyan]\n")
        
    profile_path = config.get_profile_path(name)
    current_key = ""
    current_url = "https://api.openai.com/v1"
    current_model = "gpt-4o-mini"
    
    if profile_path.exists():
        from dotenv import dotenv_values
        vals = dotenv_values(profile_path)
        current_key = vals.get("OPENAI_API_KEY", "")
        current_url = vals.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        current_model = vals.get("OPENAI_MODEL_NAME", "gpt-4o-mini")

    masked_key = f"...{current_key[-6:]}" if len(current_key) > 6 else ""
    
    api_key = typer.prompt(
        "OpenAI-compatible API Key",
        default=masked_key,
        hide_input=True,
    )
    if api_key == masked_key:
        api_key = current_key
        
    base_url = typer.prompt(
        "API Base URL",
        default=current_url,
    )
    
    model_name = typer.prompt(
        "Model Name",
        default=current_model,
    )
    
    config.save_profile_config(name, api_key, base_url, model_name)
    config.set_active_profile(name)
    
    console.print(f"\n[bold green]✓ Profile '{name}' configured and set as active![/bold green]")
    console.print(f"[dim]Settings saved to: {profile_path}[/dim]\n")

@profile_app.command(name="delete")
def profile_delete(
    name: str = typer.Argument(..., help="Name of the profile to delete.")
):
    """
    Delete a configuration profile.
    """
    active = config.get_active_profile()
    if name == active:
        console.print(f"[bold red]Error:[/bold red] Cannot delete the currently active profile '{name}'.")
        console.print("Please switch to another profile first using 'askos profile use <other_name>'.")
        raise typer.Exit(code=1)
        
    profiles = config.list_profiles()
    if name not in profiles:
        console.print(f"[bold red]Error:[/bold red] Profile '{name}' does not exist.")
        raise typer.Exit(code=1)
        
    confirm = typer.confirm(f"Are you sure you want to delete profile '{name}'?")
    if confirm:
        if config.delete_profile(name):
            console.print(f"\n[bold green]✓ Profile '{name}' deleted successfully.[/bold green]\n")
        else:
            console.print(f"\n[bold red]Error:[/bold red] Failed to delete profile '{name}'.\n")

def main_entrypoint():
    """
    Custom wrapper to support calling `askos "prompt"` directly as a default command.
    """
    subcommands = {"configure", "cache", "history", "profile", "--help", "-h"}
    if len(sys.argv) > 1 and sys.argv[1] not in subcommands:
        sys.argv.insert(1, "ask")
    app()

if __name__ == "__main__":
    main_entrypoint()
