const BOX_POS = {
	R1L: {
		x: 40,
		y: 200
	},
	R1C: {
		x: 200,
		y: 200
	},
	R1R: {
		x: 360,
		y: 200
	},
	SF1: {
		x: (40 + 200) / 2,
		y: 110
	},
	Final: {
		x: ((40 + 200) / 2 + 360) / 2,
		y: 20
	}
};

function isEliminated(tNum, seed) {
	return Object.values(S.tournaments[tNum].matches).some(m => m.winner && m.winner.seed !== seed && (m.team1?.seed === seed || m.team2?.seed === seed));
}

function findActiveMatch(tNum, seed) {
	for (const [id, m] of Object.entries(S.tournaments[tNum].matches)) {
		if (!m.winner && m.team1 && m.team2 && (m.team1.seed === seed || m.team2.seed === seed)) {
			return id;
		}
	}
	return null;
}

function findActiveMatch(tNum, seed) {
	for (const [id, m] of Object.entries(S.tournaments[tNum].matches)) {
		if (!m.winner && m.team1 && m.team2 && (m.team1.seed === seed || m.team2.seed === seed)) {
			return id;
		}
	}
	return null;
}
/* ═══════════════ HISTORY ═══════════════ */
function pushHistory() {
	S.history.push(structuredClone({
		tournaments: S.tournaments,
		preparingMatches: S.preparingMatches,
		schedule: S.schedule,
		PROGRESS: PROGRESS
	}));
	if (S.history.length > 30) S.history.shift();
}

function undo() {
	if (S.history.length === 0) return;
	const prev = S.history.pop();
	S.tournaments = structuredClone(prev.tournaments);
	S.preparingMatches = structuredClone(prev.preparingMatches);
	S.schedule = structuredClone(prev.schedule);
	PROGRESS = structuredClone(prev.PROGRESS);
	S.dirty = true;
	render();
}
/* ═══════════════ BRACKET LOGIC ═══════════════ */
function isEliminated(tNum, seed) {
	return Object.values(S.tournaments[tNum].matches).some(m => m.winner && m.winner.seed !== seed && (m.team1?.seed === seed || m.team2?.seed === seed));
}

function findActiveMatch(tNum, seed) {
	for (const [id, m] of Object.entries(S.tournaments[tNum].matches)) {
		if (!m.winner && m.team1 && m.team2 && (m.team1.seed === seed || m.team2.seed === seed)) {
			return id;
		}
	}
	return null;
}
/* ═══════════════ PREPARING MATCHES ═══════════════ */
function addPreparingMatch() {
	pushHistory();
	const id = 'prep_' + newUid();
	S.preparingMatches[id] = {
		id: id,
		label: '準備中',
		team1: null,
		team2: null,
		winner: null
	};
	S.dirty = true;
	render();
}

function removePreparingMatch(id) {
	pushHistory();
	delete S.preparingMatches[id];
	// スケジュールからも削除
	S.schedule = S.schedule.filter(s => !(s.tNum === 'preparing' && s.matchId === id));
	S.dirty = true;
	render();
}

/* ═══════════════ SCHEDULE CORE ═══════════════ */
function addToSchedule(tNum, matchId, col, beforeUid) {
	pushHistory();
	
	if (tNum !== 'preparing') {
		if (S.schedule.find(s => s.tNum === tNum && s.matchId === matchId)) return;
	}
	
	S.dirty = true;
	const colItems = S.schedule.filter(s => s.col === col).sort((a, b) => a.order - b.order);
	let insertIdx = colItems.length;
	if (beforeUid) {
		const idx = colItems.findIndex(s => s.uid === beforeUid);
		if (idx >= 0) insertIdx = idx;
	}
	S.schedule.push({
		uid: newUid(),
		tNum,
		matchId,
		col,
		order: insertIdx + 0.5,
		status: 'pending'
	});
	// 再整列
	S.schedule.filter(s => s.col === col).sort((a, b) => a.order - b.order).forEach((s, i) => s.order = i);
	render();
}

function moveScheduleItem(uid, newCol, beforeUid) {
	const item = S.schedule.find(s => s.uid === uid);
	if (!item) return;
	pushHistory();
	item.col = newCol;
	const colItems = S.schedule.filter(s => s.col === newCol && s.uid !== uid).sort((a, b) => a.order - b.order);
	let insertIdx = colItems.length;
	if (beforeUid) {
		const idx = colItems.findIndex(s => s.uid === beforeUid);
		if (idx >= 0) insertIdx = idx;
	}
	colItems.splice(insertIdx, 0, item);
	colItems.forEach((s, i) => s.order = i);
	render();
}

function removeFromSchedule(uid) {
	pushHistory();
	S.schedule = S.schedule.filter(s => s.uid !== uid);
	render();
}

function setStatus(uid, status) {
	pushHistory();
	const item = S.schedule.find(s => s.uid === uid);
	if (!item) return;
	const sameCol = S.schedule.filter(s => s.col === item.col).sort((a, b) => a.order - b.order); // 上→下
	// currentが選ばれたときだけ特別処理
	if (status === 'current') {
		let passed = false;
		for (const s of sameCol) {
			if (s.uid === uid) {
				s.status = 'current';
				passed = true;
			} else if (!passed) {
				// 上側 → 終了扱い
				s.status = 'done';
			} else {
				// 下側 → 未
				s.status = 'pending';
			}
		}
	} else {
		// 通常更新（current以外はそのまま）
		item.status = status;
	}
	S.dirty = true;
	render();
}
/* ═══════════════ DATA & STATE ═══════════════ */
let DATA = []; // teams
let PROGRESS = []; // 追加
let _uid = 0;
const newUid = () => 'u' + (++_uid);
const S = {
	currentTournament: 1,
	currentView: 'tournament', // 'tournament' または 'preparing'
	tournaments: {},
	preparingMatches: {},
	schedule: [],
	history: [],
	dirty: false,
};
/* ═══════════════ API ACTIONS ═══════════════ */
async function fetchInitialData() {
	try {
		const res = await fetch('/api/tournaments_data');
		if (!res.ok) throw new Error('データ取得失敗');
		const json = await res.json();
		DATA = json.teams || [];
		PROGRESS = json.progress || [];
		S.schedule = (json.schedule || []).map((s, i) => ({
			uid: newUid(),
			tNum: s.tournament_number,
			matchId: s.match_id,
			col: s.col,
			order: s.row,
			status: s.status || 'pending'
		}));
		// トーナメント初期化
		getTNums().forEach(num => {
			S.tournaments[num] = initTournament(num);
		});
		// 進行データ反映
		applyProgress();
		render();
	} catch (err) {
		console.error(err);
		alert('データの読み込みに失敗しました。');
	}
}
/* ═══════════════ PROGRESS適用 ═══════════════ */
function applyProgress() {
	PROGRESS.forEach(p => {
		const t = S.tournaments[p.tournament_number];
		if (!t) return;
		const m = t.matches[p.match_id];
		if (!m) return;
		const winner = [m.team1, m.team2].find(tm => tm?.seed === p.winner_seed);
		if (winner) {
			m.winner = winner;
			propagate(t);
		}
	});
}
/* ═══════════════ SAVE ═══════════════ */
async function save() {
	const courtNames = ['A', 'B', 'C'];
	// schedule
	const schedulePayload = S.schedule.map(s => {
		let m;
		if (s.tNum === 'preparing') {
			m = S.preparingMatches[s.matchId];
		} else {
			const t = S.tournaments[s.tNum];
			m = t?.matches[s.matchId];
		}

		const isPrep = s.tNum === 'preparing';
		const teamXName = isPrep ? '---' : (m?.team1?.team_name || '---');
		const teamYName = isPrep ? '---' : (m?.team2?.team_name || '---');

		return {
			// NOT NULL エラー対策（準備中は 0、それ以外は数値に変換）
			tournament_number: isPrep ? 0 : Number(s.tNum), 
			match_id: s.matchId,
			field: courtNames[s.col] + 'コート',
			label: m?.label || '準備中',
			team_x: teamXName,
			team_y: teamYName,
			game: isPrep ? '準備中' : (S.tournaments[s.tNum]?.gameName || ''),
			col: s.col,
			row: Math.floor(s.order),
			status: s.status
		};
	});

	// progress
	const progressPayload = [];
	Object.entries(S.tournaments).forEach(([tNum, t]) => {
		Object.values(t.matches).forEach(m => {
			if (m.winner) {
				progressPayload.push({
					tournament_number: Number(tNum),
					match_id: m.id,
					winner_seed: m.winner.seed
				});
			}
		});
	});
	try {
		const res = await fetch('/api/save_match', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				schedule: schedulePayload,
				progress: progressPayload
			})
		});
		const text = await res.text();
		if (!res.ok) {
			console.error("サーバーエラー:", text);
			throw new Error(text);
		}
		alert('保存が完了しました。');
		S.dirty = false;
		document.getElementById('dirtyBanner').classList.remove('show');
	} catch (err) {
		console.error(err);
		alert('保存に失敗しました。\n' + err.message);
	}
}

function setWinner(tNum, matchId, seed) {
	const t = S.tournaments[tNum];
	const m = t?.matches?.[matchId];
	if (!m) return;
	const winner = [m.team1, m.team2].find(tm => tm?.seed === seed);
	if (!winner) return;
	pushHistory();
	m.winner = winner;
	propagate(t);
	S.dirty = true;
	render();
}
/* ═══════════════ BRACKET LOGIC ═══════════════ */
function propagate(t) {
	// 準決勝
	t.matches.SF1.team1 = t.matches.R1L.winner || null;
	t.matches.SF1.team2 = t.matches.R1C.winner || null;
	// 決勝
	t.matches.Final.team1 = t.matches.SF1.winner || null;
	t.matches.Final.team2 = t.matches.R1R.winner || null;
}
/* ═══════════════ RENDER ═══════════════ */
function el(tag, cls) {
	const e = document.createElement(tag);
	if (cls) e.className = cls;
	return e;
}

function render() {
	if (DATA.length === 0) return; // データ未取得時は描画しない
	renderTournament();
	renderCourt();
	const db = document.getElementById('dirtyBanner');
	if (db) S.dirty ? db.classList.add('show') : db.classList.remove('show');
}

function renderTournament() {
	const panel = document.getElementById('tourn-panel');
	panel.innerHTML = '';
	const tabs = el('div', 'tabs');
	
	// トーナメントタブ
	getTNums().forEach(num => {
		const gn = DATA.find(d => d.tournament_number === num)?.game_name ?? '';
		const isActive = S.currentView === 'tournament' && num === S.currentTournament;
		const btn = el('button', 'tab' + (isActive ? ' active' : ''));
		btn.textContent = `T${num}（${gn}）`;
		btn.onclick = () => {
			S.currentView = 'tournament';
			S.currentTournament = num;
			render();
		};
		tabs.appendChild(btn);
	});

	// 準備中タブ
	const prepBtn = el('button', 'tab' + (S.currentView === 'preparing' ? ' active' : ''));
	prepBtn.textContent = '準備中';
	prepBtn.onclick = () => {
		S.currentView = 'preparing';
		render();
	};
	tabs.appendChild(prepBtn);

	panel.appendChild(tabs);

	// コンテンツ描画
	if (S.currentView === 'preparing') {
		renderPreparingMatches(panel);
	} else {
		renderBracket(panel);
	}
}

function renderBracket(panel) {
	const tNum = S.currentTournament;
	const t = S.tournaments[tNum];
	
	const container = el('div', 'bracket-container');
	const svgNS = 'http://www.w3.org/2000/svg';
	const svg = document.createElementNS(svgNS, 'svg');
	svg.setAttribute('class', 'lines');
	svg.setAttribute('viewBox', '0 0 530 262');
	const g = document.createElementNS(svgNS, 'g');
	g.setAttribute('stroke', '#0d2f6e');
	g.setAttribute('stroke-width', '3');
	g.setAttribute('fill', 'none');
	const BOX_W = 130;
	const BOX_H = 70;

	function line(a, b) {
		const ax = a.x + BOX_W / 2;
		const ay = a.y + BOX_H / 2;
		const bx = b.x + BOX_W / 2;
		const by = b.y + BOX_H / 2;
		const midX = (ax + bx) / 2;
		const l1 = document.createElementNS(svgNS, 'line');
		l1.setAttribute('x1', ax);
		l1.setAttribute('y1', ay);
		l1.setAttribute('x2', midX);
		l1.setAttribute('y2', ay);
		const l2 = document.createElementNS(svgNS, 'line');
		l2.setAttribute('x1', midX);
		l2.setAttribute('y1', ay);
		l2.setAttribute('x2', midX);
		l2.setAttribute('y2', by);
		const l3 = document.createElementNS(svgNS, 'line');
		l3.setAttribute('x1', midX);
		l3.setAttribute('y1', by);
		l3.setAttribute('x2', bx);
		l3.setAttribute('y2', by);
		g.appendChild(l1);
		g.appendChild(l2);
		g.appendChild(l3);
	}
	line(BOX_POS.R1L, BOX_POS.SF1);
	line(BOX_POS.R1C, BOX_POS.SF1);
	line(BOX_POS.SF1, BOX_POS.Final);
	line(BOX_POS.R1R, BOX_POS.Final);
	svg.appendChild(g);
	container.appendChild(svg);
	
	Object.values(t.matches).forEach(m => {
		const pos = BOX_POS[m.id];
		const isScheduled = S.schedule.some(s => s.tNum === tNum && s.matchId === m.id);
		const box = el('div', 'match-box' + (isScheduled ? ' scheduled' : ''));
		box.style.left = pos.x + 'px';
		box.style.top = pos.y + 'px';
		box.setAttribute('draggable', 'true');
		const lbl = el('div', 'mb-label');
		const lblText = document.createElement('span');
		lblText.textContent = m.label;
		lbl.appendChild(lblText);
		if (isScheduled) {
			const b = el('span', 'mb-scheduled-badge');
			b.textContent = '登録済';
			lbl.appendChild(b);
		}
		box.appendChild(lbl);
		const t1 = el('div', 'mb-team');
		t1.textContent = m.team1?.team_name ?? '未定';
		box.appendChild(t1);
		const vs = el('div', 'mb-vs');
		vs.textContent = 'vs';
		box.appendChild(vs);
		const t2 = el('div', 'mb-team');
		t2.textContent = m.team2?.team_name ?? '未定';
		box.appendChild(t2);
		if (m.winner) {
			const w = el('div', 'mb-winner');
			w.textContent = '🏆 ' + m.winner.team_name;
			box.appendChild(w);
		}
		box.addEventListener('dragstart', e => {
			e.dataTransfer.setData('application/json', JSON.stringify({
				type: 'bracket',
				tNum,
				matchId: m.id
			}));
		});
		container.appendChild(box);
	});
	panel.appendChild(container);
	
	const seedRow = el('div', 'seed-row');
	const champion = t.matches.Final.winner;
	[1, 2, 3, 4, 5, 6].forEach(seed => {
		const team = t.bySeed[seed];
		const elim = isEliminated(tNum, seed);
		const isChamp = champion?.seed === seed;
		const activeId = findActiveMatch(tNum, seed);
		const box = el('div', 'seed-box' + (elim ? ' eliminated' : '') + (isChamp ? ' champion' : ''));
		const num = el('div', 'seed-num');
		num.textContent = seed;
		box.appendChild(num);
		const nm = el('div', 'seed-name');
		nm.textContent = team?.team_name ?? '—';
		box.appendChild(nm);
		if (isChamp) {
			const p = el('div', 'status-pill champ');
			p.textContent = '🏆 優勝';
			box.appendChild(p);
		} else if (elim) {
			const p = el('div', 'status-pill lost');
			p.textContent = '敗退';
			box.appendChild(p);
		} else if (activeId) {
			const btn = el('button', 'win-btn');
			btn.textContent = '勝利';
			btn.onclick = () => setWinner(tNum, activeId, seed);
			box.appendChild(btn);
		}
		seedRow.appendChild(box);
	});
	panel.appendChild(seedRow);
	
	const footer = el('div', 'tourn-footer');
	if (champion) {
		const b = el('div', 'champion-banner');
		b.textContent = '🏆 優勝: ' + champion.team_name;
		footer.appendChild(b);
	}
	const rb = el('button', 'reset-btn');
	rb.textContent = 'リセット';
	rb.onclick = () => {
		S.tournaments[tNum] = initTournament(tNum);
		render();
	};
	footer.appendChild(rb);
	panel.appendChild(footer);
}

function renderPreparingMatches(panel) {
	const container = el('div', 'preparing-container');
	const header = el('div', 'preparing-header');
	header.textContent = '下の「準備中」ボックスをコートへドラッグ＆ドロップしてください';
	container.appendChild(header);

	const matchList = el('div', 'preparing-matches');
	
	const matchBox = el('div', 'match-box preparing-match');
	matchBox.setAttribute('draggable', 'true');
	
	const lbl = el('div', 'mb-label');
	const lblText = document.createElement('span');
	lblText.textContent = '準備中';
	lbl.appendChild(lblText);
	matchBox.appendChild(lbl);

	const t1 = el('div', 'mb-team');
	t1.textContent = '---';
	matchBox.appendChild(t1);
	
	const vs = el('div', 'mb-vs');
	vs.textContent = 'vs';
	matchBox.appendChild(vs);
	
	const t2 = el('div', 'mb-team');
	t2.textContent = '---';
	matchBox.appendChild(t2);

	matchBox.addEventListener('dragstart', e => {
		e.dataTransfer.setData('application/json', JSON.stringify({
			type: 'bracket',
			tNum: 'preparing_template', // これが右側にドロップされた時の合図になる
			matchId: null
		}));
	});

	matchList.appendChild(matchBox);
	container.appendChild(matchList);
	panel.appendChild(container);
}

function renderCourt() {
	const panel = document.getElementById('court-panel');
	panel.innerHTML = '';
	const colWrap = el('div', 'court-columns');
	['A', 'B', 'C'].forEach((name, ci) => {
		const col = el('div', 'court-col');
		const hdr = el('div', 'court-col-header');
		hdr.textContent = name + 'コート';
		col.appendChild(hdr);
		const colItems = S.schedule.filter(s => s.col === ci).sort((a, b) => a.order - b.order);
		colItems.forEach(sItem => {
			let m;
			if (sItem.tNum === 'preparing') {
				m = S.preparingMatches[sItem.matchId];
			} else {
				m = S.tournaments[sItem.tNum]?.matches[sItem.matchId];
			}
			col.appendChild(renderCourtItem(sItem, m));
		});
		col.addEventListener('dragover', e => e.preventDefault());
		col.addEventListener('drop', e => {
			e.preventDefault();
			let data;
			try {
				data = JSON.parse(e.dataTransfer.getData('application/json'));
			} catch {
				return;
			}
			const items = [...col.querySelectorAll('.court-item')];
			let beforeUid = null;
			for (const it of items) {
				const r = it.getBoundingClientRect();
				if (e.clientY < r.top + r.height / 2) {
					beforeUid = it.dataset.uid;
					break;
				}
			}
			
			if (data.type === 'bracket') {
				if (data.tNum === 'preparing_template') {
					// 履歴を保存
					pushHistory();
					
					// 新しいユニークなIDを生成 (例: prep_u1)
					const newMatchId = 'prep_' + newUid();
					
					// ① 実際の試合データ(実体)をオブジェクトに追加
					S.preparingMatches[newMatchId] = {
						id: newMatchId,
						label: '準備中',
						team1: null,
						team2: null,
						winner: null
					};
					
					// ② 作成した実体データを使って、コートのスケジュールに追加
					addToSchedule('preparing', newMatchId, ci, beforeUid);
				} else {
					// 通常のトーナメント戦のドロップ（既存の処理）
					addToSchedule(data.tNum, data.matchId, ci, beforeUid);
				}
			} else if (data.type === 'court') {
				moveScheduleItem(data.uid, ci, beforeUid);
			}
		});
		colWrap.appendChild(col);
	});
	panel.appendChild(colWrap);
	const saveBtn = el('button');
	saveBtn.id = 'saveBtn';
	saveBtn.textContent = 'サーバーへ保存';
	saveBtn.onclick = save;
	panel.appendChild(saveBtn);
}

function renderCourtItem(sItem, m) {
	let gameName = '';
	if (sItem.tNum === 'preparing') {
		gameName = '準備中';
	} else {
		gameName = DATA.find(d => d.tournament_number === sItem.tNum)?.game_name ?? '';
	}
	
	const itemEl = el('div', 'court-item status-' + sItem.status);
	itemEl.dataset.uid = sItem.uid;
	itemEl.setAttribute('draggable', 'true');
	
	const handle = el('span', 'handle');
	handle.textContent = '⠿';
	itemEl.appendChild(handle);
	
	const body = el('div', 'item-body');
	const lbl = el('div', 'item-label-line');
	const tNumText = sItem.tNum === 'preparing' ? '準備中' : ('T' + sItem.tNum);
	lbl.textContent = (m?.label ?? '?') + ' — ' + tNumText;
	body.appendChild(lbl);
	
	const gm = el('div', 'item-game');
	gm.textContent = gameName;
	body.appendChild(gm);
	
	const teams = el('div', 'item-teams');
	teams.textContent = (m?.team1?.team_name ?? '---') + ' vs ' + (m?.team2?.team_name ?? '---');
	body.appendChild(teams);
	
	itemEl.appendChild(body);
	
	const ctrl = el('div', 'item-controls');
	[
		['pending', '未'],
		['current', '今'],
		['done', '終']
	].forEach(([val, l]) => {
		const label = el('label');
		const radio = document.createElement('input');
		radio.type = 'radio';
		radio.name = 'st_' + sItem.uid;
		radio.value = val;
		if (sItem.status === val) radio.checked = true;
		radio.addEventListener('change', () => {
			if (radio.checked) setStatus(sItem.uid, val);
		});
		label.appendChild(radio);
		label.appendChild(document.createTextNode(l));
		ctrl.appendChild(label);
	});
	itemEl.appendChild(ctrl);
	
	const rm = el('button', 'remove-btn');
	rm.textContent = '✕';
	rm.onclick = () => removeFromSchedule(sItem.uid);
	itemEl.appendChild(rm);
	
	itemEl.addEventListener('dragstart', e => {
		e.dataTransfer.setData('application/json', JSON.stringify({
			type: 'court',
			uid: sItem.uid
		}));
	});
	
	return itemEl;
}
/* ═══════════════ INIT ═══════════════ */
function getTNums() {
	return [...new Set(DATA.map(d => d.tournament_number))].sort((a, b) => a - b);
}

function initTournament(num) {
	const bySeed = {};
	DATA.filter(d => d.tournament_number === num).forEach(t => bySeed[t.seed] = t);
	const gameName = DATA.find(d => d.tournament_number === num)?.game_name ?? '';
	return {
		bySeed,
		gameName,
		matches: {
			R1L: {
				id: 'R1L',
				label: '1回戦',
				team1: bySeed[1],
				team2: bySeed[2],
				winner: null
			},
			R1C: {
				id: 'R1C',
				label: '1回戦',
				team1: bySeed[3],
				team2: bySeed[4],
				winner: null
			},
			R1R: {
				id: 'R1R',
				label: '1回戦',
				team1: bySeed[5],
				team2: bySeed[6],
				winner: null
			},
			SF1: {
				id: 'SF1',
				label: '準決勝',
				team1: null,
				team2: null,
				winner: null
			},
			Final: {
				id: 'Final',
				label: '決勝',
				team1: null,
				team2: null,
				winner: null
			},
		}
	};
}

fetchInitialData();