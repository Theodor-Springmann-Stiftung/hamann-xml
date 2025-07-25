#!/usr/bin/env python3
import sys
import re
from lxml import etree

def lint_briefe(filename):
    """
    Lint briefe.xml file by:
    1. Removing all whitespace before and after page, line, letterText, opus, and document tags
    2. Inserting newlines before each of these elements
    3. Inserting newline after self-closing page tags
    4. Inserting extra newline before letterText elements
    """
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Target tags to process
    tags = ['page', 'line', 'letterText', 'opus', 'document']
    
    # Remove whitespace around target tags
    for tag in tags:
        # Remove whitespace before opening tags
        content = re.sub(r'\s*(<' + tag + r'[^>]*>)', r'\1', content)
        # Remove whitespace before closing tags
        content = re.sub(r'\s*(</' + tag + r'>)', r'\1', content)
        # Remove whitespace after opening tags (but not self-closing)
        content = re.sub(r'(<' + tag + r'[^/>]*>)\s*', r'\1', content)
        # Remove whitespace after closing tags
        content = re.sub(r'(</' + tag + r'>)\s*', r'\1', content)
        # Remove whitespace after self-closing tags
        content = re.sub(r'(<' + tag + r'[^>]*/>\s*)', lambda m: m.group(1).rstrip(), content)
    
    # Insert newlines before target elements
    for tag in tags:
        # Before opening tags (not preceded by newline)
        content = re.sub(r'([^\n])(<' + tag + r'[^>]*>)', r'\1\n\2', content)
        # Before self-closing tags (not preceded by newline)
        content = re.sub(r'([^\n])(<' + tag + r'[^>]*/>)', r'\1\n\2', content)
        # Before closing tags (not preceded by newline)
        content = re.sub(r'([^\n])(</' + tag + r'>)', r'\1\n\2', content)
    
    # Insert newline after self-closing page tags
    content = re.sub(r'(<page[^>]*/>)([^\n])', r'\1\n\2', content)
    
    # Insert extra newline before letterText elements (empty line)
    content = re.sub(r'(\n)(<letterText[^>]*>)', r'\1\n\2', content)
    
    # Write the linted content back
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Linted {filename}")

def lint_meta_or_references(filename):
    """
    Lint meta.xml or references.xml using lxml pretty print.
    Preserves comments, empty tags, and all content while formatting.
    """
    # Parse with lxml preserving comments
    parser = etree.XMLParser(strip_cdata=False, remove_blank_text=False, remove_comments=False)
    tree = etree.parse(filename, parser)
    
    # Pretty print with proper formatting
    etree.indent(tree, space="  ")
    
    # Write back to file with XML declaration
    with open(filename, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True, pretty_print=True)
    
    print(f"Linted {filename}")

def main():
    if len(sys.argv) != 3:
        print("Usage: lint.py <type> <filename>")
        print("Available types: briefe, meta, references")
        sys.exit(1)
    
    lint_type = sys.argv[1]
    filename = sys.argv[2]
    
    if lint_type == "briefe":
        lint_briefe(filename)
    elif lint_type == "meta":
        lint_meta_or_references(filename)
    elif lint_type == "references":
        lint_meta_or_references(filename)
    else:
        print(f"Unknown lint type: {lint_type}")
        print("Available types: briefe, meta, references")
        sys.exit(1)

if __name__ == "__main__":
    main()