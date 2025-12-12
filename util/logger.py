"""
Colored console logging utility.

Provides a simple Logger class with colored output for different message types.
Uses ANSI escape codes for terminal colors - works on most Unix terminals and
Windows Terminal/PowerShell.
"""

import sys
from enum import Enum
from typing import TextIO


class Color(Enum):
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"


class Logger:
    """
    Provides colored console output for user feedback.

    All methods are static for convenience. Colors can be disabled
    by setting the class variable `use_colors = False`.

    Example:
        Logger.success("Repository updated!")
        Logger.error("Failed to fetch remote")
        Logger.info("Processing 5 repositories...")
        Logger.warning("Branch 'develop' not found, skipping")
    """

    use_colors: bool = True
    output: TextIO = sys.stdout
    error_output: TextIO = sys.stderr

    @classmethod
    def _format(cls, color: Color, prefix: str, msg: str) -> str:
        """Format a message with color and prefix."""
        if cls.use_colors:
            return f"{color.value}{Color.BOLD.value}{prefix}{Color.RESET.value} {msg}"
        return f"{prefix} {msg}"

    @classmethod
    def success(cls, msg: str) -> None:
        """Print success message in green with checkmark."""
        formatted = cls._format(Color.GREEN, "✓", msg)
        print(formatted, file=cls.output)

    @classmethod
    def error(cls, msg: str) -> None:
        """Print error message in red with X mark."""
        formatted = cls._format(Color.RED, "✗", msg)
        print(formatted, file=cls.error_output)

    @classmethod
    def info(cls, msg: str) -> None:
        """Print info message in blue with arrow."""
        formatted = cls._format(Color.BLUE, "→", msg)
        print(formatted, file=cls.output)

    @classmethod
    def warning(cls, msg: str) -> None:
        """Print warning message in yellow with warning sign."""
        formatted = cls._format(Color.YELLOW, "⚠", msg)
        print(formatted, file=cls.output)

    @classmethod
    def header(cls, msg: str) -> None:
        """Print a header/section title in cyan."""
        if cls.use_colors:
            formatted = f"\n{Color.CYAN.value}{Color.BOLD.value}{'─' * 50}{Color.RESET.value}"
            formatted += f"\n{Color.CYAN.value}{Color.BOLD.value}{msg}{Color.RESET.value}"
            formatted += f"\n{Color.CYAN.value}{Color.BOLD.value}{'─' * 50}{Color.RESET.value}"
        else:
            formatted = f"\n{'─' * 50}\n{msg}\n{'─' * 50}"
        print(formatted, file=cls.output)

    @classmethod
    def dim(cls, msg: str) -> None:
        """Print a dimmed/secondary message."""
        if cls.use_colors:
            formatted = f"\033[90m{msg}{Color.RESET.value}"
        else:
            formatted = msg
        print(formatted, file=cls.output)

    @classmethod
    def newline(cls) -> None:
        """Print an empty line."""
        print(file=cls.output)
