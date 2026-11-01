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
    // document.getElementById(`${prefix}-game`).textContent = d.game || "---";
    document.getElementById(`${prefix}-next`).textContent = d.next || "---";
    // document.getElementById(`${prefix}-next-game`).textContent = d.next_game || "---";
    document.getElementById(`${prefix}-gathering`).textContent = d.gathering || "---";
}

setInterval(fetchDashboard, 3000); //毎3.0秒
fetchDashboard();

let prevJson = "";

function clearClubRelay() {
    document.getElementById("relay-club").textContent = "---";

    for (let n = 1; n <= 6; n++) {
        document.getElementById(`Re${n}-team`).textContent = "---";
        document.getElementById(`Re${n}-1`).textContent = "---";
        document.getElementById(`Re${n}-2`).textContent = "---";
        document.getElementById(`Re${n}-3`).textContent = "---";
        document.getElementById(`Re${n}-4`).textContent = "---";
        document.getElementById(`Re${n}-5`).textContent = "---";
        document.getElementById(`Re${n}-6`).textContent = "---";
    }
}

async function loadClubRelay() {
    try {
        const res = await fetch("/api/relay_data");
        const data = await res.json();

        const currentJson = JSON.stringify(data);

        if (currentJson === prevJson) {
            return; // 変更なし
        }

        prevJson = currentJson;
        clearClubRelay();

        document.getElementById("relay-club").textContent =
            data.category_name || "---";

        data.items.forEach((team, i) => {
            const n = i + 1;

            document.getElementById(`Re${n}-team`).textContent =
                team.team_name ?? "---";

            document.getElementById(`Re${n}-1`).textContent =
                team.first ?? "---";

            document.getElementById(`Re${n}-2`).textContent =
                team.second ?? "---";

            document.getElementById(`Re${n}-3`).textContent =
                team.third ?? "---";

            document.getElementById(`Re${n}-4`).textContent =
                team.fourth ?? "---";

            document.getElementById(`Re${n}-5`).textContent =
                team.fifth ?? "---";

            document.getElementById(`Re${n}-6`).textContent =
                team.sixth ?? "---";
        });

    } catch (err) {
        console.error("Club Relay data load failed:", err);
    }
}

async function loadClassRelay() {
    try {
        const res = await fetch("/api/class_relay_data");
        const data = await res.json();

        data.items.forEach((team, i) => {
            const n = i + 1;

            document.getElementById(`ClR${n}-team`).textContent =
                team.team_name ?? "---";

            document.getElementById(`ClR${n}-1`).textContent =
                team.first ?? "---";

            document.getElementById(`ClR${n}-2`).textContent =
                team.second ?? "---";

            document.getElementById(`ClR${n}-3`).textContent =
                team.third ?? "---";

            document.getElementById(`ClR${n}-4`).textContent =
                team.fourth ?? "---";

            document.getElementById(`ClR${n}-5`).textContent =
                team.fifth ?? "---";

            document.getElementById(`ClR${n}-6`).textContent =
                team.sixth ?? "---";

            document.getElementById(`ClR${n}-7`).textContent =
                team.seventh ?? "---";

            document.getElementById(`ClR${n}-8`).textContent =
                team.eighth ?? "---";

            document.getElementById(`ClR${n}-9`).textContent =
                team.ninth ?? "---";

            document.getElementById(`ClR${n}-10`).textContent =
                team.tenth ?? "---";
        });

    } catch (err) {
        console.error("Class Relay data load failed:", err);
    }
}

loadClubRelay();
loadClassRelay();
setInterval(loadClubRelay, 10000); //毎10.0秒
setInterval(loadClassRelay, 10000); //毎10.0秒

async function updatePageStyle() {
  const res = await fetch('/api/page_style');
  const data = await res.json();

  const activeStyle = data.style;

  document.querySelectorAll('[data-style]').forEach(el => {
    el.classList.toggle(
      'hidden',
      el.dataset.style !== activeStyle
    );
  });
}

updatePageStyle();
setInterval(updatePageStyle, 5000); //毎5.0秒



// ===== インフォメーションバー制御 =====
const infoText = document.querySelector(".info-text");

// 初回スタート
startInfoScroll();

function startInfoScroll() {
    infoText.classList.remove("scroll-once");

    // 再描画トリガー
    void infoText.offsetWidth;

    // 文字数で速度調整
    const distance = infoText.scrollWidth; // テキストの実際の幅
    const speed = 100; // 100px/秒

    const duration = distance / speed;

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
