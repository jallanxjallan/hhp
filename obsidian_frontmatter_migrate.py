#!/home/jeremy/Python3.13Env/bin/python
"""
Transform Obsidian Markdown files per Jeremy's migration rules:
1) Delete `chapter` from frontmatter.
2) Move an [[Instructions/...]] wikilink from body into YAML field `instruction` (kept as a wikilink string).
3) Move an [[Notes/...]] wikilink from body into YAML field `note` (wikilink string).
4) Ensure `status` is the LAST key in the frontmatter block.
5) If body content is an ordered list, set `status: "💬 Prompt"`.

Fill in INPUT_DIR and OUTPUT_DIR below. Output mirrors input tree; only .md files are processed.
No external dependencies.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys
from typing import Dict, List, Tuple, Optional

# ========================= USER: SET THESE ========================= #
INPUT_DIR = Path("ContentVault/Scenes")
OUTPUT_DIR = Path("Staging")
# ================================================================== #

FM_BOUNDARY = re.compile(r"^---\s*$")
KEY_VAL = re.compile(r"^(?P<key>[A-Za-z0-9_\-]+):\s*(?P<val>.*)\s*$")
LIST_INLINE = re.compile(r"^\[(?P<body>.*)\]$")
ORDERED_LIST_FIRSTLINE = re.compile(r"^\s*\d+\.\s+")
WIKILINK_LINE = re.compile(r"^\s*\[\[(?P<target>[^\]]+)\]\]\s*$")

INSTR_PREFIX = "Instructions/"
NOTES_PREFIX = "Notes/"

class MigrationError(Exception):
    pass

def unquote(s: str) -> str:
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s

def quote_if_needed(s: str) -> str:
    if s is None:
        return '""'
    if not s:
        return '""'
    # Keep Obsidian wikilinks unquoted so Properties render them as links
    if re.match(r'^\[\[[^\]]+\]\]$', str(s)):
        return str(s)
    # Quote if whitespace or YAML/Obsidian-relevant special chars present
    if any(ch.isspace() for ch in str(s)) or any(ch in ':#[]{}' for ch in str(s)):
        s_escaped = str(s).replace('"', '\"')
        return f'"{s_escaped}"'
    return str(s)
    # Quote if whitespace or YAML/Obsidian-relevant special chars present
    if any(ch.isspace() for ch in s) or any(ch in ':#{}' for ch in s):
        s_escaped = s.replace('"', '\\"')
        return f'"{s_escaped}"'
    return s

def dump_frontmatter(data: Dict[str, object], status_last: bool = True) -> str:
    keys = list(data.keys())
    if status_last and "status" in data:
        keys = [k for k in keys if k != "status"] + ["status"]

    lines: List[str] = ["---"]
    for k in keys:
        v = data[k]
        if isinstance(v, list):
            def fmt_item(x: object) -> str:
                sx = str(x) if x is not None else ''
                # leave wikilinks as-is inside lists
                if re.match(r'^\[\[[^\]]+\]\]$', sx):
                    return sx
                return quote_if_needed(sx)
            body = ", ".join(fmt_item(x) for x in v)
            lines.append(f"{k}: [{body}]")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            sv = str(v)
            if re.match(r'^\[\[[^\]]+\]\]$', sv):
                lines.append(f"{k}: {sv}")
            else:
                lines.append(f"{k}: {quote_if_needed(sv)}")
    lines.append("---")
    return "\n".join(lines) + "\n"

def extract_links_from_body(body: str) -> Tuple[str, Optional[str], Optional[str]]:
    instruction = None
    note = None
    out_lines: List[str] = []
    for ln in body.splitlines():
        m = WIKILINK_LINE.match(ln)
        if m:
            target = m.group('target')
            if target.startswith(INSTR_PREFIX) and instruction is None:
                instruction = f"[[{target}]]"
                continue
            if target.startswith(NOTES_PREFIX) and note is None:
                note = f"[[{target}]]"
                continue
        out_lines.append(ln)
    new = "\n".join(out_lines).strip("\n") + ("\n" if out_lines else "")
    return new, instruction, note

def is_ordered_list(body: str) -> bool:
    for ln in body.splitlines():
        if not ln.strip():
            continue
        return bool(ORDERED_LIST_FIRSTLINE.match(ln))
    return False

def process_markdown(md_text: str) -> str:
    lines = md_text.splitlines()

    if not lines or not FM_BOUNDARY.match(lines[0]):
        raise MigrationError("File is missing frontmatter '---' header.")

    end_line = None
    for i in range(1, len(lines)):
        if FM_BOUNDARY.match(lines[i]):
            end_line = i
            break
    if end_line is None:
        raise MigrationError("Frontmatter block not closed with '---'.")

    fm_lines = lines[1:end_line]
    body_lines = lines[end_line + 1 :]
    data: Dict[str, object] = {}
    for ln in fm_lines:
        if not ln.strip():
            continue
        m = KEY_VAL.match(ln)
        if not m:
            raise MigrationError(f"Unrecognized frontmatter line: {ln!r}")
        k, v = m.group('key'), m.group('val').strip()
        if v.lower() == "null":
            data[k] = None
        elif v in ("[]", "[ ]"):
            data[k] = []
        elif LIST_INLINE.match(v):
            inner = LIST_INLINE.match(v).group('body').strip()
            parts = [p.strip() for p in inner.split(',')] if inner else []
            data[k] = [unquote(p) for p in parts if p]
        else:
            data[k] = unquote(v)

    # Normalize pre-existing instruction/note fields: convert plain paths to wikilinks
    for key in ("instruction", "note"):
        val = data.get(key)
        if isinstance(val, str) and val:
            if not re.match(r'^\[\[[^\]]+\]\]$', val):
                if val.startswith(INSTR_PREFIX) or val.startswith(NOTES_PREFIX):
                    data[key] = f"[[{val}]]"

    if 'chapter' in data:
        data.pop('chapter', None)

    body = "\n".join(body_lines)

    body, instr, note = extract_links_from_body(body)
    if instr is not None:
        data['instruction'] = instr
    if note is not None:
        data['note'] = note

    if is_ordered_list(body):
        data['status'] = "💬 Prompt"

    new_fm = dump_frontmatter(data, status_last=True)

    new_text = new_fm + body.lstrip('\n')
    return new_text

def process_file(src: Path, dst: Path) -> None:
    text = src.read_text(encoding='utf-8')
    new = process_markdown(text)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(new, encoding='utf-8')

def main() -> int:
    if not INPUT_DIR or not OUTPUT_DIR:
        print("ERROR: Set INPUT_DIR and OUTPUT_DIR at top of script.", file=sys.stderr)
        return 2
    if not INPUT_DIR.exists() or not INPUT_DIR.is_dir():
        print(f"ERROR: INPUT_DIR not found: {INPUT_DIR}", file=sys.stderr)
        return 2
    count = 0
    errors: List[str] = []
    for p in INPUT_DIR.rglob("*.md"):
        rel = p.relative_to(INPUT_DIR)
        outp = OUTPUT_DIR / rel
        try:
            process_file(p, outp)
            count += 1
        except Exception as e:
            errors.append(f"{rel}: {e}")
    print(f"Processed {count} Markdown files into {OUTPUT_DIR}")
    if errors:
        print("\nFailures:", file=sys.stderr)
        for msg in errors:
            print(" - ", msg, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
