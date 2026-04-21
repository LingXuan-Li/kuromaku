let timer = null;

/* =========================
   共通ユーティリティ
========================= */

// 数値制限（-1未満禁止）
function clamp(value, min, max = Infinity) {
    value = parseInt(value);
    if (isNaN(value)) value = 0;
    return Math.max(min, Math.min(max, value));
}

// トースト通知
function showToast(message, isError = false) {
    let toast = document.getElementById("toast");

    // なければ自動生成
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "toast";
        toast.style.position = "fixed";
        toast.style.bottom = "20px";
        toast.style.right = "20px";
        toast.style.padding = "10px 16px";
        toast.style.borderRadius = "8px";
        toast.style.color = "#fff";
        toast.style.opacity = 0;
        toast.style.transition = "opacity 0.3s";
        document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.style.background = isError ? "#e74c3c" : "#333";
    toast.style.opacity = 1;

    setTimeout(() => {
        toast.style.opacity = 0;
    }, 2000);
}

/* =========================
   値同期
========================= */

function syncAll() {
    document.getElementById("hidden_field_a").value =
        clamp(document.getElementById("field_a").value, -1);

    document.getElementById("hidden_field_b").value =
        clamp(document.getElementById("field_b").value, -1);

    document.getElementById("hidden_field_c").value =
        clamp(document.getElementById("field_c").value, -1);
}

/* =========================
   入力監視（手入力対策）
========================= */

document.querySelectorAll("input[type='number']").forEach(el => {
    el.addEventListener("input", () => {

        // 強制補正
        el.value = clamp(el.value, -1);

        syncAll();
        triggerPreview();
    });
});

/* =========================
   ＋－ボタン
========================= */

function changeValue(id, delta) {
    const input = document.getElementById(id);

    let newValue = parseInt(input.value || 0) + delta;

    input.value = clamp(newValue, -1);

    syncAll();
    triggerPreview();
}

/* =========================
   プレビュー
========================= */

function triggerPreview() {
    clearTimeout(timer);

    timer = setTimeout(async () => {

        const payload = {
            field_a: clamp(document.getElementById("field_a").value, -1),
            field_b: clamp(document.getElementById("field_b").value, -1),
            field_c: clamp(document.getElementById("field_c").value, -1)
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

    // A
    document.getElementById("p_now_a").textContent = data.field_a.match ?? "";
    document.getElementById("p_next_a").textContent = data.field_a.next_match ?? "";
    document.getElementById("p_gather_a").textContent = data.field_a.gathering ?? "";

    // B
    document.getElementById("p_now_b").textContent = data.field_b.match ?? "";
    document.getElementById("p_next_b").textContent = data.field_b.next_match ?? "";
    document.getElementById("p_gather_b").textContent = data.field_b.gathering ?? "";

    // C
    document.getElementById("p_now_c").textContent = data.field_c.match ?? "";
    document.getElementById("p_next_c").textContent = data.field_c.next_match ?? "";
    document.getElementById("p_gather_c").textContent = data.field_c.gathering ?? "";
}

/* =========================
   保存処理（非同期）
========================= */

async function handleSubmit(e) {
    e.preventDefault();

    syncAll();

    const payload = {
        field_a: document.getElementById("hidden_field_a").value,
        field_b: document.getElementById("hidden_field_b").value,
        field_c: document.getElementById("hidden_field_c").value
    };

    try {
        const res = await fetch("", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error();

        showToast("保存しました");

    } catch (err) {
        console.error(err);
        showToast("保存に失敗しました", true);
    }
}