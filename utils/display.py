"""
Display Utilities
Functions for terminal output formatting
"""
from config import Config


def print_separator(title: str = "", width: int = None):
    """
    Print a separator line with optional title
    
    Args:
        title: Optional title text
        width: Width of separator (default from config)
    """
    width = width or Config.SEPARATOR_WIDTH
    
    if title:
        print(f"\n{'='*width}")
        print(f"  {title}")
        print(f"{'='*width}\n")
    else:
        print(f"{'='*width}")


def print_section(title: str, width: int = None):
    """
    Print a section header
    
    Args:
        title: Section title
        width: Width of separator (default from config)
    """
    width = width or Config.SEPARATOR_WIDTH
    print(f"\n{'-'*width}")
    print(f"  {title}")
    print(f"{'-'*width}")


def print_error(message: str):
    """Print an error message"""
    print(f"❌ ERROR: {message}")


def print_success(message: str):
    """Print a success message"""
    print(f"✅ {message}")


def print_warning(message: str):
    """Print a warning message"""
    print(f"⚠️  WARNING: {message}")


def print_info(message: str):
    """Print an info message"""
    print(f"ℹ️  {message}")


def print_header(text: str, width: int = None):
    """
    Print a prominent header with centered text
    
    Args:
        text: Header text
        width: Width of header (default from config)
    """
    width = width or Config.SEPARATOR_WIDTH
    print("\n" + "="*width)
    padding = (width - len(text) - 2) // 2
    print(" "*padding + text)
    print("="*width)
