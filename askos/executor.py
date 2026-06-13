import subprocess
import typer
from rich.console import Console

console = Console()

class CommandExecutor:
    """
    Handles user confirmation and execution of the generated OS commands.
    """
    def __init__(self):
        pass

    def execute(self, command: str) -> int:
        """
        Safely prompts the user for confirmation and runs the command in a subprocess.
        """
        # Ask the user for confirmation
        confirm = typer.confirm("Do you want to run this command?", default=False)
        
        if not confirm:
            console.print("[yellow]Execution cancelled.[/yellow]")
            return 130  # Standard exit code for cancellation
        
        console.print("[dim yellow]Executing command...\n[/dim yellow]")
        
        try:
            # Run the command with shell=True to support pipes, redirects, and environment variables
            result = subprocess.run(command, shell=True)
            
            console.print()
            if result.returncode == 0:
                console.print("[bold green]✓ Command completed successfully.[/bold green]")
            else:
                console.print(f"[bold red]✗ Command exited with code {result.returncode}.[/bold red]")
            return result.returncode
        except Exception as e:
            console.print(f"[bold red]Execution error:[/bold red] {e}")
            return 1
