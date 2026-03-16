# export_test_svg.py
# Run this script to generate a high-quality SVG of your pytest results.
# Usage: python export_test_svg.py

import subprocess
import sys
from rich.console import Console
from rich.terminal_theme import MONOKAI

console = Console(record=True, width=90)

console.print()
console.print(
    "[bold cyan]  Prompting Helper — Test Suite[/bold cyan]",
    justify="center"
)
console.print(
    "[dim]  Running pytest against src/utils/database.py[/dim]",
    justify="center"
)
console.print()

# Run pytest and capture output
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "--no-header"],
    capture_output=True,
    text=True
)

# Print captured output through rich console
console.print(result.stdout)

if result.returncode == 0:
    console.print("[bold green]  ✅ All tests passed![/bold green]", justify="center")
else:
    console.print("[bold red]  ❌ Some tests failed.[/bold red]", justify="center")

console.print()

# Export to SVG
console.save_svg(
    "images/pytest_results.svg",
    title="Prompting Helper — pytest results",
    theme=MONOKAI,
)

print("SVG saved to images/pytest_results.svg")
