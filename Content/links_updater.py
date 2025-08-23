#!/usr/bin/env python3
import re
from pathlib import Path
from datetime import datetime
import sys

# --- config ---
infile = Path(sys.argv[1] if len(sys.argv) > 1 else "content_index.md")
outfile = Path('outline.md')
text = infile.read_text(encoding="utf-8")

# Make backup
stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = infile.with_suffix(infile.suffix + f".bak.{stamp}")
backup.write_text(text, encoding="utf-8")

# 1) stories/*.md  -> [[scenes/<name>|<label>]]
stories_pat = re.compile(r"\[([^\]]+)\]\(stories/([^)]+?)\.md\)")
text = stories_pat.sub(r"[[scenes/\2|\1]]", text)

# 2) images/*.md   -> [[images/<name>|<label>]]
images_pat = re.compile(r"\[([^\]]+)\]\(images/([^)]+?)\.md\)")
text = images_pat.sub(r"[[images/\2|\1]]", text)

# 3) absolute .ctd pseudo-links -> [[scenes/<leaf>|<label>]]
#    Capture anything ending with "/ <leaf>" after a path containing "stories.ctd"
#    Handles spaces around slashes.
ctd_pat = re.compile(
    r"\[([^\]]+)\]\("
    r"[^)]*stories\.ctd[^)]*?"   # any path that mentions stories.ctd
    r"/\s*([^/]+?)\s*"           # final leaf after the last slash (no further '/')
    r"\)"
)
text = ctd_pat.sub(r"[[scenes/\2|\1]]", text)

# Write result
outfile.write_text(text, encoding="utf-8")

print(f"Rewrote links in {infile}")
print(f"Backup saved to {backup}")
 
