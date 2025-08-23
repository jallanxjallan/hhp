# Queries Dashboard

## Scene → Instructions
```dataview
TABLE file.link AS "Scene", join(filter(file.outlinks, (l) => contains(l, "Instructions/")), ", ") AS "Instructions"
FROM "Scenes"
```

## Scene → Notes
```dataview
TABLE file.link AS "Scene", join(filter(file.outlinks, (l) => contains(l, "Notes/")), ", ") AS "Notes"
FROM "Scenes"
```

## Combined Scene Links
```dataview
TABLE file.link AS "Scene",
join(filter(file.outlinks, (l) => contains(l, "Instructions/")), ", ") AS "Instructions",
join(filter(file.outlinks, (l) => contains(l, "Notes/")), ", ") AS "Notes"
FROM "Scenes"
```

---

## Instructions → Scenes
```dataview
TABLE file.link AS "Instruction",
length(file.inlinks) AS "# Scenes",
file.inlinks AS "Scenes"
FROM "Instructions"
```

## Notes → Scenes
```dataview
TABLE file.link AS "Note",
length(file.inlinks) AS "# Scenes",
file.inlinks AS "Scenes"
FROM "Notes"
```

---

## Unlinked Scenes (no Instructions or Notes)
```dataview
TABLE file.link AS "Scene"
FROM "Scenes"
WHERE length(filter(file.outlinks, (l) => contains(l, "Instructions/"))) = 0
AND length(filter(file.outlinks, (l) => contains(l, "Notes/"))) = 0
```

## Orphan Instructions (no Scenes link here)
```dataview
TABLE file.link AS "Instruction"
FROM "Instructions"
WHERE length(file.inlinks) = 0
```

## Orphan Notes (no Scenes link here)
```dataview
TABLE file.link AS "Note"
FROM "Notes"
WHERE length(file.inlinks) = 0
```
