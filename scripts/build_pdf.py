"""Compatibility entrypoint. Portfolio content is rendered from HTML by Playwright."""
from pathlib import Path
import subprocess

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    subprocess.run(['node', str(root / 'scripts' / 'build_pdf.cjs')], cwd=root, check=True)
