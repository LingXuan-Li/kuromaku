const editor = document.getElementById("editor");
const preview = document.getElementById("preview");
const menu = document.getElementById("menu");
const saveBtn = document.getElementById("saveBtn");

async function updatePreview() {
    const res = await fetch("/api/message_preview", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ text: editor.value })
    });

    const data = await res.json();
    preview.innerHTML = data.html || "";
}

editor.addEventListener("input", updatePreview);

editor.addEventListener("contextmenu", (e) => {
    e.preventDefault();

    menu.style.left = e.pageX + "px";
    menu.style.top = e.pageY + "px";
    menu.style.display = "block";
});


document.addEventListener("click", () => {
    menu.style.display = "none";
});

function execCmd(type) {
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const selected = editor.value.substring(start, end);

    let result = selected;

    if (type === "bold") {
        result = "**" + selected + "**";
    }

    if (type === "green") {
        result = "$$" + selected + "$$";
    }

    if (type === "orange") {
        result = "@@" + selected + "@@";
    }

    editor.setRangeText(result, start, end, "end");
    menu.style.display = "none";

    editor.dispatchEvent(new Event("input"));
}

async function save() {
    await fetch("/api/message_save", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ text: editor.value })
    });

    menu.style.display = "none";
    alert("保存しました");
}

saveBtn.addEventListener("click", save);

async function loadData() {
    const res = await fetch("/api/message_load");
    const data = await res.json();

    editor.value = data.text || "";
    updatePreview();
}

loadData();