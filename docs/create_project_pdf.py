"""Create a PDF from PROJECT_DOCUMENTATION.md using a local Chromium browser.

Usage:
    python docs/create_project_pdf.py
    python docs/create_project_pdf.py --output docs/PROJECT_DOCUMENTATION.pdf

The script intentionally uses a browser's print-to-PDF engine so Markdown
headings, lists, tables, code blocks, and page layout are rendered consistently.
No network access is required.
"""

from __future__ import annotations

import argparse
import html
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR / "PROJECT_DOCUMENTATION.md"
DEFAULT_OUTPUT = SCRIPT_DIR / "PROJECT_DOCUMENTATION.pdf"


def find_browser() -> str:
    """Return a usable Chromium-based browser executable."""
    candidates = [
        shutil.which("msedge"),
        shutil.which("chrome"),
        shutil.which("chromium"),
        os.path.expandvars(
            r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
        ),
        os.path.expandvars(
            r"%LocalAppData%\Google\Chrome\Application\chrome.exe"
        ),
    ]

    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate

    raise RuntimeError(
        "No Chromium-based browser was found. Install Microsoft Edge or "
        "Google Chrome, then run this script again."
    )


def markdown_to_html(markdown_text: str) -> str:
    """Convert Markdown to HTML using markdown-it-py."""
    try:
        from markdown_it import MarkdownIt
    except ImportError as exc:
        raise RuntimeError(
            "The 'markdown-it-py' package is required. Install it with "
            "'python -m pip install markdown-it-py'."
        ) from exc

    return MarkdownIt("commonmark", {"html": True}).enable("table").render(
        markdown_text
    )


def build_html(markdown_text: str, source_name: str) -> str:
    """Wrap rendered Markdown in print-friendly HTML."""
    rendered = markdown_to_html(markdown_text)
    title = html.escape(Path(source_name).stem.replace("_", " "))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    @page {{ size: Letter; margin: 0.7in; }}
    :root {{ color-scheme: light; }}
    body {{
      color: #202124;
      font-family: "Segoe UI", Arial, sans-serif;
      font-size: 10.5pt;
      line-height: 1.45;
    }}
    h1, h2, h3, h4 {{ color: #17365d; page-break-after: avoid; }}
    h1 {{ border-bottom: 2px solid #17365d; padding-bottom: 8px; }}
    h2 {{ border-bottom: 1px solid #b7c9e2; padding-bottom: 4px; }}
    h3, h4 {{ margin-bottom: 4px; }}
    p, ul, ol, table, pre {{ page-break-inside: avoid; }}
    table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
    th, td {{ border: 1px solid #b8c2cc; padding: 5px 7px; vertical-align: top; }}
    th {{ background: #eaf1f8; text-align: left; }}
    code {{ background: #f1f3f4; padding: 1px 3px; border-radius: 3px; }}
    pre {{ background: #f5f6f7; border: 1px solid #d8dadd; padding: 9px; overflow-wrap: anywhere; }}
    pre code {{ background: transparent; padding: 0; }}
    a {{ color: #1155cc; }}
    .footer {{ color: #687078; font-size: 8pt; margin-top: 24px; }}
  </style>
</head>
<body>
{rendered}
<div class="footer">Generated from {html.escape(source_name)}</div>
</body>
</html>
"""


def create_pdf(input_path: Path, output_path: Path) -> None:
    """Render the Markdown file to a PDF using a local browser."""
    if not input_path.is_file():
        raise FileNotFoundError(f"Markdown source not found: {input_path}")

    browser = find_browser()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="job-platform-pdf-") as temp_dir:
        html_path = Path(temp_dir) / "project-documentation.html"
        html_path.write_text(
            build_html(
                input_path.read_text(encoding="utf-8"),
                input_path.name,
            ),
            encoding="utf-8",
        )

        command = [
            browser,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={output_path}",
            html_path.as_uri(),
        ]
        subprocess.run(command, check=True)

    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise RuntimeError(f"Browser did not create a valid PDF: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a PDF from the project Markdown documentation."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Markdown source file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="PDF output file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    create_pdf(args.input.resolve(), args.output.resolve())
    print(f"Created PDF: {args.output.resolve()}")


if __name__ == "__main__":
    main()
