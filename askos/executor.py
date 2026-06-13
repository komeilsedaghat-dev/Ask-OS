import subprocess
import sys
import typer
from rich.console import Console

console = Console()

class CommandExecutor:
    """
    Handles user confirmation and execution of the generated OS commands.
    """
    def __init__(self):
        pass

    def execute(self, command: str) -> tuple[int, str]:
        """
        Safely prompts the user for confirmation and runs the command in a subprocess,
        streaming stdout/stderr in real-time while capturing it.
        
        Returns:
            (exit_code, captured_output)
        """
        # Loop to handle Run, Cancel, or Edit actions
        while True:
            choice = typer.prompt(
                "Action? [y]run, [n]cancel, [e]edit",
                default="y",
            ).strip().lower()
            
            if choice == "y":
                break
            elif choice == "n":
                console.print("[yellow]Execution cancelled.[/yellow]")
                return 130, ""
            elif choice == "e":
                import readline
                # Prefill the command input buffer so the user can edit in-place
                readline.set_startup_hook(lambda: readline.insert_text(command))
                try:
                    command = input("Edit command: ").strip()
                finally:
                    readline.set_startup_hook() # Clear hook
                
                console.print(f"[dim yellow]Updated command: {command}[/dim yellow]\n")
            else:
                console.print("[red]Invalid option. Please choose y, n, or e.[/red]")
        
        console.print("[dim yellow]Executing command...\n[/dim yellow]")
        
        captured_output = []
        returncode = 0
        
        try:
            # Run the command, merging stderr into stdout, and streaming it
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    sys.stdout.write(line)
                    sys.stdout.flush()
                    captured_output.append(line)
                    
            returncode = process.wait()
            
        except KeyboardInterrupt:
            console.print("\n[bold red]Execution interrupted by user.[/bold red]")
            if process:
                process.terminate()
                process.wait()
            return 130, "".join(captured_output)
            
        except Exception as e:
            console.print(f"[bold red]Execution error:[/bold red] {e}")
            return 1, "".join(captured_output)
            
        console.print()
        if returncode == 0:
            console.print("[bold green]✓ Command completed successfully.[/bold green]")
        else:
            console.print(f"[bold red]✗ Command exited with code {returncode}.[/bold red]")
            
        return returncode, "".join(captured_output)
