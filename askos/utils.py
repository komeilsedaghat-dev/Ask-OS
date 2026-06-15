import os
import platform
import shutil

def collect_environment_context() -> str:
    """
    Collects details about the user's operating system, shell, privilege level,
    available package managers, and top-level directory contents.
    Returns a formatted context block.
    """
    os_name = platform.system()
    shell_name = os.path.basename(os.environ.get("SHELL", "bash")) if os_name != "Windows" else "PowerShell"
    
    # Check for available package managers/installers
    pkg_managers = []
    candidates = ["apt-get", "brew", "yum", "dnf", "pacman", "zypper", "apk", "pip", "npm", "cargo"]
    for cmd in candidates:
        if shutil.which(cmd):
            pkg_managers.append(cmd)
            
    # Check privilege level on Unix systems
    is_root = False
    if os_name != "Windows":
        try:
            is_root = os.getuid() == 0
        except AttributeError:
            pass
            
    privilege = "root/administrator (sudo not needed)" if is_root else "standard user (prepend sudo for system-level actions)"
    
    # List top-level files/directories in current working directory to give LLM workspace context
    cwd_items = []
    try:
        # Limit items to 40 to avoid bloating context
        raw_items = os.listdir(".")
        sorted_dirs = []
        sorted_files = []
        for item in sorted(raw_items):
            # Ignore hidden files/dirs and standard environment folders to keep prompt clean
            if item.startswith(".") or item in ("venv", "__pycache__", "node_modules", "askos.egg-info"):
                continue
            if os.path.isdir(item):
                sorted_dirs.append(f"{item}/")
            else:
                sorted_files.append(item)
                
        cwd_items = (sorted_dirs + sorted_files)[:40]
    except Exception:
        pass

    context = (
        f"Target OS: {os_name}\n"
        f"Active Shell: {shell_name}\n"
        f"Privilege Level: {privilege}\n"
        f"Available Installers/CLI Tools: {', '.join(pkg_managers) if pkg_managers else 'none detected'}\n"
        f"Current Directory Contents: {', '.join(cwd_items) if cwd_items else 'empty or inaccessible'}\n"
    )
    return context
