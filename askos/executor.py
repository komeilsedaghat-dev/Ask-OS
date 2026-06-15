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
        process = None
        
        try:
            try:
                # Try to use interactive PTY for Unix systems to support unbuffered output and stdin
                import pty
                import select
                import fcntl
                import os
                import errno

                master_fd, slave_fd = pty.openpty()
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdin=slave_fd,
                    stdout=slave_fd,
                    stderr=slave_fd,
                    close_fds=True,
                )
                os.close(slave_fd)

                # Set master_fd to non-blocking mode
                fl = fcntl.fcntl(master_fd, fcntl.F_GETFL)
                fcntl.fcntl(master_fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

                while True:
                    # Monitor both the process output PTY master_fd and user's stdin
                    r, _, _ = select.select([master_fd, sys.stdin], [], [], 0.05)

                    if master_fd in r:
                        try:
                            data = os.read(master_fd, 4096)
                            if not data:
                                break
                            decoded = data.decode(errors="replace")
                            sys.stdout.write(decoded)
                            sys.stdout.flush()
                            captured_output.append(decoded)
                        except BlockingIOError:
                            pass
                        except OSError as e:
                            if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                                pass
                            else:
                                break

                    if sys.stdin in r:
                        user_input = sys.stdin.readline()
                        if not user_input:
                            break
                        try:
                            os.write(master_fd, user_input.encode())
                        except OSError:
                            break

                    # Check if the process has terminated
                    if process.poll() is not None:
                        # Flush any remaining outputs
                        while True:
                            r_flush, _, _ = select.select([master_fd], [], [], 0.01)
                            if master_fd in r_flush:
                                try:
                                    data = os.read(master_fd, 4096)
                                    if not data:
                                        break
                                    decoded = data.decode(errors="replace")
                                    sys.stdout.write(decoded)
                                    sys.stdout.flush()
                                    captured_output.append(decoded)
                                except OSError:
                                    break
                            else:
                                break
                        break

                returncode = process.wait()
                try:
                    os.close(master_fd)
                except OSError:
                    pass

            except (ImportError, AttributeError):
                # Fallback for Windows or systems without pty/fcntl support
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
            if process and process.poll() is None:
                process.terminate()
                process.wait()
            return 1, "".join(captured_output)
            
        console.print()
        if returncode == 0:
            console.print("[bold green]✓ Command completed successfully.[/bold green]")
        else:
            console.print(f"[bold red]✗ Command exited with code {returncode}.[/bold red]")
            
        return returncode, "".join(captured_output)
