"""Repository facts from the GitHub REST API (M6 code items; SCOPE.md F7 "health card").

Phase 3 never clones or runs anything: it reads repo metadata, the root file listing and the
README through the API. Unauthenticated calls allow 60 requests/hour; set GITHUB_TOKEN in
.env for 5000. Any failure leaves `reachable=None` so the items become "unknown", not "missing".
"""

from __future__ import annotations

import logging
import re
from urllib.parse import urlparse

import httpx

from app.schemas.repro import RepoInfo

log = logging.getLogger("paperlens.repro")

API = "https://api.github.com"
README_CHARS = 20_000
# Path parts after owner/name that are not part of the repo name ("/tree/main/src").
_REPO_PATH = re.compile(r"^/([\w.\-]+)/([\w.\-]+?)(?:\.git)?(?:/.*)?$")


def parse_repo_url(url: str) -> RepoInfo:
    parsed = urlparse(url.strip())
    host = (parsed.netloc or "").lower().removeprefix("www.")
    info = RepoInfo(url=url, host=host)
    if m := _REPO_PATH.match(parsed.path):
        info.owner, info.name = m.group(1), m.group(2)
    return info


class GitHubClient:
    def __init__(
        self,
        token: str | None = None,
        *,
        timeout_s: float = 15.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "PaperLens (reproducibility checker)",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._http = httpx.Client(
            base_url=API,
            headers=headers,
            timeout=timeout_s,
            transport=transport,
            follow_redirects=True,  # renamed / moved repositories answer with a 301
        )

    def close(self) -> None:
        self._http.close()

    def inspect(self, url: str) -> RepoInfo:
        info = parse_repo_url(url)
        if info.host != "github.com" or not info.owner or not info.name:
            info.error = f"only GitHub repositories are checked in this phase ({info.host})"
            return info
        base = f"/repos/{info.owner}/{info.name}"
        try:
            resp = self._http.get(base)
            if resp.status_code == 404:
                info.reachable = False
                info.error = "repository not found (404)"
                return info
            if resp.status_code != 200:
                info.error = f"GitHub API HTTP {resp.status_code}: {_message(resp)}"
                return info
            repo = resp.json()
            info.reachable = True
            lic = repo.get("license") or {}
            spdx = lic.get("spdx_id")
            info.license = spdx if spdx and spdx != "NOASSERTION" else lic.get("name")
            info.stars = repo.get("stargazers_count")
            info.pushed_at = repo.get("pushed_at")
            info.archived = repo.get("archived")
            # A redirect means the repo was renamed / moved; keep the canonical name.
            info.owner, info.name = repo["owner"]["login"], repo["name"]

            contents = self._http.get(f"{base}/contents")
            if contents.status_code == 200 and isinstance(contents.json(), list):
                info.root_files = sorted(e["name"] for e in contents.json())
            readme = self._http.get(
                f"{base}/readme", headers={"Accept": "application/vnd.github.raw+json"}
            )
            if readme.status_code == 200:
                info.readme_excerpt = readme.text[:README_CHARS]
        except httpx.HTTPError as exc:
            log.warning("github check failed for %s: %s", url, exc)
            info.error = f"GitHub API unreachable: {type(exc).__name__}"
        return info


def _message(resp: httpx.Response) -> str:
    try:
        text = str(resp.json().get("message", ""))
    except ValueError:
        text = resp.text
    first = text.split(". ")[0].strip()  # e.g. "API rate limit exceeded for 1.2.3.4"
    return first[:120] + ("…" if len(first) > 120 else "")
