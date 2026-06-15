let relayData = [];
let cultureData = [];
let sportsData = [];

let sortable;


async function loadCulture() {
    const res = await fetch("/api/culture_load");
    cultureData = await res.json();
    renderCulture();
}

async function loadSports() {
    const res = await fetch("/api/sports_load");
    sportsData = await res.json();
    renderSports();
}

async function loadRelay() {
    const res = await fetch("/api/relay_load");
    relayData = await res.json();
    renderRelay();
}

async function loadCategory() {
    const res = await fetch("/api/category_load");
    const data = await res.json();

    document.getElementById("current-category").innerText =
        data.category_name + "（" + data.category + "）";

}



function renderCulture() {

    const tbody =
        document.getElementById("culture-body");

    tbody.innerHTML = "";

    cultureData.forEach((team, index) => {

        const tr = document.createElement("tr");

        tr.innerHTML = `
        <td>${team.id}</td>

        <td>
            <input
                value="${team.team_name || ''}"
                onchange="updateCulture(${index}, 'team_name', this.value)">
        </td>

        <td>
            <input
                value="${team.first || ''}"
                onchange="updateCulture(${index}, 'first', this.value)">
        </td>

        <td>
            <input
                value="${team.second || ''}"
                onchange="updateCulture(${index}, 'second', this.value)">
        </td>

        <td>
            <input
                value="${team.third || ''}"
                onchange="updateCulture(${index}, 'third', this.value)">
        </td>

        <td>
            <input
                value="${team.fourth || ''}"
                onchange="updateCulture(${index}, 'fourth', this.value)">
        </td>

        <td>
            <input
                value="${team.fifth || ''}"
                onchange="updateCulture(${index}, 'fifth', this.value)">
        </td>

        <td>
            <input
                value="${team.sixth || ''}"
                onchange="updateCulture(${index}, 'sixth', this.value)">
        </td>

        <td>
            <button
                class="btn btn-green"
                onclick="addRelayFromCulture(${index})">
                追加
            </button>
        </td>
    `;

        tbody.appendChild(tr);
    });

}

function updateCulture(index, key, value) {
    cultureData[index][key] = value;
}

function addRelayFromCulture(index) {
    addRelay({
        ...cultureData[index]
    });
}



function renderSports() {

    const tbody =
        document.getElementById("sports-body");

    tbody.innerHTML = "";

    sportsData.forEach((team, index) => {

        const tr = document.createElement("tr");

        tr.innerHTML = `
        <td>${team.id}</td>

        <td>
            <input
                value="${team.team_name || ''}"
                onchange="updateSports(${index}, 'team_name', this.value)">
        </td>

        <td>
            <input
                value="${team.first || ''}"
                onchange="updateSports(${index}, 'first', this.value)">
        </td>

        <td>
            <input
                value="${team.second || ''}"
                onchange="updateSports(${index}, 'second', this.value)">
        </td>

        <td>
            <input
                value="${team.third || ''}"
                onchange="updateSports(${index}, 'third', this.value)">
        </td>

        <td>
            <input
                value="${team.fourth || ''}"
                onchange="updateSports(${index}, 'fourth', this.value)">
        </td>

        <td>
            <input
                value="${team.fifth || ''}"
                onchange="updateSports(${index}, 'fifth', this.value)">
        </td>

        <td>
            <input
                value="${team.sixth || ''}"
                onchange="updateSports(${index}, 'sixth', this.value)">
        </td>

        <td>
            <button
                class="btn btn-green"
                onclick="addRelayFromSports(${index})">
                追加
            </button>
        </td>
    `;

        tbody.appendChild(tr);
    });

}

function updateSports(index, key, value) {
    sportsData[index][key] = value;
}

function addRelayFromSports(index) {
    addRelay({
        ...sportsData[index]
    });
}



function renderRelay() {


    const tbody =
        document.getElementById("relay-body");

    tbody.innerHTML = "";

    if (relayData.length === 0) {

        const tr = document.createElement("tr");

        tr.innerHTML = `
        <td colspan="9"
            style="color:#aaa;text-align:center;padding:12px">
            （なし）
        </td>
    `;

        tbody.appendChild(tr);

        if (sortable) {
            sortable.destroy();
            sortable = null;
        }

        return;
    }

    relayData.forEach((team, index) => {

        const tr = document.createElement("tr");

        const fields = [
            "team_name",
            "first",
            "second",
            "third",
            "fourth",
            "fifth",
            "sixth"
        ];

        const cells = fields.map(f => `
        <td>
            <input
                value="${team[f] ?? ''}"
                onchange="updateField(${index}, '${f}', this.value)">
        </td>
    `).join("");

        tr.innerHTML = `
        <td class="drag-handle">⠿</td>

        ${cells}

        <td>
            <button
                class="btn btn-red"
                onclick="deleteRelay(${index})">
                削除
            </button>
        </td>
    `;

        tbody.appendChild(tr);
    });

    initSortable();
}

function updateField(index, key, value) {
    relayData[index][key] = value;
}

function addRelay(team) {
    const exists = relayData.some(
        item => item.team_name === team.team_name
    );

    if (exists) {
        alert("その団体は既に追加されています");
        return;
    }

    relayData.push(team);

    renderRelay();
}

function deleteRelay(index) {
    relayData.splice(index, 1);

    renderRelay();
}



function initSortable() {

    if (sortable) {
        sortable.destroy();
    }

    sortable = new Sortable(
        document.getElementById("relay-body"), {
            animation: 150,

            handle: ".drag-handle",

            onEnd(evt) {

                const moved =
                    relayData.splice(
                        evt.oldIndex,
                        1
                    )[0];

                relayData.splice(
                    evt.newIndex,
                    0,
                    moved
                );
            }
        }
    );

}



async function saveCulture() {

    await fetch("/api/culture_save", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            items: cultureData
        })
    });

    alert("CultureClubを保存しました");

}

async function saveSports() {
    await fetch("/api/sports_save", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            items: sportsData
        })
    });

    alert("SportsClubを保存しました");

}

async function saveRelay() {

    await fetch("/api/relay_save", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            category: "relay",
            items: relayData
        })
    });

    alert("Final Relayを保存しました");

}

async function saveCategory(category) {

    await fetch("/api/category_save", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            category
        })
    });

    await loadCategory();

    alert(
        `案内表示を ${category} に切り替えました`
    );

}


loadCulture();
loadSports();
loadRelay();
loadCategory();