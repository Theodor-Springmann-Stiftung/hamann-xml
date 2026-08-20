from __future__ import annotations

import difflib
import json
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from lxml import etree


MARKUP_RE = re.compile(
    r"<!--.*?-->|<!\[CDATA\[.*?\]\]>|<\?.*?\?>|<![^>]*>|<[^>]+>", re.DOTALL
)
TAG_RE = re.compile(r"</?\s*([A-Za-z_][\w:.-]*)")
ATTR_RE = re.compile(r"([A-Za-z_][\w:.-]*)\s*=\s*(['\"])(.*?)\2", re.DOTALL)
ENTITY_RE = re.compile(r"&(?:#x[0-9A-Fa-f]+|#\d+|amp|lt|gt|apos|quot);")
WORD_RE = re.compile(r"\w+(?:[’'-]\w+)*|[^\w\s]+", re.UNICODE)


class Normalizer(Protocol):
    def normalize_many(self, texts: Sequence[str]) -> list[str]: ...


@dataclass
class Token:
    raw: str
    is_markup: bool


@dataclass(frozen=True)
class Atom:
    char: str
    raw: str
    token_index: int


@dataclass
class Segment:
    letter: str
    line: dict[str, str]
    part: int
    token_indexes: list[int] = field(default_factory=list)
    atoms: list[Atom] = field(default_factory=list)
    source: str = ""
    core_start: int = 0
    core_end: int = 0


def _parse_attrs(markup: str) -> dict[str, str]:
    return {match.group(1): match.group(3) for match in ATTR_RE.finditer(markup)}


def _tag_name(markup: str) -> str | None:
    match = TAG_RE.match(markup)
    return match.group(1) if match else None


def _tokenize(raw: str) -> list[Token]:
    tokens: list[Token] = []
    position = 0
    for match in MARKUP_RE.finditer(raw):
        if match.start() > position:
            tokens.append(Token(raw[position : match.start()], False))
        tokens.append(Token(match.group(), True))
        position = match.end()
    if position < len(raw):
        tokens.append(Token(raw[position:], False))
    return tokens


def _decode_entity(entity: str) -> str:
    if entity.startswith("&#x"):
        return chr(int(entity[3:-1], 16))
    if entity.startswith("&#"):
        return chr(int(entity[2:-1]))
    return {
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&apos;": "'",
        "&quot;": '"',
    }[entity]


def _atoms(raw: str, token_index: int) -> list[Atom]:
    atoms: list[Atom] = []
    position = 0
    for match in ENTITY_RE.finditer(raw):
        for char in raw[position : match.start()]:
            atoms.append(Atom(char, char, token_index))
        entity = match.group()
        atoms.append(Atom(_decode_entity(entity), entity, token_index))
        position = match.end()
    for char in raw[position:]:
        atoms.append(Atom(char, char, token_index))
    return atoms


def _escape_generated(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _is_opening_tag(markup: str) -> bool:
    return markup.startswith("<") and not markup.startswith(("</", "<!", "<?")) and not markup.rstrip().endswith("/>")


def _is_closing_tag(markup: str) -> bool:
    return markup.startswith("</")


def _validated_letter_ids(raw: bytes) -> set[str]:
    parser = etree.XMLParser(
        strip_cdata=False,
        remove_blank_text=False,
        remove_comments=False,
        resolve_entities=False,
        huge_tree=True,
    )
    root = etree.fromstring(raw, parser)
    return {
        value
        for value in root.xpath("//letterText/@letter")
        if isinstance(value, str)
    }


def _collect_segments(
    tokens: list[Token],
    selected_letters: set[str],
    excluded_tags: set[str],
) -> list[Segment]:
    segments: list[Segment] = []
    active_letter: str | None = None
    current_line: dict[str, str] = {}
    current_indexes: list[int] = []
    excluded_depth = 0
    part = 1

    def flush() -> None:
        nonlocal current_indexes, part
        if active_letter is not None and current_indexes:
            atoms = [atom for index in current_indexes for atom in _atoms(tokens[index].raw, index)]
            chars = "".join(atom.char for atom in atoms)
            start = 0
            while start < len(chars) and chars[start].isspace():
                start += 1
            end = len(chars)
            while end > start and chars[end - 1].isspace():
                end -= 1
            if start < end:
                segments.append(
                    Segment(
                        letter=active_letter,
                        line=current_line.copy(),
                        part=part,
                        token_indexes=current_indexes.copy(),
                        atoms=atoms,
                        source=chars[start:end],
                        core_start=start,
                        core_end=end,
                    )
                )
                part += 1
        current_indexes = []

    for index, token in enumerate(tokens):
        if not token.is_markup:
            if active_letter is not None and excluded_depth == 0:
                current_indexes.append(index)
            continue

        name = _tag_name(token.raw)
        if name == "letterText" and _is_opening_tag(token.raw):
            flush()
            letter = _parse_attrs(token.raw).get("letter")
            active_letter = letter if letter in selected_letters else None
            current_line = {}
            part = 1
            continue
        if name == "letterText" and _is_closing_tag(token.raw):
            flush()
            active_letter = None
            current_line = {}
            continue
        if active_letter is None or name is None:
            continue
        if name == "line" and not _is_closing_tag(token.raw):
            flush()
            current_line = _parse_attrs(token.raw)
            part = 1
            continue
        if name in excluded_tags:
            if _is_opening_tag(token.raw):
                flush()
                excluded_depth += 1
            elif _is_closing_tag(token.raw):
                excluded_depth -= 1
                current_indexes = []
            else:
                flush()
                current_indexes = []

    flush()
    return segments


def _word_alignment(source: str, target: str) -> list[dict[str, object]]:
    source_words = WORD_RE.findall(source)
    target_words = WORD_RE.findall(target)
    matcher = difflib.SequenceMatcher(a=source_words, b=target_words, autojunk=False)
    return [
        {
            "operation": operation,
            "source": source_words[source_start:source_end],
            "output": target_words[target_start:target_end],
        }
        for operation, source_start, source_end, target_start, target_end in matcher.get_opcodes()
    ]


def _project_segment(
    tokens: list[Token], segment: Segment, normalized: str
) -> tuple[int, list[dict[str, object]]]:
    core_atoms = segment.atoms[segment.core_start : segment.core_end]
    source = segment.source
    matcher = difflib.SequenceMatcher(a=source, b=normalized, autojunk=False)
    generated: dict[int, list[str]] = {index: [] for index in segment.token_indexes}
    ambiguous = 0

    for operation, source_start, source_end, target_start, target_end in matcher.get_opcodes():
        target_text = normalized[target_start:target_end]
        if operation == "equal":
            for atom in core_atoms[source_start:source_end]:
                generated[atom.token_index].append(atom.raw)
            continue
        if operation == "insert":
            if source_start < len(core_atoms):
                token_index = core_atoms[source_start].token_index
            else:
                token_index = core_atoms[-1].token_index
            generated[token_index].append(_escape_generated(target_text))
            continue
        if operation == "delete":
            continue

        source_atoms = core_atoms[source_start:source_end]
        runs: list[tuple[int, int]] = []
        for atom in source_atoms:
            if runs and runs[-1][0] == atom.token_index:
                token_index, length = runs[-1]
                runs[-1] = (token_index, length + 1)
            else:
                runs.append((atom.token_index, 1))
        if len(runs) > 1:
            ambiguous += 1
        source_total = sum(length for _, length in runs)
        consumed_source = 0
        consumed_target = 0
        for run_index, (token_index, length) in enumerate(runs):
            consumed_source += length
            if run_index == len(runs) - 1:
                next_target = len(target_text)
            else:
                next_target = round(consumed_source * len(target_text) / source_total)
            generated[token_index].append(
                _escape_generated(target_text[consumed_target:next_target])
            )
            consumed_target = next_target

    atom_positions: dict[int, list[tuple[int, Atom]]] = {}
    for position, atom in enumerate(segment.atoms):
        atom_positions.setdefault(atom.token_index, []).append((position, atom))
    for token_index in segment.token_indexes:
        prefix = "".join(
            atom.raw
            for position, atom in atom_positions[token_index]
            if position < segment.core_start
        )
        suffix = "".join(
            atom.raw
            for position, atom in atom_positions[token_index]
            if position >= segment.core_end
        )
        tokens[token_index].raw = prefix + "".join(generated[token_index]) + suffix

    return ambiguous, _word_alignment(source, normalized)


def transform_xml(
    source_path: Path,
    output_path: Path,
    normalizer: Normalizer,
    report_path: Path | None = None,
    letters: set[str] | None = None,
    excluded_tags: set[str] | None = None,
) -> dict[str, int]:
    raw_bytes = source_path.read_bytes()
    available_letters = _validated_letter_ids(raw_bytes)
    selected_letters = letters or available_letters
    unknown_letters = selected_letters - available_letters
    if unknown_letters:
        raise ValueError(f"Unknown letter IDs: {', '.join(sorted(unknown_letters))}")

    encoding_match = re.search(br"<\?xml[^>]*encoding=['\"]([^'\"]+)", raw_bytes[:200])
    encoding = encoding_match.group(1).decode("ascii") if encoding_match else "utf-8"
    raw = raw_bytes.decode(encoding)
    tokens = _tokenize(raw)
    segments = _collect_segments(tokens, selected_letters, excluded_tags or {"nr", "gr", "hb"})
    normalized_texts = normalizer.normalize_many([segment.source for segment in segments])
    if len(normalized_texts) != len(segments):
        raise ValueError("Normalizer returned a different number of segments")

    report_records: list[dict[str, object]] = []
    changed = 0
    ambiguous_total = 0
    for segment, normalized in zip(segments, normalized_texts, strict=True):
        ambiguous, word_alignment = _project_segment(tokens, segment, normalized)
        was_changed = segment.source != normalized
        changed += int(was_changed)
        ambiguous_total += ambiguous
        report_records.append(
            {
                "letter": segment.letter,
                "line": segment.line,
                "part": segment.part,
                "source": segment.source,
                "output": normalized,
                "changed": was_changed,
                "ambiguous_markup_spans": ambiguous,
                "word_alignment": word_alignment,
            }
        )

    output = "".join(token.raw for token in tokens).encode(encoding)
    _validated_letter_ids(output)
    output_path.write_bytes(output)

    if report_path is not None:
        with report_path.open("w", encoding="utf-8") as report:
            for record in report_records:
                report.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "letters": len(selected_letters),
        "segments": len(segments),
        "changed_segments": changed,
        "ambiguous_markup_spans": ambiguous_total,
    }
