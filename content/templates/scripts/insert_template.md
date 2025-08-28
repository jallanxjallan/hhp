<%*
function insertTemplate(templateName) {
    const templatePath = `Templates/${templateName}.md`;
    const template = await tp.file.read(templatePath);
    return template;
}

// Insert templates based on the chosen type
const templateType = tp.file.get_attribute("templateType");

if (templateType === "scene") {
    tR += await insertTemplate("scene");
} else if (templateType === "topic") {
    tR += await insertTemplate("topic");
} else if (templateType === "instruction") {
    tR += await insertTemplate("instruction");
}
%>