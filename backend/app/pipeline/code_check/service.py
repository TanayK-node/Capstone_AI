"""Code stage (M7): discover -> clone -> static scan in the sandbox -> compare with the paper.

No LLM is involved. Every failure is a report status (no_repo, needs_confirmation,
clone_failed, too_large, scan_failed) with the reason, never an exception: the paper's other
results stay usable.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from pydantic import ValidationError

from app.pipeline.code_check.clone import CloneError, RepoTooLargeError, clone
from app.pipeline.code_check.compare import compare
from app.pipeline.code_check.discovery import (
    CONFIRM_BELOW,
    candidates_from_paper,
    candidates_from_search,
)
from app.pipeline.code_check.sandbox import ScanError, run_scanner
from app.pipeline.repro.github import GitHubClient, parse_repo_url
from app.schemas.code import CodeParam, CodeReport, RepoCandidate
from app.schemas.extraction import PaperExtraction

log = logging.getLogger("paperlens.code")


def check_code(
    extraction: PaperExtraction,
    workdir: Path,
    *,
    method_names: list[str],
    github: GitHubClient | None,
    user_repo: str | None = None,
    sandbox: str = "auto",
    clone_timeout_s: float = 60,
    max_repo_mb: float = 200,
    search: bool = True,
    allow_file_protocol: bool = False,
) -> CodeReport:
    candidates = _discover(extraction, method_names, github, user_repo, search)
    report = CodeReport(status="no_repo", candidates=candidates)
    if not candidates:
        report.warnings.append("No repository linked in the paper and none found by search.")
        return report
    best = candidates[0]
    report.repo = parse_repo_url(best.url)
    if best.confidence < CONFIRM_BELOW:
        report.status = "needs_confirmation"
        report.warnings.append(
            f"Best guess {best.url} ({best.reason}); confirm it or give the right repository."
        )
        return report

    if github is not None:
        info = github.inspect(best.url)  # health card: license, stars, last push
        report.repo = info
        if info.owner and info.name and info.reachable:
            report.reproduce_issues = github.reproduce_issues(info.owner, info.name)
    dest = workdir / "repo"
    try:
        cloned = clone(best, dest, timeout_s=clone_timeout_s, max_mb=max_repo_mb,
                       allow_file_protocol=allow_file_protocol)  # fmt: skip
    except RepoTooLargeError as exc:
        report.status = "too_large"
        report.warnings.append(str(exc))
        return report
    except CloneError as exc:
        report.status = "clone_failed"
        report.warnings.append(str(exc))
        return report
    report.commit = cloned.commit
    try:
        scan_root = cloned.path / cloned.subdir if cloned.subdir else cloned.path
        output, mode = run_scanner(scan_root if scan_root.exists() else cloned.path, sandbox)
    except ScanError as exc:
        report.status = "scan_failed"
        report.warnings.append(str(exc))
        return report
    finally:
        shutil.rmtree(dest, ignore_errors=True)  # nothing from the repo is kept
    report.sandbox = mode
    if mode != "docker":
        report.warnings.append(
            "Scanned in a separate process, not the Docker sandbox (build sandbox/Dockerfile "
            "as paperlens-sandbox to isolate it). The scan only parses files either way."
        )
    params: list[CodeParam] = []
    for raw in output.get("params", []):
        try:  # the scanner's output is data from a stranger's repository: validate each row
            params.append(CodeParam.model_validate(raw))
        except ValidationError:
            continue
    report.files_scanned = int(output.get("files_scanned", 0))
    report.params_found = len(params)
    report.comparisons = compare(extraction.hyperparameters, params)
    counts: dict[str, int] = {}
    for row in report.comparisons:
        counts[row.status] = counts.get(row.status, 0) + 1
    report.counts = counts
    report.status = "ok"
    return report


def _discover(
    extraction: PaperExtraction,
    method_names: list[str],
    github: GitHubClient | None,
    user_repo: str | None,
    search: bool,
) -> list[RepoCandidate]:
    if user_repo:
        return [RepoCandidate(url=user_repo, source="user", confidence=1.0,
                              reason="confirmed by the user")]  # fmt: skip
    found = candidates_from_paper(extraction, method_names)
    if found or not search or github is None or not extraction.metadata.title:
        return found
    title = extraction.metadata.title
    return candidates_from_search(
        github.search_repositories(f'"{title}" in:readme,description'), title
    )
