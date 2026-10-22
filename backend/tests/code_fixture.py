"""A tiny local git repository standing in for a paper's code (no network in tests)."""

from __future__ import annotations

import subprocess
from pathlib import Path

FILES = {
    "README.md": "# SparseRoute\n\n```bash\npython train.py --lr 3e-4 --batch_size 256\n```\n",
    # The default disagrees with the paper (3e-4): a paper-code mismatch to find.
    "train.py": (
        "import argparse\n"
        "p = argparse.ArgumentParser()\n"
        "p.add_argument('--lr', type=float, default=1e-3)\n"
        "p.add_argument('--dropout', type=float, default=0.1)\n"
        "args = p.parse_args()\n"
        "open('/tmp/PAPERLENS_EXECUTED', 'w').write('this must never run')\n"
    ),
    "configs/base.yaml": "optimizer:\n  lr: 0.001\n  weight_decay: 0.01\ntrain:\n  epochs: 10\n",
    "requirements.txt": "torch==2.4.0\n",
}


def make_repo(root: Path, files: dict[str, str] | None = None) -> Path:
    repo = root / "fixture-repo"
    for name, text in (files or FILES).items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "init.defaultBranch=main"]
    subprocess.run([*git, "init", "-q", str(repo)], check=True)
    subprocess.run([*git, "-C", str(repo), "add", "-A"], check=True)
    subprocess.run([*git, "-C", str(repo), "commit", "-qm", "init"], check=True)
    return repo
