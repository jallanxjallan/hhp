#!/bin/zsh
for f in notes/*.md; do
  # only proceed if the file has YAML frontmatter
  if grep -q "^---" "$f"; then
    # check if field already exists
    if ! grep -q "^last-updated:" "$f"; then
      # insert before the closing '---' of frontmatter
      today=$(date +%Y-%m-%d)
      awk -v today="$today" '
        BEGIN {frontmatter=0}
        /^---$/ {
          if (frontmatter==1) {
            print "last-updated: " today
          }
          frontmatter++
        }
        {print}
      ' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
      echo "Added last-updated to $f"
    else
      echo "Skipped $f (already has last-updated)"
    fi
  else
    echo "Skipped $f (no frontmatter)"
  fi
done

