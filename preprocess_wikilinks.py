#!/usr/bin/env python3
"""Preprocess wiki markdown files to convert [[wikilinks]] to proper markdown links.

Reads mkdocs.yml nav structure, builds a page-name → file-path map,
then rewrites all .md files in the wiki directory converting wikilinks.
"""

import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)


def build_page_map(nav, prefix=""):
    """Recursively extract page_name → relative_file_path from mkdocs.yml nav."""
    page_map = {}
    if not isinstance(nav, list):
        return page_map
    for item in nav:
        if isinstance(item, dict):
            for key, value in item.items():
                full_prefix = f"{prefix}/{key}" if prefix else key
                if isinstance(value, str) and value.endswith(".md"):
                    # This is a leaf node (page)
                    page_name = key.lower().replace(" ", "-")
                    page_map[page_name] = value
                elif isinstance(value, list):
                    # This is a section with subsections
                    sub_map = build_page_map(value, full_prefix)
                    page_map.update(sub_map)
        elif isinstance(item, str):
            # Simple string entry (shouldn't happen in our nav but handle it)
            pass
    return page_map


def resolve_link(link_name, source_file, page_map, wiki_root):
    """Resolve a [[wikilink]] to a relative markdown link path."""
    target = link_name.lower().strip()

    # Direct match in page map
    if target in page_map:
        target_path = page_map[target]
        return make_relative_link(source_file, target_path)

    # Try matching by filename (without .md)
    base_name = os.path.splitext(os.path.basename(target))[0].lower()
    for name, path in page_map.items():
        if name == base_name or os.path.splitext(name)[0] == base_name:
            return make_relative_link(source_file, path)

    # Try matching by partial filename match
    for name, path in page_map.items():
        if target.replace("-", "") in name.replace("-", "") or \
           name.replace("-", "") in target.replace("-", ""):
            return make_relative_link(source_file, path)

    # Fallback: try to find any file with matching name pattern
    for root, dirs, files in os.walk(wiki_root):
        for f in files:
            if f.endswith(".md") and f != "mkdocs.yml":
                fname = os.path.splitext(f)[0].lower()
                if target.replace("-", "") == fname.replace("-", ""):
                    rel = os.path.relpath(os.path.join(root, f), wiki_root)
                    return make_relative_link(source_file, rel)

    # Last resort: link to the name as-is (will be a broken link but won't crash)
    return f"[{link_name}](#{link_name})"


def make_relative_link(from_path, to_path):
    """Convert two relative paths into a proper markdown relative link."""
    from_dir = os.path.dirname(from_path)
    # Both are relative to wiki root
    full_to = os.path.join("/wiki", to_path)  # normalize
    full_from = os.path.join("/wiki", from_dir, "")

    rel = os.path.relpath(to_path, from_dir if from_dir else ".")
    return f"[{os.path.splitext(os.path.basename(rel))[0]}]({rel})"


def preprocess_file(filepath, page_map, wiki_root):
    """Process a single markdown file, converting wikilinks."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # Find all [[wikilink]] patterns (but not inside YAML frontmatter)
    def replace_wikilink(match):
        link_name = match.group(1)
        return resolve_link(link_name, filepath, page_map, wiki_root)

    # Only process lines outside of YAML frontmatter
    in_frontmatter = False
    lines = content.split("\n")
    result_lines = []

    for line in lines:
        if line.strip() == "---" and not in_frontmatter:
            in_frontmatter = True
            result_lines.append(line)
            continue
        elif line.strip() == "---" and in_frontmatter:
            in_frontmatter = False
            result_lines.append(line)
            continue

        if not in_frontmatter:
            # Replace wikilinks only outside frontmatter
            new_line = re.sub(r'\[\[([^\]]+)\]\]', replace_wikilink, line)
            result_lines.append(new_line)
        else:
            result_lines.append(line)

    content = "\n".join(result_lines)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    wiki_root = Path(__file__).parent.resolve()
    mkdocs_path = wiki_root / "mkdocs.yml"

    if not mkdocs_path.exists():
        print(f"Error: {mkdocs_path} not found")
        sys.exit(1)

    with open(mkdocs_path, "r") as f:
        config = yaml.safe_load(f)

    page_map = build_page_map(config.get("nav", []))
    print(f"Page map built: {len(page_map)} pages indexed")

    # Find all markdown files (excluding mkdocs.yml itself)
    content_dir = wiki_root / "content"
    if not content_dir.exists():
        print(f"Error: {content_dir} not found")
        sys.exit(1)

    md_files = []
    for root, dirs, files in os.walk(content_dir):
        # Skip hidden directories and the site/ output dir
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "site"]
        for f in files:
            if f.endswith(".md") and f != "mkdocs.yml":
                md_files.append(os.path.join(root, f))

    updated_count = 0
    for filepath in sorted(md_files):
        if preprocess_file(filepath, page_map, content_dir):
            rel = os.path.relpath(filepath, content_dir)
            print(f"  Updated: {rel}")
            updated_count += 1

    print(f"\nDone. {updated_count}/{len(md_files)} files updated.")


if __name__ == "__main__":
    main()
