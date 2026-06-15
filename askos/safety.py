import re

class SafetyScanner:
    """
    Scans terminal commands for potential hazards or destructive operations.
    """
    def __init__(self):
        # List of rules: (regex pattern, risk level, description/warning)
        self.rules = [
            (
                r"\brm\s+-[a-zA-Z]*[rfRF]+[a-zA-Z]*\b",
                "HIGH",
                "Recursive deletion detected (rm -r / rm -f). This can permanently delete files and directories."
            ),
            (
                r"\b(mkfs|fdisk|parted|sfdisk|gparted)\b",
                "CRITICAL",
                "Disk formatting or partitioning tool detected. This can lead to complete data loss on storage devices."
            ),
            (
                r"\bdd\s+if=",
                "CRITICAL",
                "Low-level copy tool (dd) detected. Writing directly to disks/partitions can overwrite critical system files."
            ),
            (
                r"\bchown\s+.*(/etc|/usr|/var|/boot|/sys|/proc|/)\b",
                "HIGH",
                "System-wide ownership change detected. Modifying critical path ownership can break system permissions."
            ),
            (
                r"\bchmod\s+.*(/etc|/usr|/var|/boot|/sys|/proc|/)\b",
                "HIGH",
                "System-wide permission change detected. Modifying critical path permissions can render the OS unusable."
            ),
            (
                r"\bcurl\s+.*\|\s*(sudo\s+)?(bash|sh|zsh)\b",
                "HIGH",
                "Piping external web script directly into a shell interpreter. This executes remote unverified code."
            ),
            (
                r"\b(shutdown|reboot|poweroff|init\s+0|init\s+6)\b",
                "MEDIUM",
                "System shutdown or reboot command detected."
            ),
            (
                r"(>>|>)\s*(/dev/sd[a-z]|/dev/nvme[0-9]n[0-9]|/dev/loop[0-9])",
                "CRITICAL",
                "Direct redirection to a raw block device detected. This will overwrite the target disk partition."
            ),
            (
                r"\b:\(\)\{\s*:\s*\|\s*:\s*&\s*\};\s*:",
                "CRITICAL",
                "Fork bomb pattern detected. This will freeze the system by exhaustively consuming all processes."
            )
        ]

    def scan(self, command: str) -> list[dict]:
        """
        Scans a command against safety rules.
        Returns a list of warning dicts: [{"level": "...", "warning": "..."}]
        """
        warnings = []
        normalized_command = command.strip()
        
        for pattern, level, warning in self.rules:
            if re.search(pattern, normalized_command):
                warnings.append({
                    "level": level,
                    "warning": warning
                })
        return warnings
