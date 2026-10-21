import pytest

from app.pipeline.ingest.resolver import InputError, resolve


@pytest.mark.parametrize(
    ("raw", "kind", "ident"),
    [
        ("1706.03762", "arxiv", "1706.03762"),
        ("arXiv:2301.12345v2", "arxiv", "2301.12345v2"),
        ("cs.CL/0601001", "arxiv", "cs.CL/0601001"),
        ("https://arxiv.org/abs/1706.03762", "arxiv", "1706.03762"),
        ("https://arxiv.org/pdf/1706.03762v7.pdf", "arxiv", "1706.03762v7"),
        ("arxiv.org/abs/2010.11929", "arxiv", "2010.11929"),
        ("https://arxiv.org/html/2401.00001v1", "arxiv", "2401.00001v1"),
        ("10.48550/arXiv.1706.03762", "arxiv", "1706.03762"),
        ("https://doi.org/10.48550/arXiv.2010.11929", "arxiv", "2010.11929"),
        ("10.18653/v1/N19-1423", "doi", "10.18653/v1/N19-1423"),
        ("https://doi.org/10.1145/3292500.3330701", "doi", "10.1145/3292500.3330701"),
        ("https://openreview.net/forum?id=YicbFdNTTy", "openreview", "YicbFdNTTy"),
        ("https://openreview.net/pdf?id=YicbFdNTTy", "openreview", "YicbFdNTTy"),
        ("https://aclanthology.org/N19-1423/", "acl", "N19-1423"),
        ("https://aclanthology.org/2023.acl-long.1.pdf", "acl", "2023.acl-long.1"),
        (
            "https://www.semanticscholar.org/paper/Attention-is-All-you-Need-Vaswani/"
            "204e3073870fae3d05bcbc2f6a8e263d9b72e776",
            "semantic_scholar",
            "204e3073870fae3d05bcbc2f6a8e263d9b72e776",
        ),
        ("https://example.org/papers/foo.pdf", "pdf_url", "https://example.org/papers/foo.pdf"),
    ],
)
def test_resolves_known_sources(raw: str, kind: str, ident: str) -> None:
    resolved = resolve(raw)
    assert (resolved.kind, resolved.identifier) == (kind, ident)


@pytest.mark.parametrize("raw", ["", "attention is all you need", "https://openreview.net/forum"])
def test_rejects_unusable_input(raw: str) -> None:
    with pytest.raises(InputError):
        resolve(raw)
