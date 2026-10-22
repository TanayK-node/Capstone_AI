"""Shallow, locked-down clone of a paper repository (M7). Nothing in it is ever executed.

git runs with hooks disabled, symlinks checked out as plain files, no file:// / ext:: or
other local protocols, no credential prompts and no LFS downloads; blobs over 2 MB are not
fetched. The clone is deleted if it exceeds the size cap.
"""

from __future__ import annotations

import contextlib
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from app.schemas.code import RepoCandidate

_TREE = re.compile(r"^(https?://[^/]+/[^/]+/[^/]+?)(?:\.git)?/(?:tree|blob)/[^/]+/(.+?)/?$")


class CloneError(RuntimeError):
    pass


class RepoTooLargeError(CloneError):
    pass


@dataclass
class Clone:
    path: Path
    commit: str | None
    size_mb: float
    subdir: str | None


def split_url(url: str) -> tuple[str, str | None]:
    """https://github.com/o/r/tree/main/examples/x -> (https://github.com/o/r, examples/x)."""
    url = url.strip().rstrip("/").removesuffix(".git")
    if not url.startswith("http"):
        return url, None  # a local path (tests only: file:// needs allow_file_protocol)
    if m := _TREE.match(url):
        return m.group(1), m.group(2)
    parts = url.split("/")
    return "/".join(parts[:5]), None  # scheme, '', host, owner, repo


def _git_env(home: Path) -> dict[str, str]:
    return {
        "PATH": os.environ.get("PATH", ""),
        "HOME": str(home),  # no user ~/.gitconfig
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_LFS_SKIP_SMUDGE": "1",
        # Keep the environment's proxy / CA settings so clones work behind a proxy.
        **{k: v for k, v in os.environ.items() if k.lower().endswith("_proxy") or k in (
            "SSL_CERT_FILE", "GIT_SSL_CAINFO", "REQUESTS_CA_BUNDLE")},
    }  # fmt: skip


SAFE_CONFIG = [
    "-c", "core.hooksPath=/dev/null",
    "-c", "core.symlinks=false",
    "-c", "protocol.allow=never",
    "-c", "protocol.https.allow=always",
    "-c", "advice.detachedHead=false",
]  # fmt: skip


def clone(
    candidate: RepoCandidate,
    dest: Path,
    *,
    timeout_s: float = 60,
    max_mb: float = 200,
    allow_file_protocol: bool = False,  # tests clone local fixture repos only
) -> Clone:
    base, subdir = split_url(candidate.url)
    subdir = candidate.subdir or subdir
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    home = dest.parent / ".git-home"
    home.mkdir(exist_ok=True)
    config = list(SAFE_CONFIG)
    if allow_file_protocol:
        config += ["-c", "protocol.file.allow=always"]
    cmd = ["git", *config, "clone", "--depth", "1", "--single-branch", "--no-tags",
           "--filter=blob:limit=2m"]  # fmt: skip
    if subdir:
        cmd.append("--sparse")
    cmd += [base, str(dest)]
    _run(cmd, home, timeout_s)
    if subdir:
        _run(["git", *config, "-C", str(dest), "sparse-checkout", "set", subdir], home, timeout_s)
    size = _size_mb(dest)
    if size > max_mb:
        shutil.rmtree(dest, ignore_errors=True)
        raise RepoTooLargeError(f"repository is {size:.0f} MB (limit {max_mb:.0f} MB)")
    commit = None
    with contextlib.suppress(CloneError):
        commit = _run(["git", "-C", str(dest), "rev-parse", "HEAD"], home, 10).strip() or None
    return Clone(dest, commit, size, subdir)


def _run(cmd: list[str], home: Path, timeout_s: float) -> str:
    try:
        proc = subprocess.run(
            cmd, env=_git_env(home), capture_output=True, text=True, timeout=timeout_s,
            check=False,
        )  # fmt: skip
    except subprocess.TimeoutExpired as exc:
        raise CloneError(f"git timed out after {timeout_s:.0f}s") from exc
    except FileNotFoundError as exc:
        raise CloneError("git is not installed") from exc
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip().splitlines()[-1:] or ["?"]
        raise CloneError(f"git failed: {detail[0][:200]}")
    return proc.stdout


def _size_mb(path: Path) -> float:
    total = 0
    for root, _dirs, files in os.walk(path, followlinks=False):
        for f in files:
            fp = os.path.join(root, f)
            if not os.path.islink(fp):
                total += os.path.getsize(fp)
    return total / 1e6
