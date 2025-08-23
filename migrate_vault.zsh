rsync -a --delete --exclude='.obsidian' --exclude='.git' ContentVault/ Content/ && \
find Content -type f -name '*.md' -print0 | \
xargs -0 perl -0777 -pi -e '
  # Edit only the first YAML frontmatter block
  s{
    \A(---\s*\n)          # $1 start of frontmatter
    (.*?)                 # $2 body (non-greedy)
    (\n---\s*\n?)         # $3 end of frontmatter
  }{
    my ($start,$body,$end)=($1,$2,$3);

    # 1) single-quoted wikilink -> double-quoted
    $body =~ s{
      ^((?:note|notes|instruction|instructions)\s*:\s*)  # key+colon
      '\s*(\[\[[^]]+\]\])\s*'                            # '[[...]]'
      (\s*(?:#.*)?)\s*$                                  # optional comment
    }{$1"$2"$3}mgi;

    # 2) bare wikilink -> double-quoted
    $body =~ s{
      ^((?:note|notes|instruction|instructions)\s*:\s*)  # key+colon
      (\[\[[^]]+\]\])                                    # [[...]]
      (\s*(?:#.*)?)\s*$                                  # optional comment
    }{$1"$2"$3}mgi;

    $start.$body.$end
  }xes;
'
