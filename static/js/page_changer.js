const guides = {
    opening: {
        url: "#",
        title: "開会式"
    },
    "1G-game": {
        url: "#",
        title: "1学年競技（玉入れ）"
    },
    "2G-game": {
        url: "#",
        title: "2学年競技（ムカデ競争）"
    },
    "3G-game": {
        url: "#",
        title: "3学年競技（中当て）"
    },
    "4G-game": {
        url: "#",
        title: "4学年競技（台風の目）"
    },
    "5G-game": {
        url: "#",
        title: "5学年競技（綱引き）"
    },
    jump: {
        url: "#",
        title: "大縄跳び"
    },
    lunch: {
        url: "#",
        title: "昼休憩"
    },
    closing: {
        url: "#",
        title: "閉会式"
    },
    tournament: {
        url: "/tournaments_editor",
        title: "トーナメント"
    },
    club_relay: {
        url: "/relay_editor",
        title: "部活対抗リレー"
    },
    class_relay: {
        url: "/class_relay",
        title: "選抜リレー"
    }
};

async function savePageStyle(style) {
    await fetch("/api/page_style_save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ style })
    });
    await loadPageStyle();
    alert(`ダッシュボード表示を ${guides[style].title} (${style}) に切り替えました`);
}

async function loadPageStyle() {
    const res = await fetch("/api/page_style_load");
    const data = await res.json();
    document.getElementById("current-style").innerText =
        data.style_name + "（" + data.style + "）";

    document.getElementById("card-guide").innerHTML = `
        <a href="${guides[data.style].url}"
           target="_blank"
           rel="noopener noreferrer"
           class="card">

            <div class="card-path">${guides[data.style].url} (${guides[data.style].title})</div>

            <div class="card-desc">
                ${guides[data.style].title}編集画面を新しいタブで開く
            </div>

            <div class="card-arrow">
                ↗ OPEN IN NEW TAB
            </div>
        </a>
    `;
}

loadPageStyle();