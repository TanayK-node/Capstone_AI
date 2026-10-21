"""Classify user input (M1): arXiv, DOI, OpenReview, ACL Anthology, Semantic Scholar, or a
direct PDF URL. Pure string handling, no network."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal
from urllib.parse import parse_qs, urlparse

SourceKind = Literal["upload", "arxiv", "doi", "openreview", "acl", "semantic_scholar", "pdf_url"]


class InputError(ValueError):
    """The input is not something we know how to fetch."""


@dataclass(frozen=True)
class ResolvedInput:
    kind: SourceKind
    identifier: str  # arXiv id, DOI, OpenReview id, ACL id, S2 id, or the URL itself
    url: str | None = None  # the original URL, if one was given


# New-style (2301.12345, optional version) and old-style (cs.CL/0601001) arXiv ids.
_ARXIV_ID = r"(?:\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?"
_ARXIV_BARE = re.compile(rf"^(?:arxiv:\s*)?({_ARXIV_ID})$", re.IGNORECASE)
_ARXIV_URL = re.compile(rf"arxiv\.org/(?:abs|pdf|html|format)/({_ARXIV_ID})(?:\.pdf)?", re.I)
_ARXIV_DOI = re.compile(rf"^10\.48550/arxiv\.({_ARXIV_ID})$", re.IGNORECASE)
_DOI = re.compile(r"^(10\.\d{4,9}/\S+)$")
_DOI_URL = re.compile(r"(?:dx\.)?doi\.org/(10\.\d{4,9}/\S+)$", re.IGNORECASE)
_ACL_ID = re.compile(r"aclanthology\.org/([A-Za-z0-9.\-]+?)(?:\.pdf)?/?$")
_S2_ID = re.compile(r"semanticscholar\.org/(?:paper/(?:[^/]+/)?|arxiv/)?([0-9a-f]{40})", re.I)


def resolve(raw: str) -> ResolvedInput:
    text = raw.strip()
    if not text:
        raise InputError("empty input")

    if m := _ARXIV_BARE.match(text):
        return ResolvedInput("arxiv", m.group(1))
    if m := _ARXIV_DOI.match(text):
        return ResolvedInput("arxiv", m.group(1))
    if m := _DOI.match(text):
        return ResolvedInput("doi", m.group(1).rstrip("."))

    if not re.match(r"^https?://", text, re.IGNORECASE):
        if "." in text and "/" in text and " " not in text:
            text = "https://" + text  # "arxiv.org/abs/..." without a scheme
        else:
            raise InputError(
                "not a recognised link or identifier; paste an arXiv id, DOI or PDF URL"
            )

    url = text
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")

    if m := _ARXIV_URL.search(url):
        return ResolvedInput("arxiv", m.group(1), url)
    if m := _DOI_URL.search(url):
        doi = m.group(1)
        if a := _ARXIV_DOI.match(doi):
            return ResolvedInput("arxiv", a.group(1), url)
        return ResolvedInput("doi", doi, url)
    if host == "openreview.net":
        ids = parse_qs(parsed.query).get("id")
        if ids:
            return ResolvedInput("openreview", ids[0], url)
        raise InputError("OpenReview link without ?id=")
    if host == "aclanthology.org" and (m := _ACL_ID.search(url)):
        return ResolvedInput("acl", m.group(1), url)
    if host.endswith("semanticscholar.org") and (m := _S2_ID.search(url)):
        return ResolvedInput("semantic_scholar", m.group(1).lower(), url)
    return ResolvedInput("pdf_url", url, url)
