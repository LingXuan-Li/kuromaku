let previousData = null;

async function fetchDashboard() {
    try {
        const res = await fetch("/api/dashboard");
        const data = await res.json();

        if (!previousData) {
            updateAll(data);
        } else {
            updateDiff(data, previousData);
        }

        previousData = data;

    } catch (err) {
        console.error(err);
    }
}

function updateAll(data) {
    updateField("a", data.A);
    updateField("b", data.B);
    updateField("c", data.C);
}

function updateDiff(newData, oldData) {
    ["A", "B", "C"].forEach(key => {
        if (JSON.stringify(newData[key]) !== JSON.stringify(oldData[key])) {
            updateField(key.toLowerCase(), newData[key]);
        }
    });
}

function updateField(prefix, d) {
    document.getElementById(`${prefix}-teamX`).textContent = d.teamX || "---";
    document.getElementById(`${prefix}-teamY`).textContent = d.teamY || "---";
    document.getElementById(`${prefix}-game`).textContent = d.game || "---";
    document.getElementById(`${prefix}-next`).textContent = d.next || "---";
    document.getElementById(`${prefix}-next-game`).textContent = d.next_game || "---";
    document.getElementById(`${prefix}-gathering`).textContent = d.gathering || "---";
}

setInterval(fetchDashboard, 3000);
fetchDashboard();

// ===== インフォメーションバー制御 =====
const infoText = document.querySelector(".info-text");

// 初回スタート
startInfoScroll();

function startInfoScroll() {
    infoText.classList.remove("scroll-once");

    // 再描画トリガー（これないと再スタートしない）
    void infoText.offsetWidth;

    // 文字数で速度調整（おすすめ）
    const textLength = infoText.textContent.length;
    const duration = 15;
    infoText.style.animationDuration = duration + "s";

    infoText.classList.add("scroll-once");
}

// 流れ終わったら更新
infoText.addEventListener("animationend", async () => {
    try {
        const res = await fetch("/api/info"); // ← インフォ専用API
        const data = await res.json();

        // テキスト更新
        infoText.innerHTML = data.message || "お知らせはありません";

    } catch (e) {
        console.error("info更新失敗", e);
    }

    // 再スタート
    startInfoScroll();
});
