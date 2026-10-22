"""Run the static scanner in the sandbox (CLAUDE.md rule 6).

docker:  the paperlens-sandbox image (sandbox/Dockerfile), no network, read-only root,
         repository mounted read-only, memory / pid / CPU limits, non-root user.
process: a separate `python -I` process with CPU / memory limits (Linux) and a timeout,
         for setups without Docker access (e.g. inside the compose worker). The scanner only
         parses files in both modes; the mode used is recorded in the report.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

SCANNER = Path(__file__).with_name("scanner.py")
IMAGE = "paperlens-sandbox"


class ScanError(RuntimeError):
    pass


def docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        proc = subprocess.run(
            ["docker", "image", "inspect", IMAGE], capture_output=True, timeout=10, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0


def run_scanner(
    repo: Path, mode: str = "auto", timeout_s: float = 60
) -> tuple[dict[str, Any], str]:
    """Returns (scanner output, mode used)."""
    use = "docker" if mode == "docker" or (mode == "auto" and docker_available()) else "process"
    if use == "docker":
        cmd = [
            "docker", "run", "--rm", "--network", "none", "--read-only",
            "--memory", "512m", "--pids-limit", "64", "--cpus", "1",
            "--security-opt", "no-new-privileges",
            "-v", f"{repo.resolve()}:/repo:ro",
            "-v", f"{SCANNER.resolve()}:/work/scan.py:ro",
            IMAGE, "/work/scan.py", "/repo",
        ]  # fmt: skip
        preexec = None
    else:
        cmd = [sys.executable, "-I", str(SCANNER), str(repo.resolve())]
        preexec = _limits if sys.platform != "win32" else None
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout_s, check=False,
            preexec_fn=preexec, cwd=str(repo.parent),
        )  # fmt: skip
    except subprocess.TimeoutExpired as exc:
        raise ScanError(f"scanner timed out after {timeout_s:.0f}s ({use})") from exc
    if proc.returncode != 0:
        raise ScanError(f"scanner failed ({use}): {proc.stderr.strip()[-300:]}")
    try:
        return json.loads(proc.stdout), use
    except json.JSONDecodeError as exc:
        raise ScanError(f"scanner output was not JSON ({use})") from exc


def _limits() -> None:  # pragma: no cover - runs in the child process
    import resource

    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    resource.setrlimit(resource.RLIMIT_AS, (1_500_000_000, 1_500_000_000))
    resource.setrlimit(resource.RLIMIT_FSIZE, (10_000_000, 10_000_000))
