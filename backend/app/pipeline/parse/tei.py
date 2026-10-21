"""GROBID TEI XML -> ParsedDocument. Pure function, no I/O, so it is unit-testable.

GROBID puts figures and tables at the end of <body>, outside the section divs; we place each
one in reading order after the last text block above it in the same column, and give it that
block's section path.
"""

from __future__ import annotations

import re

from lxml import etree

from app.pipeline.parse.tables import table_from_rows
from app.schemas.document import (
    Author,
    Block,
    BlockType,
    Box,
    DocumentMetadata,
    PageInfo,
    ParsedDocument,
    Reference,
    Sentence,
    union_box,
)

NS = {"t": "http://www.tei-c.org/ns/1.0"}
_WS = re.compile(r"\s+")
# Unnumbered headings that are always top-level, even after numbered sections.
_TOP_LEVEL = re.compile(
    r"^(abstract|references|bibliography|acknowledge?ments?|appendix|appendices|"
    r"supplementary|limitations|ethics|broader impact|conclusions?)\b",
    re.IGNORECASE,
)


def _q(tag: str) -> str:
    return f"{{{NS['t']}}}{tag}"


def clean(text: str | None) -> str:
    return _WS.sub(" ", text or "").strip()


def text_of(el: etree._Element) -> str:
    return clean("".join(el.itertext()))


def parse_coords(value: str | None) -> list[Box]:
    """'page,x,y,w,h;page,x,y,w,h' -> boxes (deduplicated, GROBID sometimes repeats them)."""
    boxes: list[Box] = []
    seen: set[tuple[int, float, float, float, float]] = set()
    for part in (value or "").split(";"):
        bits = part.split(",")
        if len(bits) != 5:
            continue
        try:
            page = int(float(bits[0]))
            x, y, w, h = (float(b) for b in bits[1:])
        except ValueError:
            continue
        key = (page, round(x, 1), round(y, 1), round(w, 1), round(h, 1))
        if key in seen:
            continue
        seen.add(key)
        boxes.append(Box(page=page, x0=x, y0=y, x1=x + w, y1=y + h))
    return boxes


def _sentences(p: etree._Element) -> list[Sentence]:
    return [Sentence(text=text_of(s), boxes=parse_coords(s.get("coords"))) for s in p.iter(_q("s"))]


def _mostly_inside(boxes: list[Box], regions: list[Box], threshold: float = 0.6) -> bool:
    total = sum(b.area for b in boxes)
    if not regions or total <= 0:
        return False
    inside = 0.0
    for b in boxes:
        for r in regions:
            if r.page == b.page:
                w = min(b.x1, r.x1) - max(b.x0, r.x0)
                h = min(b.y1, r.y1) - max(b.y0, r.y0)
                if w > 0 and h > 0:
                    inside += w * h
    return inside / total >= threshold


class _Builder:
    def __init__(self, exclude: list[Box] | None = None) -> None:
        # Table regions: GROBID sometimes reads table headers as headings or paragraphs.
        self.exclude = exclude or []
        self.blocks: list[Block] = []
        self.floating: list[Block] = []  # figures/tables, placed after the text blocks
        self.path: list[tuple[int, str]] = []  # (depth, heading text)
        self.last_numbered_depth = 0

    def section_path(self) -> list[str]:
        return [title for _, title in self.path]

    def add(
        self,
        type_: BlockType,
        text: str,
        boxes: list[Box],
        *,
        sentences: list[Sentence] | None = None,
        label: str | None = None,
        path: list[str] | None = None,
        floating: bool = False,
    ) -> Block | None:
        if not text and type_ not in ("figure", "table"):
            return None
        if type_ in ("heading", "paragraph") and _mostly_inside(boxes, self.exclude):
            return None
        bbox = union_box(boxes)
        block = Block(
            id="",
            type=type_,
            order=0,
            page=bbox.page if bbox else 1,
            bbox=bbox,
            boxes=boxes,
            section_path=path if path is not None else self.section_path(),
            text=text,
            sentences=sentences or [],
            label=label,
        )
        (self.floating if floating else self.blocks).append(block)
        return block

    def heading(self, head: etree._Element) -> None:
        title = text_of(head)
        if not title or _mostly_inside(parse_coords(head.get("coords")), self.exclude):
            return
        n = (head.get("n") or "").strip().rstrip(".")
        if n:
            depth = n.count(".") + 1
            self.last_numbered_depth = depth
            title = f"{n} {title}"
        elif _TOP_LEVEL.match(title) or self.last_numbered_depth == 0:
            depth = 1
            self.last_numbered_depth = 0
        else:
            depth = min(self.last_numbered_depth + 1, 4)  # unnumbered sub-heading
        self.path = [(d, t) for d, t in self.path if d < depth] + [(depth, title)]
        self.add("heading", title, parse_coords(head.get("coords")))

    def div(self, div: etree._Element, *, top_title: str | None = None) -> None:
        if top_title is not None:
            self.path = [(1, top_title)]
            self.last_numbered_depth = 0
        for child in div:
            tag = etree.QName(child).localname
            if tag == "head":
                self.heading(child)
            elif tag == "p":
                sents = _sentences(child)
                text = " ".join(s.text for s in sents) if sents else text_of(child)
                boxes = parse_coords(child.get("coords"))
                if not boxes:
                    boxes = [b for s in sents for b in s.boxes]
                self.add("paragraph", text, boxes, sentences=sents)
            elif tag == "formula":
                label_el = child.find("t:label", NS)
                label = text_of(label_el) if label_el is not None else None
                self.add("equation", text_of(child), parse_coords(child.get("coords")), label=label)
            elif tag == "figure":
                self.figure(child)
            elif tag == "note" and child.get("place") == "foot":
                self.add("footnote", text_of(child), parse_coords(child.get("coords")))
            elif tag == "div":
                self.div(child)

    def figure(self, fig: etree._Element) -> None:
        is_table = fig.get("type") == "table"
        head = fig.find("t:head", NS)
        label_el = fig.find("t:label", NS)
        desc = fig.find("t:figDesc", NS)
        head_text = text_of(head) if head is not None else ""
        number = text_of(label_el) if label_el is not None else ""
        kind = "Table" if is_table else "Figure"
        label = f"{kind} {number}" if number else (head_text.rstrip(" :.") or None)
        caption = text_of(desc) if desc is not None else ""
        text = f"{label}: {caption}" if label and caption else (caption or label or "")
        block = self.add(
            "table" if is_table else "figure",
            text,
            parse_coords(fig.get("coords")),
            label=label,
            path=[],
            floating=True,
        )
        if block is not None and is_table:
            rows = [[text_of(cell) for cell in row.iter(_q("cell"))] for row in fig.iter(_q("row"))]
            # GROBID's own grid is lossy; parse/grobid.py rebuilds it from the PDF and keeps
            # this one only as a fallback.
            block.table = table_from_rows(rows, caption=caption, label=label)

    def place_floating(self) -> None:
        """Insert figures/tables after the last text block above them in the same column."""
        for fig in self.floating:
            if fig.bbox is None:
                self.blocks.append(fig)
                continue
            insert_at = 0
            path: list[str] = []
            for i, b in enumerate(self.blocks):
                if b.bbox is None:
                    continue
                same_col = min(b.bbox.x1, fig.bbox.x1) - max(b.bbox.x0, fig.bbox.x0) > 0
                above = (b.bbox.page, b.bbox.y0) <= (fig.bbox.page, fig.bbox.y0)
                if b.bbox.page < fig.bbox.page or (above and same_col):
                    insert_at, path = i + 1, b.section_path
            fig.section_path = path
            self.blocks.insert(insert_at, fig)


def tei_to_document(
    xml: bytes, parser_version: str = "unknown", exclude: list[Box] | None = None
) -> ParsedDocument:
    """Convert GROBID TEI. `exclude`: regions (tables) whose headings/paragraphs are dropped."""
    root = etree.fromstring(xml)
    pages = [
        PageInfo(
            number=int(s.get("n") or i + 1),
            width=float(s.get("lrx") or 0),
            height=float(s.get("lry") or 0),
        )
        for i, s in enumerate(root.iterfind(".//t:facsimile/t:surface", NS))
    ]
    builder = _Builder(exclude)

    # ---- header
    meta = DocumentMetadata()
    title_el = root.find(".//t:teiHeader/t:fileDesc/t:titleStmt/t:title", NS)
    if title_el is not None and text_of(title_el):
        meta.title = clean_title(text_of(title_el))
        builder.add("title", meta.title, parse_coords(title_el.get("coords")), path=[])
    for author in root.iterfind(".//t:sourceDesc/t:biblStruct/t:analytic/t:author", NS):
        pers = author.find("t:persName", NS)
        if pers is None:
            continue
        aff = author.find("t:affiliation", NS)
        # forename/surname are adjacent elements with no whitespace between them.
        name = clean(" ".join(text_of(part) for part in pers))
        meta.authors.append(
            Author(name=name, affiliation=text_of(aff) if aff is not None else None)
        )
    for idno in root.iterfind(".//t:sourceDesc/t:biblStruct//t:idno", NS):
        if idno.get("type") == "DOI":
            meta.doi = clean(idno.text)
        elif idno.get("type") == "arXiv":
            meta.arxiv_id = clean(idno.text).removeprefix("arXiv:")
    date = root.find(".//t:sourceDesc/t:biblStruct//t:imprint/t:date", NS)
    if date is not None and date.get("when"):
        meta.year = date.get("when", "")[:4]

    abstract = root.find(".//t:profileDesc/t:abstract", NS)
    if abstract is not None:
        builder.path = [(1, "Abstract")]
        for div in (
            abstract.iterfind(".//t:div", NS)
            if abstract.find(".//t:div", NS) is not None
            else [abstract]
        ):
            builder.div(div)
        meta.abstract = (
            " ".join(b.text for b in builder.blocks if b.section_path == ["Abstract"]) or None
        )

    # ---- body
    body = root.find(".//t:text/t:body", NS)
    builder.path, builder.last_numbered_depth = [], 0
    if body is not None:
        builder.div(body)

    # ---- back matter
    back = root.find(".//t:text/t:back", NS)
    references: list[Reference] = []
    if back is not None:
        for div in back.iterfind("t:div", NS):
            kind = div.get("type")
            if kind == "references":
                builder.path = [(1, "References")]
                for bib in div.iter(_q("biblStruct")):
                    ref = _reference(bib)
                    references.append(ref)
                    builder.add("reference", ref.text, ref.boxes)
            elif kind == "acknowledgement":
                builder.div(div, top_title="Acknowledgements")
            elif kind == "annex":
                builder.div(div, top_title="Appendix")
            else:
                builder.div(div)

    builder.place_floating()
    for i, block in enumerate(builder.blocks):
        block.order = i
        block.id = f"b{i:04d}"
    return ParsedDocument(
        parser="grobid",
        parser_version=parser_version,
        pages=pages,
        metadata=meta,
        blocks=builder.blocks,
        references=references,
    )


def _reference(bib: etree._Element) -> Reference:
    raw = bib.find("t:note[@type='raw_reference']", NS)
    title = bib.find("t:analytic/t:title", NS)
    if title is None:
        title = bib.find("t:monogr/t:title", NS)
    date = bib.find(".//t:imprint/t:date", NS)
    ref = Reference(
        id=bib.get("{http://www.w3.org/XML/1998/namespace}id") or "",
        text=text_of(raw) if raw is not None else text_of(bib),
        title=text_of(title) if title is not None else None,
        year=(date.get("when") or "")[:4] or None if date is not None else None,
        boxes=parse_coords(bib.get("coords")),
    )
    for idno in bib.iterfind(".//t:idno", NS):
        if idno.get("type") == "DOI":
            ref.doi = clean(idno.text)
        elif idno.get("type") == "arXiv":
            ref.arxiv_id = clean(idno.text).removeprefix("arXiv:")
    return ref


# Front-page notices GROBID sometimes merges into the title ("Provided proper attribution is
# provided, Google hereby grants permission ... works. Attention Is All You Need").
_NOTICE = re.compile(
    r"permission|copyright|licen[cs]e|attribution|preprint|under review|accepted (at|to)|"
    r"proceedings|conference|workshop|©",
    re.IGNORECASE,
)


def clean_title(title: str) -> str:
    """Drop leading sentences that are notices, keeping the real title after them."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", title.strip())
    while len(parts) > 1 and _NOTICE.search(parts[0]):
        parts = parts[1:]
    return " ".join(parts)
