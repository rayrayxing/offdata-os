"""Deterministic knowledge-ingestion intelligence and admission controls."""

from __future__ import annotations

import hashlib
import io
import re
import unicodedata
import zipfile
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_INSTRUCTION_MARKERS = (
    "ignore previous",
    "ignore all previous",
    "system prompt",
    "developer message",
    "upload credentials",
    "reveal secret",
    "send externally",
)
_STOP_WORDS = {
    "a",
    "an",
    "and",
    "assessment",
    "analysis",
    "architecture",
    "design",
    "for",
    "model",
    "modeling",
    "modelling",
    "of",
    "or",
    "the",
    "using",
}


class SourceFormat(StrEnum):
    MARKDOWN = "markdown"
    DOCX = "docx"


class BlockKind(StrEnum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"


class ResolutionState(StrEnum):
    RESOLVED = "resolved"
    AMBIGUOUS = "ambiguous"
    QUARANTINED = "quarantined"


class IntendedUse(StrEnum):
    INTERNAL_RETRIEVAL = "internal_retrieval"
    INTERNAL_DERIVATION = "internal_derivation"
    CLIENT_PARAPHRASE = "client_paraphrase"
    EXTERNAL_REDISTRIBUTION = "external_redistribution"


class SourceProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str = Field(min_length=1)
    original_filename: str = Field(min_length=1)
    preferred_repository_filename: str = Field(min_length=1)
    declared_title: str = Field(min_length=1)
    source_format: SourceFormat
    role_or_domain: str = Field(min_length=1)
    checksum_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    byte_size: int = Field(gt=0)
    line_or_paragraph_count: int = Field(gt=0)
    heading_count: int = Field(ge=0)
    method_heading_count: int = Field(ge=0)
    rights_status: str = Field(min_length=1)
    external_redistribution_allowed: bool = False
    import_status: str = Field(min_length=1)
    review_cadence: str = Field(min_length=1)


class SourceBlock(BaseModel):
    model_config = ConfigDict(frozen=True)

    ordinal: int = Field(ge=1)
    kind: BlockKind
    text: str = Field(min_length=1)
    heading_level: int | None = Field(default=None, ge=1, le=9)
    style_name: str = ""
    instruction_like: bool = False

    @model_validator(mode="after")
    def validate_heading(self) -> "SourceBlock":
        if self.kind == BlockKind.HEADING and self.heading_level is None:
            raise ValueError("Heading blocks require a heading level.")
        if self.kind == BlockKind.PARAGRAPH and self.heading_level is not None:
            raise ValueError("Paragraph blocks cannot have a heading level.")
        return self


class KnowledgeChunk(BaseModel):
    model_config = ConfigDict(frozen=True)

    chunk_id: str = Field(pattern=r"^CHUNK-[0-9a-f]{20}$")
    source_id: str = Field(min_length=1)
    ordinal: int = Field(ge=1)
    heading_path: tuple[str, ...]
    text: str = Field(min_length=1)
    first_block_ordinal: int = Field(ge=1)
    last_block_ordinal: int = Field(ge=1)
    instruction_like: bool = False


class AliasRule(BaseModel):
    model_config = ConfigDict(frozen=True)

    alias: str = Field(min_length=1)
    resolves_to_source_id: str = Field(min_length=1)
    resolution_note: str = ""


class AliasResolution(BaseModel):
    model_config = ConfigDict(frozen=True)

    query: str
    normalized_query: str
    state: ResolutionState
    source_id: str | None = None
    candidates: tuple[str, ...] = ()
    reason: str


class MethodIndexRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    method_index_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    local_method_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    source_heading: str = Field(min_length=1)
    paragraph_ordinal: int = Field(ge=1)
    extraction_confidence: float = Field(ge=0, le=1)
    canonicalisation_state: str = Field(min_length=1)


class RetrievalCase(BaseModel):
    model_config = ConfigDict(frozen=True)

    case_id: str = Field(min_length=1)
    query: str = Field(min_length=1)
    expected_source_ids: tuple[str, ...]
    expected_heading_anchors: tuple[str, ...]
    prohibited_source_ids: tuple[str, ...] = ()
    decision_use: str = Field(min_length=1)


class RetrievalEvaluation(BaseModel):
    model_config = ConfigDict(frozen=True)

    case_id: str
    passed: bool
    missing_source_ids: tuple[str, ...]
    missing_heading_anchors: tuple[str, ...]
    prohibited_source_ids_returned: tuple[str, ...]


class RightsDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str
    intended_use: IntendedUse
    allowed: bool
    reason: str
    requires_founder_confirmation: bool = False


class DomainOverlay(BaseModel):
    model_config = ConfigDict(frozen=True)

    overlay_id: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    hypothesis_additions: tuple[str, ...]
    evidence_additions: tuple[str, ...]
    method_additions: tuple[str, ...]
    metric_additions: tuple[str, ...]
    constraint_additions: tuple[str, ...]
    reviewer_additions: tuple[str, ...]
    recommended_answer: str | None = None
    preferred_option: str | None = None

    @model_validator(mode="after")
    def prevent_answer_preselection(self) -> "DomainOverlay":
        if self.recommended_answer or self.preferred_option:
            raise ValueError("Domain overlays cannot pre-decide the engagement answer.")
        return self


class KnowledgeIntelligenceBaseline(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
    source_profiles: tuple[SourceProfile, ...]
    method_index: tuple[MethodIndexRecord, ...]
    retrieval_cases: tuple[RetrievalCase, ...]
    alias_count: int = Field(ge=1)
    dependency_case_count: int = Field(ge=1)
    collision_family_count: int = Field(ge=1)
    method_record_example_count: int = Field(ge=1)
    radar_category_count: int = Field(ge=1)
    source_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    method_digest: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_unique_identity(self) -> "KnowledgeIntelligenceBaseline":
        source_ids = [item.source_id for item in self.source_profiles]
        method_ids = [item.method_index_id for item in self.method_index]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("Source profile IDs must be unique.")
        if len(method_ids) != len(set(method_ids)):
            raise ValueError("Method index IDs must be unique.")
        known = set(source_ids)
        unknown = sorted({item.source_id for item in self.method_index} - known)
        if unknown:
            raise ValueError(f"Method index contains unknown source IDs: {unknown}")
        return self


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_filename(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"[—–−]", "-", normalized)
    normalized = re.sub(r"\((?:copy|final|v?\d+)\)(?=\.[^.]+$)", "", normalized)
    stem, dot, suffix = normalized.rpartition(".")
    if dot:
        stem = re.sub(r"[\s_]+", "-", stem)
        stem = re.sub(r"-+", "-", stem).strip("-")
        suffix = re.sub(r"[^a-z0-9]+", "", suffix)
        return f"{stem}.{suffix}"
    normalized = re.sub(r"[\s_]+", "-", normalized)
    return re.sub(r"-+", "-", normalized).strip("-")


def is_instruction_like(text: str) -> bool:
    folded = unicodedata.normalize("NFKC", text).casefold()
    return any(marker in folded for marker in _INSTRUCTION_MARKERS)


def parse_markdown(text: str) -> tuple[SourceBlock, ...]:
    blocks: list[SourceBlock] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph:
            return
        value = " ".join(item.strip() for item in paragraph if item.strip()).strip()
        paragraph.clear()
        if value:
            blocks.append(
                SourceBlock(
                    ordinal=len(blocks) + 1,
                    kind=BlockKind.PARAGRAPH,
                    text=value,
                    instruction_like=is_instruction_like(value),
                )
            )

    for line in text.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            flush_paragraph()
            value = heading.group(2).strip()
            blocks.append(
                SourceBlock(
                    ordinal=len(blocks) + 1,
                    kind=BlockKind.HEADING,
                    text=value,
                    heading_level=len(heading.group(1)),
                    style_name=f"Heading {len(heading.group(1))}",
                    instruction_like=is_instruction_like(value),
                )
            )
        elif line.strip():
            paragraph.append(line.strip())
        else:
            flush_paragraph()
    flush_paragraph()
    return tuple(blocks)


def parse_docx_bytes(data: bytes) -> tuple[SourceBlock, ...]:
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
        document_xml = archive.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile) as exc:
        raise ValueError("DOCX must be a valid package containing word/document.xml.") from exc
    root = ElementTree.fromstring(document_xml)
    blocks: list[SourceBlock] = []
    namespace = {"w": _W_NS}
    for paragraph in root.findall(".//w:body/w:p", namespace):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", namespace)).strip()
        if not text:
            continue
        style_node = paragraph.find("./w:pPr/w:pStyle", namespace)
        style = ""
        if style_node is not None:
            style = style_node.attrib.get(f"{{{_W_NS}}}val", "")
        heading_level: int | None = None
        match = re.search(r"heading\s*([1-9])", style, flags=re.IGNORECASE)
        if match:
            heading_level = int(match.group(1))
        kind = BlockKind.HEADING if heading_level is not None else BlockKind.PARAGRAPH
        blocks.append(
            SourceBlock(
                ordinal=len(blocks) + 1,
                kind=kind,
                text=text,
                heading_level=heading_level,
                style_name=style,
                instruction_like=is_instruction_like(text),
            )
        )
    if not blocks:
        raise ValueError("DOCX contains no extractable paragraphs.")
    return tuple(blocks)


def stable_chunks(
    source_id: str, blocks: Iterable[SourceBlock], max_characters: int = 1600
) -> tuple[KnowledgeChunk, ...]:
    if max_characters < 200:
        raise ValueError("max_characters must be at least 200.")
    heading_stack: list[str] = []
    chunk_blocks: list[SourceBlock] = []
    chunks: list[KnowledgeChunk] = []

    def emit() -> None:
        if not chunk_blocks:
            return
        ordinal = len(chunks) + 1
        text = "\n\n".join(item.text for item in chunk_blocks)
        digest = hashlib.sha256(
            f"{source_id}|{ordinal}|{'/'.join(heading_stack)}|{text}".encode("utf-8")
        ).hexdigest()[:20]
        chunks.append(
            KnowledgeChunk(
                chunk_id=f"CHUNK-{digest}",
                source_id=source_id,
                ordinal=ordinal,
                heading_path=tuple(heading_stack),
                text=text,
                first_block_ordinal=chunk_blocks[0].ordinal,
                last_block_ordinal=chunk_blocks[-1].ordinal,
                instruction_like=any(item.instruction_like for item in chunk_blocks),
            )
        )
        chunk_blocks.clear()

    for block in blocks:
        if block.kind == BlockKind.HEADING:
            emit()
            level = block.heading_level or 1
            del heading_stack[level - 1 :]
            while len(heading_stack) < level - 1:
                heading_stack.append("")
            heading_stack.append(block.text)
            chunk_blocks.append(block)
            continue
        projected = sum(len(item.text) for item in chunk_blocks) + len(block.text)
        if chunk_blocks and projected > max_characters:
            emit()
        chunk_blocks.append(block)
    emit()
    return tuple(chunks)


def resolve_alias(
    query: str, profiles: Iterable[SourceProfile], aliases: Iterable[AliasRule]
) -> AliasResolution:
    profile_list = tuple(profiles)
    alias_list = tuple(aliases)
    normalized = normalize_filename(query)
    candidates: set[str] = set()
    for profile in profile_list:
        if query == profile.source_id:
            candidates.add(profile.source_id)
        if normalized in {
            normalize_filename(profile.original_filename),
            normalize_filename(profile.preferred_repository_filename),
        }:
            candidates.add(profile.source_id)
    for alias in alias_list:
        if normalized == normalize_filename(alias.alias):
            candidates.add(alias.resolves_to_source_id)
    ordered = tuple(sorted(candidates))
    if len(ordered) == 1:
        return AliasResolution(
            query=query,
            normalized_query=normalized,
            state=ResolutionState.RESOLVED,
            source_id=ordered[0],
            candidates=ordered,
            reason="Unique canonical source resolution.",
        )
    if len(ordered) > 1:
        return AliasResolution(
            query=query,
            normalized_query=normalized,
            state=ResolutionState.AMBIGUOUS,
            candidates=ordered,
            reason="Multiple canonical sources match; resolution requires review.",
        )
    return AliasResolution(
        query=query,
        normalized_query=normalized,
        state=ResolutionState.QUARANTINED,
        candidates=(),
        reason="No canonical source or approved alias matches the query.",
    )


def rights_decision(profile: SourceProfile, intended_use: IntendedUse) -> RightsDecision:
    if intended_use == IntendedUse.EXTERNAL_REDISTRIBUTION:
        return RightsDecision(
            source_id=profile.source_id,
            intended_use=intended_use,
            allowed=profile.external_redistribution_allowed,
            reason=(
                "External redistribution is explicitly allowed."
                if profile.external_redistribution_allowed
                else "Founder-supplied source is internal-only until rights are confirmed."
            ),
            requires_founder_confirmation=not profile.external_redistribution_allowed,
        )
    if intended_use == IntendedUse.CLIENT_PARAPHRASE:
        return RightsDecision(
            source_id=profile.source_id,
            intended_use=intended_use,
            allowed=True,
            reason="Original synthesis and paraphrase may use underlying ideas without copying protected expression.",
            requires_founder_confirmation=False,
        )
    return RightsDecision(
        source_id=profile.source_id,
        intended_use=intended_use,
        allowed=True,
        reason="Internal retrieval and controlled derivation are permitted for this project.",
        requires_founder_confirmation=False,
    )


def method_name_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    tokens = re.findall(r"[a-z0-9]+", normalized.casefold())
    return " ".join(token for token in tokens if token not in _STOP_WORDS)


def detect_duplicate_methods(
    records: Iterable[MethodIndexRecord], minimum_similarity: float = 0.72
) -> tuple[tuple[str, str, float], ...]:
    if not 0 < minimum_similarity <= 1:
        raise ValueError("minimum_similarity must be between zero and one.")
    items = tuple(records)
    result: list[tuple[str, str, float]] = []
    for left_index, left in enumerate(items):
        left_tokens = set(method_name_key(left.name).split())
        if not left_tokens:
            continue
        for right in items[left_index + 1 :]:
            if left.source_id == right.source_id:
                continue
            right_tokens = set(method_name_key(right.name).split())
            if not right_tokens:
                continue
            similarity = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
            if similarity >= minimum_similarity:
                result.append(
                    (left.method_index_id, right.method_index_id, round(similarity, 4))
                )
    return tuple(sorted(result))


def evaluate_retrieval(
    case: RetrievalCase,
    returned_source_ids: Iterable[str],
    returned_heading_anchors: Iterable[str],
) -> RetrievalEvaluation:
    sources = set(returned_source_ids)
    anchors = set(returned_heading_anchors)
    missing_sources = tuple(sorted(set(case.expected_source_ids) - sources))
    missing_anchors = tuple(sorted(set(case.expected_heading_anchors) - anchors))
    prohibited = tuple(sorted(set(case.prohibited_source_ids) & sources))
    return RetrievalEvaluation(
        case_id=case.case_id,
        passed=not missing_sources and not missing_anchors and not prohibited,
        missing_source_ids=missing_sources,
        missing_heading_anchors=missing_anchors,
        prohibited_source_ids_returned=prohibited,
    )


def apply_domain_overlay(
    base: dict[str, tuple[str, ...]], overlay: DomainOverlay
) -> dict[str, tuple[str, ...]]:
    result = dict(base)
    additions = {
        "hypotheses": overlay.hypothesis_additions,
        "evidence": overlay.evidence_additions,
        "methods": overlay.method_additions,
        "metrics": overlay.metric_additions,
        "constraints": overlay.constraint_additions,
        "reviewers": overlay.reviewer_additions,
    }
    for key, values in additions.items():
        result[key] = tuple(dict.fromkeys((*result.get(key, ()), *values)))
    return result


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected YAML object: {path}")
    return value


def load_source_profiles(path: Path) -> tuple[SourceProfile, ...]:
    raw = _load_yaml(path).get("sources")
    if not isinstance(raw, list):
        raise ValueError("Source profile seed requires a sources list.")
    return tuple(SourceProfile.model_validate(item) for item in raw)


def load_method_index(path: Path) -> tuple[MethodIndexRecord, ...]:
    raw = _load_yaml(path).get("records")
    if not isinstance(raw, list):
        raise ValueError("Domain method seed requires a records list.")
    return tuple(MethodIndexRecord.model_validate(item) for item in raw)


def load_retrieval_cases(path: Path) -> tuple[RetrievalCase, ...]:
    raw = _load_yaml(path).get("cases")
    if not isinstance(raw, list):
        raise ValueError("Retrieval evaluation file requires a cases list.")
    return tuple(RetrievalCase.model_validate(item) for item in raw)


def object_digest(value: Any) -> str:
    import json

    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_baseline(root: Path) -> KnowledgeIntelligenceBaseline:
    profiles = load_source_profiles(root / "knowledge/source-profile-seeds.yaml")
    methods = load_method_index(root / "knowledge/domain-method-headings.yaml")
    retrieval_cases = load_retrieval_cases(root / "knowledge/retrieval-evaluation.yaml")
    alias_document = _load_yaml(root / "knowledge/alias-map.yaml")
    dependency_document = _load_yaml(root / "knowledge/dependency-resolution-cases.yaml")
    collision_document = _load_yaml(root / "knowledge/method-collision-map.yaml")
    examples_document = _load_yaml(root / "knowledge/method-record-examples.yaml")
    radar_document = _load_yaml(root / "knowledge/radar-source-taxonomy.yaml")
    source_payload = [item.model_dump(mode="json") for item in profiles]
    method_payload = [item.model_dump(mode="json") for item in methods]
    return KnowledgeIntelligenceBaseline(
        version="1.0.0",
        source_profiles=profiles,
        method_index=methods,
        retrieval_cases=retrieval_cases,
        alias_count=len(alias_document.get("aliases", [])),
        dependency_case_count=len(dependency_document.get("cases", [])),
        collision_family_count=len(collision_document.get("collision_families", [])),
        method_record_example_count=len(examples_document.get("examples", [])),
        radar_category_count=len(radar_document.get("source_categories", [])),
        source_digest=object_digest(source_payload),
        method_digest=object_digest(method_payload),
    )


def serialise_baseline(baseline: KnowledgeIntelligenceBaseline) -> str:
    import json

    document = baseline.model_dump(mode="json")
    document["baseline_digest"] = object_digest(document)
    document["agent_visible"] = True
    document["original_source_files_committed"] = False
    return json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_baseline(root: Path, destination: Path) -> Path:
    destination.write_text(serialise_baseline(build_baseline(root)), encoding="utf-8")
    return destination


def verify_baseline(root: Path, destination: Path) -> None:
    expected = serialise_baseline(build_baseline(root))
    if not destination.exists() or destination.read_text(encoding="utf-8") != expected:
        raise ValueError("Committed knowledge-intelligence baseline is stale or non-reproducible.")
