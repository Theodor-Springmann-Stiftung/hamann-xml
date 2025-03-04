#!/usr/bin/env python3

"""
Single integrated validator script with structured error handling (GitHub Actions annotations),
plus checks for:
 1) Cross-references (sender/receiver/location) in meta.xml
 2) page/line merges from briefe.xml & traditions.xml for letter=, page=, line=
 3) <intlink> references
 4) <kommentar id="..."> & <subsection id="..."> in registers (must have <lemma>)
 5) IDs must be unique among all kommentars or all subsections across registers
 6) <link ref="..." subref="..."> must match a valid kommentar/subsection ID
"""

import sys
import argparse
import re
from collections import defaultdict

from lxml import etree

##############################################################################
# Basic parse / line info
##############################################################################

def parse_xml(file_path):
    """
    Parse XML using lxml.etree (keeping line numbers).
    Exit on syntax/file errors.
    """
    try:
        parser = etree.XMLParser(remove_blank_text=False)
        return etree.parse(file_path, parser)
    except etree.XMLSyntaxError as e:
        print(f"Error parsing {file_path}: {e}")
        sys.exit(1)
    except OSError:
        print(f"Error: File not found - {file_path}")
        sys.exit(1)

def get_line_number(elem):
    """
    Return the sourceline of an lxml element, or 'Unknown'.
    """
    return elem.sourceline if hasattr(elem, 'sourceline') and elem.sourceline else "Unknown"

##############################################################################
# Merging letter/page/line from briefe.xml + traditions.xml
##############################################################################

def build_letter_page_line_map_brief(doc_root):
    """
    letter_pages[letter][page] = set(line)

    We allow <page> to continue across <letterText> transitions unless
    a new <page> is encountered.
    """
    letter_pages = defaultdict(lambda: defaultdict(set))

    doc_elem = doc_root.find(".//document")
    if doc_elem is None:
        doc_elem = doc_root

    current_letter = None
    current_page = None

    for elem in doc_elem.iter():
        tag = elem.tag
        if tag == 'letterText':
            current_letter = elem.get('letter')
        elif tag == 'page':
            page_index = elem.get('index')
            if page_index:
                current_page = page_index
        elif tag == 'line':
            line_index = elem.get('index')
            if current_letter and current_page and line_index:
                letter_pages[current_letter][current_page].add(line_index)

    return letter_pages

def build_letter_page_line_map_trad(trad_root):
    """
    Similarly for traditions.xml, reading <letterTradition letter="...">
    to find any <page> and <line>. We'll unify them with briefe.xml data.
    """
    letter_pages = defaultdict(lambda: defaultdict(set))

    for letter_trad in trad_root.findall(".//letterTradition"):
        letter_id = letter_trad.get('letter')
        if not letter_id:
            continue
        current_page = None

        for elem in letter_trad.iter():
            if elem is letter_trad:
                continue
            if elem.tag == 'page':
                pidx = elem.get('index')
                if pidx:
                    current_page = pidx
            elif elem.tag == 'line':
                lidx = elem.get('index')
                if current_page and lidx:
                    letter_pages[letter_id][current_page].add(lidx)

    return letter_pages

def merge_page_line_maps(map_a, map_b):
    """
    Merge two letter->page->lines maps (map_b into map_a).
    """
    for letter_id, pages_dict in map_b.items():
        for page_id, line_set in pages_dict.items():
            map_a[letter_id][page_id].update(line_set)
    return map_a

##############################################################################
# <intlink> check
##############################################################################

def validate_intlinks(xml_root, file_path, letter_pages, letter_refs, errors):
    """
    For each <intlink letter=... page=... line=.../>:
      - letter is mandatory, must be in letter_refs
      - if page is present => must exist in letter_pages
      - if line is present => must also have that page
      - line w/o page => error
    """
    for intlink in xml_root.findall(".//intlink"):
        line_no = get_line_number(intlink)
        letter_id = intlink.get('letter')
        page_id   = intlink.get('page')
        line_id   = intlink.get('line')

        if not letter_id or letter_id not in letter_refs:
            errors.append({
                "file": file_path,
                "line": line_no,
                "message": f"Invalid intlink letter={letter_id}"
            })
            continue

        if letter_id not in letter_pages:
            errors.append({
                "file": file_path,
                "line": line_no,
                "message": f"No pages known for letter={letter_id} in intlink"
            })
            continue

        if page_id:
            if page_id not in letter_pages[letter_id]:
                errors.append({
                    "file": file_path,
                    "line": line_no,
                    "message": f"Invalid page={page_id} for letter={letter_id} in intlink"
                })
            else:
                if line_id:
                    if line_id not in letter_pages[letter_id][page_id]:
                        errors.append({
                            "file": file_path,
                            "line": line_no,
                            "message": f"Invalid line={line_id} for letter={letter_id}, page={page_id} in intlink"
                        })
        else:
            # no page
            if line_id:
                errors.append({
                    "file": file_path,
                    "line": line_no,
                    "message": f"intlink has line={line_id} but no page=? for letter={letter_id}"
                })

##############################################################################
# <kommentar> and <subsection> check
##############################################################################

def gather_commentaries_and_subsections(xml_root, file_path, errors,
                                        global_kommentar_ids, global_subsection_ids):
    """
    For each <kommentar id="XYZ"> => must have <lemma>. ID must be globally unique among kommentars.
    For each <subsection id="ABC"> => must have <lemma>. ID must be globally unique among subsections.
    """
    local_komm_ids = set()
    local_sub_ids  = set()

    # <kommentar id="...">
    for kom in xml_root.findall(".//kommentar"):
        kid = kom.get('id')
        ln  = get_line_number(kom)
        if not kid:
            errors.append({
                "file": file_path,
                "line": ln,
                "message": "<kommentar> missing @id"
            })
            continue

        # check local duplicates
        if kid in local_komm_ids:
            errors.append({
                "file": file_path,
                "line": ln,
                "message": f"Duplicate <kommentar id='{kid}'> in this file"
            })
        else:
            local_komm_ids.add(kid)

        # check global duplicates
        if kid in global_kommentar_ids:
            errors.append({
                "file": file_path,
                "line": ln,
                "message": f"Duplicate <kommentar id='{kid}'> across multiple registers"
            })
        else:
            global_kommentar_ids.add(kid)

        # must have a <lemma> child
        lemma_elem = kom.find(".//lemma")
        if lemma_elem is None:
            errors.append({
                "file": file_path,
                "line": ln,
                "message": f"<kommentar id='{kid}'> missing <lemma> child"
            })

    # <subsection id="...">
    for sub in xml_root.findall(".//subsection"):
        sid = sub.get('id')
        ln  = get_line_number(sub)
        if not sid:
            errors.append({
                "file": file_path,
                "line": ln,
                "message": "<subsection> missing @id"
            })
            continue

        # local duplicates
        if sid in local_sub_ids:
            errors.append({
                "file": file_path,
                "line": ln,
                "message": f"Duplicate <subsection id='{sid}'> in this file"
            })
        else:
            local_sub_ids.add(sid)

        # global duplicates
        if sid in global_subsection_ids:
            errors.append({
                "file": file_path,
                "line": ln,
                "message": f"Duplicate <subsection id='{sid}'> across multiple registers"
            })
        else:
            global_subsection_ids.add(sid)

        # must have <lemma>
        lemma_elem = sub.find(".//lemma")
        if lemma_elem is None:
            errors.append({
                "file": file_path,
                "line": ln,
                "message": f"<subsection id='{sid}'> missing <lemma> child"
            })

##############################################################################
# <link ref="..." subref="..."> check
##############################################################################

def validate_links_for_commentary(xml_root, file_path,
                                  kommentar_ids, subsection_ids,
                                  errors):
    """
    For each <link ref="X" subref="Y">:
      - if ref="X" => X must be in kommentars OR subsections
      - if subref="Y" => Y must be in subsections
    """
    for link_elem in xml_root.findall(".//link"):
        ln = get_line_number(link_elem)
        refval    = link_elem.get('ref')
        subrefval = link_elem.get('subref')

        # check ref
        if refval:
            if refval not in kommentar_ids and refval not in subsection_ids:
                errors.append({
                    "file": file_path,
                    "line": ln,
                    "message": f"Invalid <link ref='{refval}'> (not in komentar/subsection IDs)"
                })
        # check subref
        if subrefval:
            if subrefval not in subsection_ids:
                errors.append({
                    "file": file_path,
                    "line": ln,
                    "message": f"Invalid <link subref='{subrefval}'> (not in <subsection> IDs)"
                })

##############################################################################
# The Main Validator
##############################################################################

def validate_references(meta_file, references_file, briefe_file,
                        edits_file, traditions_file, marginalien_file,
                        extra_registers=None):
    """All checks in one place."""

    # 1) Parse main files
    meta_tree       = parse_xml(meta_file)
    references_tree = parse_xml(references_file)
    briefe_tree     = parse_xml(briefe_file)
    edits_tree      = parse_xml(edits_file)
    traditions_tree = parse_xml(traditions_file)
    marginal_tree   = parse_xml(marginalien_file)

    # parse optional register files
    register_trees = []
    if extra_registers:
        for rfile in extra_registers:
            rtree = parse_xml(rfile)
            register_trees.append((rfile, rtree))

    # 2) Get roots
    meta_xml        = meta_tree.getroot()
    references_xml  = references_tree.getroot()
    briefe_xml      = briefe_tree.getroot()
    edits_xml       = edits_tree.getroot()
    traditions_xml  = traditions_tree.getroot()
    marginalien_xml = marginal_tree.getroot()

    # 3) Reference sets from references.xml + edits.xml + meta.xml
    person_refs   = {p.get('index') for p in references_xml.findall(".//personDef")}
    location_refs = {l.get('index') for l in references_xml.findall(".//locationDef")}
    hand_refs     = {h.get('index') for h in references_xml.findall(".//handDef")}
    app_refs      = {a.get('index') for a in references_xml.findall(".//appDef")}
    edit_refs     = {e.get('index') for e in edits_xml.findall(".//editreason")}
    letter_refs   = {desc.get('letter') for desc in meta_xml.findall(".//letterDesc")}

    # We'll accumulate all errors as a list of dict: {file, line, message}
    errors = []

    # 4) Gather all <kommentar> and <subsection> IDs from each register
    #    to check their uniqueness and presence of <lemma>.
    global_kommentar_ids  = set()
    global_subsection_ids = set()

    for (rfile, rtree) in register_trees:
        rroot = rtree.getroot()
        gather_commentaries_and_subsections(
            rroot, rfile, errors,
            global_kommentar_ids, global_subsection_ids
        )

    # (If references.xml or traditions.xml also contain <kommentar> or <subsection>,
    #  call gather_commentaries_and_subsections on them similarly.)

    # 5) Validate meta.xml references
    for letter in meta_xml.findall(".//letterDesc"):
        letter_id = letter.get('letter')
        ln = get_line_number(letter)

        # <sender ref="...">
        for sender in letter.findall(".//sender"):
            ref = sender.get('ref')
            if ref and ref not in person_refs:
                errors.append({
                    "file": meta_file,
                    "line": get_line_number(sender),
                    "message": f"Invalid sender ref: {ref} in letter={letter_id}"
                })

        # <receiver ref="...">
        for receiver in letter.findall(".//receiver"):
            ref = receiver.get('ref')
            if ref and ref not in person_refs:
                errors.append({
                    "file": meta_file,
                    "line": get_line_number(receiver),
                    "message": f"Invalid receiver ref: {ref} in letter={letter_id}"
                })

        # <location ref="...">
        loc_elem = letter.find(".//location")
        if loc_elem is not None:
            r = loc_elem.get('ref')
            if r and r not in location_refs:
                errors.append({
                    "file": meta_file,
                    "line": get_line_number(loc_elem),
                    "message": f"Invalid location ref: {r} in letter={letter_id}"
                })

    # 6) Validate briefe.xml references
    for letter_text in briefe_xml.findall(".//letterText"):
        letter_id = letter_text.get('letter')
        ln = get_line_number(letter_text)

        if letter_id and letter_id not in letter_refs:
            errors.append({
                "file": briefe_file,
                "line": ln,
                "message": f"Invalid letter reference: {letter_id} in briefe.xml"
            })

        for hand_elem in letter_text.findall(".//hand"):
            ref = hand_elem.get('ref')
            if ref and ref not in hand_refs:
                errors.append({
                    "file": briefe_file,
                    "line": get_line_number(hand_elem),
                    "message": f"Invalid hand ref: {ref} in letter {letter_id}"
                })

        for edit_elem in letter_text.findall(".//edit"):
            ref = edit_elem.get('ref')
            if ref and ref not in edit_refs:
                errors.append({
                    "file": briefe_file,
                    "line": get_line_number(edit_elem),
                    "message": f"Invalid edit ref: {ref} in letter {letter_id}"
                })

    # 7) Validate traditions.xml references (besides page/line)
    for tradition in traditions_xml.findall(".//letterTradition"):
        letter_id = tradition.get('letter')
        ln = get_line_number(tradition)
        if letter_id and letter_id not in letter_refs:
            errors.append({
                "file": traditions_file,
                "line": ln,
                "message": f"Invalid letterTradition reference: {letter_id}"
            })

        # <app ref="...">
        for app_elem in tradition.findall(".//app"):
            ref = app_elem.get('ref')
            if ref and ref not in app_refs:
                errors.append({
                    "file": traditions_file,
                    "line": get_line_number(app_elem),
                    "message": f"Invalid app ref: {ref} in letterTradition {letter_id}"
                })

        # <hand ref="...">
        for hand_elem in tradition.findall(".//hand"):
            ref = hand_elem.get('ref')
            if ref and ref not in hand_refs:
                errors.append({
                    "file": traditions_file,
                    "line": get_line_number(hand_elem),
                    "message": f"Invalid hand ref: {ref} in letterTradition {letter_id}"
                })

    # 8) Merge letter->page->lines from briefe.xml & traditions.xml
    letter_pages_brief = build_letter_page_line_map_brief(briefe_xml)
    letter_pages_trad  = build_letter_page_line_map_trad(traditions_xml)
    letter_pages       = merge_page_line_maps(letter_pages_brief, letter_pages_trad)

    # 9) Validate <intlink> in traditions.xml, marginalien.xml, and all registers
    validate_intlinks(traditions_xml, traditions_file, letter_pages, letter_refs, errors)
    validate_intlinks(marginalien_xml, marginalien_file, letter_pages, letter_refs, errors)
    for (rfile, rtree) in register_trees:
        rroot = rtree.getroot()
        validate_intlinks(rroot, rfile, letter_pages, letter_refs, errors)

    # 10) <marginal letter="..." page="..." line="..."> in Marginal-Kommentar.xml
    for marginal_elem in marginalien_xml.findall(".//marginal"):
        letter_id = marginal_elem.get('letter')
        page_id   = marginal_elem.get('page')
        line_id   = marginal_elem.get('line')
        ln        = get_line_number(marginal_elem)

        if letter_id not in letter_refs:
            errors.append({
                "file": marginalien_file,
                "line": ln,
                "message": f"Invalid marginal letter reference: {letter_id} (not in meta.xml)"
            })
        else:
            if letter_id not in letter_pages:
                errors.append({
                    "file": marginalien_file,
                    "line": ln,
                    "message": f"No pages/lines known for letter={letter_id} in briefe/traditions"
                })
            else:
                if page_id not in letter_pages[letter_id]:
                    errors.append({
                        "file": marginalien_file,
                        "line": ln,
                        "message": f"Invalid page reference: letter={letter_id}, page={page_id}"
                    })
                else:
                    if line_id not in letter_pages[letter_id][page_id]:
                        errors.append({
                            "file": marginalien_file,
                            "line": ln,
                            "message": f"Invalid line reference: letter={letter_id}, page={page_id}, line={line_id}"
                        })

    # 11) Now validate all <link ref="..." subref="..."> across every file for commentary IDs
    #     We'll define two sets that might have come from gather_commentaries_and_subsections:
    #     global_kommentar_ids, global_subsection_ids
    def validate_links_in_tree(root, path):
        validate_links_for_commentary(root, path, global_kommentar_ids, global_subsection_ids, errors)

    # meta.xml
    validate_links_in_tree(meta_xml, meta_file)
    # references.xml
    validate_links_in_tree(references_xml, references_file)
    # briefe.xml
    validate_links_in_tree(briefe_xml, briefe_file)
    # edits.xml
    validate_links_in_tree(edits_xml, edits_file)
    # traditions.xml
    validate_links_in_tree(traditions_xml, traditions_file)
    # marginalien.xml
    validate_links_in_tree(marginalien_xml, marginalien_file)
    # registers
    for (rfile, rtree) in register_trees:
        validate_links_in_tree(rtree.getroot(), rfile)

    ############################################################################
    # Final: Print errors or success
    ############################################################################
    if errors:
        # Print them in GitHub annotation format: ::error file=...,line=...::{message}
        for err in errors:
            file_name = err["file"]
            line_no   = err["line"]
            message   = err["message"]
            print(f"::error file={file_name},line={line_no}::{message}")
        sys.exit(1)
    else:
        print("All references are valid.")

##############################################################################
# Entry Point
##############################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
Validates cross-references among multiple XML files, merges page/line from briefe.xml & traditions.xml,
handles <intlink>, plus checks <kommentar>/<subsection> with unique IDs and <lemma>, and <link ref/subref> to these IDs.
Produces GitHub Actions annotation errors.
""")

    parser.add_argument("meta_file", help="Path to meta.xml")
    parser.add_argument("references_file", help="Path to references.xml")
    parser.add_argument("briefe_file", help="Path to briefe.xml")
    parser.add_argument("edits_file", help="Path to edits.xml")
    parser.add_argument("traditions_file", help="Path to traditions.xml")
    parser.add_argument("marginalien_file", help="Path to Marginal-Kommentar.xml")
    parser.add_argument(
        "--register",
        dest="registers",
        nargs="*",
        default=None,
        help="One or more register.xml files, containing <kommentar>/<subsection> plus possible <link> or <intlink>."
    )

    args = parser.parse_args()

    validate_references(
        args.meta_file,
        args.references_file,
        args.briefe_file,
        args.edits_file,
        args.traditions_file,
        args.marginalien_file,
        extra_registers=args.registers
    )
