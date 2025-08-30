

# Status Queries (Scenes)

> These assume the **scene** notes carry a `status` field in YAML, with emoji values.

## 🤖 Queued Scenes
```dataview
TABLE WITHOUT ID file.link AS Scene, file.tags AS Tags
FROM "scenes"
WHERE queue = true
SORT file.name ASC
```

## 💬 Unqueued Prompts 
```dataview
TABLE WITHOUT ID file.link AS Scene, file.tags AS Tags
FROM "scenes"
WHERE status = "💬" OR contains(string(status), "💬")
and queue = false
SORT file.tags ASC
```

## 🤖 Generated Scenes (e.g., machine‑edited or AI‑ready)
```dataview
TABLE WITHOUT ID file.link AS Scene, file.tags AS Tags
FROM "scenes"
WHERE status = "🤖" OR contains(string(status), "🤖")
SORT file.name ASC
```

## 💬 Prompt Scenes (awaiting / contains prompt work)
```dataview
TABLE WITHOUT ID file.link AS Scene, file.tags AS Tags
FROM "scenes"
WHERE status = "💬" OR contains(string(status), "💬")
SORT file.tags ASC
```

## 🔳 Placeholder Scenes (stub content)
```dataview
TABLE WITHOUT ID file.link AS Scene, file.tags AS Tags
FROM "scenes"
WHERE status = "🔳" OR contains(string(status), "🔳")
SORT file.name ASC
```



```dataview
TABLE file.link as Scene, length(file.content) as Words
FROM "scenes"
WHERE contains(file.content, "1.")
```

