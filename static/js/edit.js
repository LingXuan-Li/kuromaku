let timer = null;

function syncAll() {
    document.getElementById("hidden_field_a").value =
        document.getElementById("field_a").value || 0;

    document.getElementById("hidden_field_b").value =
        document.getElementById("field_b").value || 0;

    document.getElementById("hidden_field_c").value =
        document.getElementById("field_c").value || 0;
}

// 入力監視
document.querySelectorAll("input[type='number']").forEach(el => {
    el.addEventListener("input", () => {
        syncAll();
        triggerPreview();
    });
});

// ＋－ボタン対応
function changeValue(id, delta) {
    const input = document.getElementById(id);
    input.value = parseInt(input.value || 0) + delta;
    syncAll();
    triggerPreview();
}

// debounce付きプレビュー
function triggerPreview() {
    clearTimeout(timer);

    timer = setTimeout(async () => {

        const payload = {
            field_a: document.getElementById("field_a").value,
            field_b: document.getElementById("field_b").value,
            field_c: document.getElementById("field_c").value
        };

        try {
            const res = await fetch("/api/preview", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error("API error");

            const data = await res.json();

            updatePreview(data);

        } catch (err) {
            console.error("preview error:", err);
        }

    }, 100);
}

function updatePreview(data) {

    // Aコート
    document.getElementById("p_now_a").textContent = data.field_a.match ?? "";
    document.getElementById("p_next_a").textContent = data.field_a.next_match ?? "";
    document.getElementById("p_gather_a").textContent = data.field_a.gathering ?? "";

    // Bコート
    document.getElementById("p_now_b").textContent = data.field_b.match ?? "";
    document.getElementById("p_next_b").textContent = data.field_b.next_match ?? "";
    document.getElementById("p_gather_b").textContent = data.field_b.gathering ?? "";

    // Cコート
    document.getElementById("p_now_c").textContent = data.field_c.match ?? "";
    document.getElementById("p_next_c").textContent = data.field_c.next_match ?? "";
    document.getElementById("p_gather_c").textContent = data.field_c.gathering ?? "";
}