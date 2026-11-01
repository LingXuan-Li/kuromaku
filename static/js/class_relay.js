let sortable;
let classRelayData = [];
async function loadRelay() {
	const res = await fetch("/api/class_relay_load");
	classRelayData = await res.json();
	renderRelay();
}

function renderRelay() {
	const tbody = document.getElementById("race-body");
	tbody.innerHTML = "";
	classRelayData.forEach((team, index) => {
		const tr = document.createElement("tr");
		tr.innerHTML = `
            <td class="drag-handle">⠿</td>
            <td><input value="${team.team_name || ''}" onchange="updateRelay(${index}, 'team_name', this.value)"></td>
            <td><input value="${team.first || ''}" onchange="updateRelay(${index}, 'first', this.value)"></td>
            <td><input value="${team.second || ''}" onchange="updateRelay(${index}, 'second', this.value)"></td>
            <td><input value="${team.third || ''}" onchange="updateRelay(${index}, 'third', this.value)"></td>
            <td><input value="${team.fourth || ''}" onchange="updateRelay(${index}, 'fourth', this.value)"></td>
            <td><input value="${team.fifth || ''}" onchange="updateRelay(${index}, 'fifth', this.value)"></td>
            <td><input value="${team.sixth || ''}" onchange="updateRelay(${index}, 'sixth', this.value)"></td>
            <td><input value="${team.seventh || ''}" onchange="updateRelay(${index}, 'seventh', this.value)"></td>
            <td><input value="${team.eighth || ''}" onchange="updateRelay(${index}, 'eighth', this.value)"></td>
            <td><input value="${team.ninth || ''}" onchange="updateRelay(${index}, 'ninth', this.value)"></td>
            <td><input value="${team.tenth || ''}" onchange="updateRelay(${index}, 'tenth', this.value)"></td>
        `;
		tbody.appendChild(tr);
	});
	initSortable();
}

function updateRelay(index, key, value) {
	classRelayData[index][key] = value;
}
async function saveRace() {
	await fetch("/api/class_relay_save", {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: JSON.stringify({
			items: classRelayData
		})
	});
	alert("保存しました");
}

function initSortable() {
	if (sortable) {
		sortable.destroy();
	}
	sortable = new Sortable(document.getElementById("race-body"), {
		animation: 150,
		handle: ".drag-handle",
		onEnd(evt) {
			const moved = classRelayData.splice(evt.oldIndex, 1)[0];
			classRelayData.splice(evt.newIndex, 0, moved);
		}
	});
}
loadRelay();