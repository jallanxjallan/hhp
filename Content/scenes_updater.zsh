#!/bin/zsh
f#!/bin/zsh
for f in Scenes/*.md; do
  # only proceed if the file has YAML frontmatter
  if grep -q "^---" "$f"; then
    # check if field already exists
    if ! grep -q "^last-checked:" "$f"; then
      today=$(date +%Y-%m-%d)
      awk -v today="$today" '
        BEGIN {frontmatter=0}
        /^---$/ {
          if (frontmatter==1) {
            print "last-checked: " today
          }
          frontmatter++
        }
        {print}
      ' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
      echo "Added last-checked to $f"
    else
      echo "Skipped $f (already has last-checked)"
    fi
  else
    echo "Skipped $f (no frontmatter)"
  fi
done

