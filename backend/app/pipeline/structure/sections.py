"""Section tree, role assignment and hierarchical chunking (M3)."""

from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from app.llm.client import LLMClient
from app.pipeline.structure.roles import (
    CHILD_OVERRIDES,
    classify_heading,
    classify_with_llm,
    is_appendix_number,
)
from app.schemas.document import Block, Box, ParsedDocument, SectionRole

CHUNKED_TYPES = {"paragraph", "table", "figure", "caption", "equation", "footnote"}


class SectionNode(BaseModel):
    id: str  # "s003"
    title: str
    path: list[str]
    depth: int
    role: SectionRole
    role_source: str  # "rule", "llm", "inherited", "position", "default"
    page: int
    block_ids: list[str] = Field(default_factory=list)  # blocks directly in this section
    children: list[str] = Field(default_factory=list)


class Chunk(BaseModel):
    id: str
    level: str  # "section" | "paragraph" | "sentence"
    parent_id: str | None
    order: int
    block_ids: list[str]
    section_path: list[str]
    role: SectionRole
    page: int
    boxes: list[Box]
    text: str


@dataclass
class StructureResult:
    sections: list[SectionNode]
    block_roles: dict[str, SectionRole]
    chunks: list[Chunk]
    llm_prompt_version: str | None = None
    warnings: list[str] = field(default_factory=list)


def build_sections(doc: ParsedDocument) -> list[SectionNode]:
    nodes: dict[tuple[str, ...], SectionNode] = {}
    order: list[SectionNode] = []
    for block in doc.blocks:
        path = tuple(block.section_path)
        if not path:
            continue
        for depth in range(1, len(path) + 1):
            key = path[:depth]
            if key in nodes:
                continue
            node = SectionNode(
                id=f"s{len(order):03d}",
                title=key[-1],
                path=list(key),
                depth=depth,
                role="other",
                role_source="default",
                page=block.page,
            )
            nodes[key] = node
            order.append(node)
            if depth > 1:
                nodes[key[:-1]].children.append(node.id)
        if block.type != "heading":
            nodes[path].block_ids.append(block.id)
    return order


def assign_roles(
    doc: ParsedDocument, sections: list[SectionNode], client: LLMClient | None
) -> str | None:
    """Rule-based roles; top-level sections the rules can't place go to one LLM call."""
    by_path = {tuple(s.path): s for s in sections}
    blocks = {b.id: b for b in doc.blocks}
    after_references = False
    unresolved: list[SectionNode] = []

    for node in sections:
        role = classify_heading(node.title)
        if node.depth == 1:
            if role == "references":
                after_references = True
            elif after_references and role is None:
                role = "appendix"  # unlabelled sections after the bibliography
            if role is None and is_appendix_number(node.title):
                role = "appendix"
            if role is None:
                unresolved.append(node)
                continue
            node.role, node.role_source = role, "rule"
        else:
            parent = by_path[tuple(node.path[:-1])]
            if role in CHILD_OVERRIDES:
                node.role, node.role_source = role, "rule"
            else:
                node.role, node.role_source = parent.role, "inherited"

    version: str | None = None
    if unresolved:
        snippets = []
        for node in unresolved:
            first = next(
                (blocks[b].text for b in node.block_ids if blocks[b].type == "paragraph"), ""
            )
            snippets.append((node.title, first))
        llm_roles, version = classify_with_llm(client, snippets)
        for i, node in enumerate(unresolved):
            if i in llm_roles:
                node.role, node.role_source = llm_roles[i], "llm"
        # Re-inherit for children of sections the LLM just labelled.
        for node in sections:
            if node.depth > 1 and node.role_source == "inherited":
                node.role = by_path[tuple(node.path[:-1])].role
    return version


def build_chunks(doc: ParsedDocument, sections: list[SectionNode]) -> list[Chunk]:
    """section -> paragraph -> sentence chunks, each keeping parents and coordinates."""
    by_path = {tuple(s.path): s for s in sections}
    blocks = {b.id: b for b in doc.blocks}
    chunks: list[Chunk] = []

    def add(**kwargs: object) -> Chunk:
        chunk = Chunk(order=len(chunks), **kwargs)
        chunks.append(chunk)
        return chunk

    for node in sections:
        members = [blocks[b] for b in node.block_ids if blocks[b].type in CHUNKED_TYPES]
        if not members:
            continue
        parent_section = by_path.get(tuple(node.path[:-1]))
        section_chunk = add(
            id=f"{node.id}",
            level="section",
            parent_id=parent_section.id if parent_section else None,
            block_ids=[b.id for b in members],
            section_path=node.path,
            role=node.role,
            page=members[0].page,
            boxes=[b.bbox for b in members if b.bbox is not None],
            text="\n\n".join([node.title, *(_chunk_text(b) for b in members)]),
        )
        for block in members:
            para = add(
                id=f"{block.id}",
                level="paragraph",
                parent_id=section_chunk.id,
                block_ids=[block.id],
                section_path=node.path,
                role=node.role,
                page=block.page,
                boxes=block.boxes,
                text=_chunk_text(block),
            )
            for k, sent in enumerate(block.sentences):
                if not sent.text:
                    continue
                boxes = sent.boxes or block.boxes
                add(
                    id=f"{block.id}.{k}",
                    level="sentence",
                    parent_id=para.id,
                    block_ids=[block.id],
                    section_path=node.path,
                    role=node.role,
                    page=boxes[0].page if boxes else block.page,
                    boxes=boxes,
                    text=sent.text,
                )
    return chunks


def _chunk_text(block: Block) -> str:
    if block.type == "table" and block.table is not None:
        rows = "\n".join(" | ".join(r) for r in block.table.grid())
        return f"{block.text}\n{rows}"
    return block.text


def structure_document(doc: ParsedDocument, client: LLMClient | None) -> StructureResult:
    sections = build_sections(doc)
    version = assign_roles(doc, sections, client)
    role_of = {tuple(s.path): s.role for s in sections}
    block_roles: dict[str, SectionRole] = {}
    for block in doc.blocks:
        if block.section_path:
            block_roles[block.id] = role_of[tuple(block.section_path)]
    warnings = [
        f"section {s.title!r}: role unknown" for s in sections if s.role_source == "default"
    ]
    return StructureResult(sections, block_roles, build_chunks(doc, sections), version, warnings)
