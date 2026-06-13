import os
import platform
import shutil

def collect_environment_context() -> str:
    """
    Collects details about the user's operating system, shell, privilege level,
    and available package managers. Returns a formatted context block.
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
    
    context = (
        f"Target OS: {os_name}\n"
        f"Active Shell: {shell_name}\n"
        f"Privilege Level: {privilege}\n"
        f"Available Installers/CLI Tools: {', '.join(pkg_managers) if pkg_managers else 'none detected'}\n"
    )
    return context
