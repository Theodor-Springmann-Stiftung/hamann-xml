#!/usr/bin/env python3
"""Prepare the HKB 458–539 release without reformatting existing XML.

Reads the main and Release refs and writes only changed files
to an output directory. Pass --letters 458,500,539 for a small review sample.
"""

import argparse
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

from lxml import etree


FILES = ("Bibel-Kommentar.xml", "Register-Kommentar.xml", "forschung.xml")


def letter_number(value):
    match = re.fullmatch(r"(\d+)[a-z]?", value or "")
    return int(match.group(1)) if match else None


def source(repo: Path, revision: str, name: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), "show", f"{revision}:{name}"])


def parse(data: bytes):
    parser = etree.XMLParser(
        strip_cdata=False, remove_blank_text=False, remove_comments=False,
        resolve_entities=False,
    )
    return etree.fromstring(data, parser)


def clean_added(data: bytes) -> bytes:
    return re.sub(rb"[ \t]+(?=\r?\n)", b"", data)


def id_map(roots):
    result = {}
    for filename, root in roots.items():
        for element in root.xpath("//*[@id]"):
            key = element.get("id")
            if key in result:
                raise ValueError(f"Duplicate identifier {key}")
            result[key] = (filename, element)
    return result


def needed_definitions(notes, main_ids, release_ids):
    needed = set()
    queue = list(notes)
    while queue:
        element = queue.pop()
        for link in element.iter("link"):
            for key in (link.get("ref"), link.get("subref")):
                if not key or key in release_ids or key in needed:
                    continue
                if key not in main_ids:
                    raise ValueError(f"Reference {key} is absent from main")
                needed.add(key)
                definition = main_ids[key][1]
                queue.append(definition)
                if definition.tag == "subsection":
                    parent = definition.getparent()
                    parent_id = parent.get("id")
                    if parent_id not in release_ids and parent_id not in needed:
                        needed.add(parent_id)
                        queue.append(parent)
    return needed


def add_definitions(name, release_data, release_root, main_ids, release_ids, needed):
    lines = release_data.splitlines(keepends=True)
    insertions = defaultdict(list)
    new_parents = []
    new_subsections = defaultdict(list)
    for key in sorted(needed):
        filename, element = main_ids[key]
        if filename != name:
            continue
        if element.tag == "kommentar":
            if key not in release_ids:
                new_parents.append(element)
        elif element.tag == "subsection" and element.getparent().get("id") in release_ids:
            new_subsections[element.getparent().get("id")].append(element)

    for parent_id, subsections in new_subsections.items():
        existing = release_ids[parent_id][1]
        start = existing.sourceline - 1
        if b"<kommentar " not in lines[start] or parent_id.encode() not in lines[start]:
            raise ValueError(f"Cannot locate existing parent {parent_id}")
        close = next((i for i in range(start + 1, len(lines)) if lines[i].strip() == b"</kommentar>"), None)
        if close is None:
            raise ValueError(f"Cannot locate end of parent {parent_id}")
        for element in subsections:
            insertions[close].append(clean_added(etree.tostring(element, encoding="utf-8", with_tail=False)) + b"\n")

    if new_parents:
        categories = {e.get("value"): e for e in release_root.findall(".//kommcat")}
        for element in new_parents:
            category_name = element.getparent().get("value")
            if category_name not in categories:
                raise ValueError(f"Missing category {category_name} in {name}")
            category = categories[category_name]
            start = category.sourceline - 1
            close = next((i for i in range(start + 1, len(lines)) if lines[i].strip() == b"</kommcat>"), None)
            if close is None:
                raise ValueError(f"Cannot locate category end in {name}")
            insertions[close].append(b"\n" + clean_added(etree.tostring(element, encoding="utf-8", with_tail=False)) + b"\n")

    result = b"".join(b"".join(insertions[i]) + line for i, line in enumerate(lines))
    parse(result)
    return result, len(new_parents), sum(map(len, new_subsections.values()))


def add_marginals(release_data, main_data, notes, all_notes):
    if len(notes) == len(all_notes):
        start = main_data.index(b"Brief Nr. 458")
        end = main_data.index(b"Brief Nr. 540")
        fragment = main_data[start:end].replace(b"\r\n", b"\n")
    else:
        fragment = b"\n".join(
            etree.tostring(note, encoding="utf-8", with_tail=False) for note in notes
        )
    marker = b"</marginalien>"
    if release_data.count(marker) != 1:
        raise ValueError("Unexpected release marginal structure")
    result = release_data.replace(marker, b"\n\n" + clean_added(fragment) + b"\n" + marker)
    wrong = b'<marginal letter="512" page="376" line="36">'
    if wrong in result:
        result = result.replace(wrong, b'<marginal letter="512" page="376" line="35">')
    parse(result)
    return result


def update_renumbered_letter(repo, release_ref, main_ref, name, tag):
    """Carry the main-branch 536a -> 537a correction into this release."""
    old = source(repo, release_ref, name)
    new = source(repo, main_ref, name)
    old_root, new_root = parse(old), parse(new)
    if len(old_root.xpath(f'.//{tag}[@letter="536a"]')) != 1:
        raise ValueError(f"Expected one old 536a in {name}")
    if len(new_root.xpath(f'.//{tag}[@letter="537a"]')) != 1:
        raise ValueError(f"Expected one new 537a in {name}")
    old_pattern = re.compile(rb"<" + tag.encode() + rb' letter="536a">.*?</' + tag.encode() + rb">", re.DOTALL)
    new_pattern = re.compile(rb"<" + tag.encode() + rb' letter="537a">.*?</' + tag.encode() + rb">", re.DOTALL)
    old_matches, new_matches = list(old_pattern.finditer(old)), list(new_pattern.finditer(new))
    if len(old_matches) != 1 or len(new_matches) != 1:
        raise ValueError(f"Cannot isolate 536a/537a in {name}")
    result = old[:old_matches[0].start()] + clean_added(new_matches[0].group()) + old[old_matches[0].end():]
    if name == "meta.xml":
        result = result.replace(b'\t  \t      <letterDesc letter="537a">',
                                b'\t      <letterDesc letter="537a">')
    if name == "traditions.xml":
        result = result.replace(b'<intlink letter="536a" page="1" line="1" linktext="false">HKB 536a</intlink>',
                                b'<intlink letter="537a" page="1" line="1" linktext="false">HKB 537a</intlink>')
    parse(result)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--letters", help="Comma-separated review subset, e.g. 458,500,537,539")
    ap.add_argument("--main-ref", default="origin/main")
    ap.add_argument("--release-ref", default="origin/Release")
    args = ap.parse_args()
    repo = Path(__file__).resolve().parents[1]
    selected = set(map(int, args.letters.split(","))) if args.letters else set(range(458, 540))
    if not selected or min(selected) < 458 or max(selected) > 539:
        raise ValueError("Letters must be in 458–539")
    main_data = source(repo, args.main_ref, "Marginal-Kommentar.xml")
    release_data = source(repo, args.release_ref, "Marginal-Kommentar.xml")
    all_notes = [e for e in parse(main_data).findall(".//marginal")
                 if letter_number(e.get("letter")) is not None and 458 <= letter_number(e.get("letter")) <= 539]
    notes = [e for e in all_notes if letter_number(e.get("letter")) in selected]
    if not notes:
        raise ValueError("No selected notes")
    new_marginals = add_marginals(release_data, main_data, notes, all_notes)
    main_roots = {n: parse(source(repo, args.main_ref, n)) for n in FILES}
    release_bytes = {n: source(repo, args.release_ref, n) for n in FILES}
    release_roots = {n: parse(data) for n, data in release_bytes.items()}
    main_ids = id_map(main_roots)
    release_ids = id_map(release_roots)
    needed = needed_definitions(notes, main_ids, release_ids)
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    (output / "Marginal-Kommentar.xml").write_bytes(new_marginals)
    for name in FILES:
        data, parents, subsections = add_definitions(
            name, release_bytes[name], release_roots[name], main_ids, release_ids, needed
        )
        if data != release_bytes[name]:
            (output / name).write_bytes(data)
        print(f"{name}: {parents} new entries, {subsections} new subsections")
    settings = json.loads(source(repo, args.release_ref, "settings.json"))
    if settings["AvailableEndYear"] != 1784:
        raise ValueError("Unexpected release year setting")
    settings["AvailableEndYear"] = 1788
    settings_data = source(repo, args.release_ref, "settings.json").replace(
        b'"AvailableEndYear": 1784', b'"AvailableEndYear": 1788'
    )
    if json.loads(settings_data)["AvailableEndYear"] != 1788:
        raise ValueError("Year replacement failed")
    (output / "settings.json").write_bytes(settings_data)

    if 537 in selected:
        for name, tag in (("meta.xml", "letterDesc"), ("briefe.xml", "letterText"), ("traditions.xml", "letterTradition")):
            (output / name).write_bytes(update_renumbered_letter(repo, args.release_ref, args.main_ref, name, tag))

    result_notes = parse(new_marginals).findall(".//marginal")
    for n in result_notes:
        letter = letter_number(n.get("letter"))
        if letter is not None and letter > 539:
            raise ValueError("Released a note after HKB 539")
    result_roots = {n: parse((output / n).read_bytes()) if (output / n).exists() else release_roots[n] for n in FILES}
    result_ids = id_map(result_roots)
    for note in notes:
        for link in note.iter("link"):
            for key in (link.get("ref"), link.get("subref")):
                if key and key not in result_ids:
                    raise ValueError(f"Unresolved link {key}")
    print(f"Added {len(notes)} notes for {len(set(n.get('letter') for n in notes))} letters; {len(needed)} required identifiers")


if __name__ == "__main__":
    main()
