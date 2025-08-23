# queries.md

# Scene → Instructions
```dataview
TABLE file.link AS "Scene", links AS "Instructions"
FROM "Scenes"
FLATTEN file.outlinks AS links
WHERE contains(links, "instructions/")
```

# Scene → Notes
```dataview
TABLE file.link AS "Scene", links AS "Notes"
FROM "Scenes"
FLATTEN file.outlinks AS links
WHERE contains(links, "Notes/")
```

# Combined: Scenes, Instructions, Notes
```dataview
TABLE file.link AS "Scene",
join(filter(file.outlinks, (l) => contains(l, "Instructions/")), ", ") AS "Instructions",
join(filter(file.outlinks, (l) => contains(l, "Notes/")), ", ") AS "Notes"
FROM "Scenes"
```

---

# Instructions → Linked Scenes
```dataview
TABLE file.link AS "Instruction", file.inlinks AS "Scenes"
FROM "Instructions"
```

# Notes → Linked Scenes
```dataview
TABLE file.link AS "Note", file.inlinks AS "Scenes"
FROM "Notes"
```
