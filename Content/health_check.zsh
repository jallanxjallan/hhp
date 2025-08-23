# Run from the vault root or adjust GLOB as needed
GLOBIGNORE='**/.obsidian/**'
print -n ""  # force zsh to load
autoload -Uz colors && colors

bad=0
for f in **/*.md(.N); do
  # detect UTF-8 BOM
  bom=$([[ $(xxd -p -l3 -- "$f") == "efbbbf" ]] && print "BOM" || print "-")
  # first non-empty line
  first_nonempty=$(awk 'NF{print; exit}' "$f")
  # opening fence present at very top?
  top_ok=$([[ "$first_nonempty" == '---' ]] && print "OK" || print "BAD")
  # closing fence present before first blank line after opening?
  close_ok=$(awk '
    BEGIN{open=0}
    NR==1 && $0=="---"{open=1; next}
    open==1 && $0=="---"{print "OK"; exit}
    END{if(open==1) print "MISSING"}' "$f")
  [[ -z "$close_ok" ]] && close_ok="-"  # no opener at top
  # windows line endings?
  crlf=$(( $(file -b "$f" | grep -c CRLF) )) && [[ $crlf -gt 0 ]] && crlf="CRLF" || crlf="-"
  # bad fence characters in first two lines?
  fence_chars=$(head -n2 "$f" | tr -d '-' | grep -q '—' && print "EMDASH" || print "-")

  if [[ "$bom" != "-" || "$top_ok" != "OK" || "$close_ok" == "MISSING" || "$crlf" != "-" || "$fence_chars" != "-" ]]; then
    ((bad++))
    print -P "%F{red}!%f $f  [BOM:$bom TOP:$top_ok CLOSE:$close_ok CRLF:$crlf EMDASH:$fence_chars]"
  fi
done

if (( bad == 0 )); then
  print -P "%F{green}✓ All Markdown files look frontmatter-healthy.%f"
else
  print -P "%F{yellow}$bad file(s) need attention (see above).%f"
fi

