// 状態管理
let isDirty = false;

function setDirty() {
  if (!isDirty) {
    isDirty = true;
    document.getElementById("dirtyBanner").style.display = "block";
  }
}

function clearDirty() {
  isDirty = false;
  document.getElementById("dirtyBanner").style.display = "none";
}

// Undo
let historyStack = [];

function snapshot() {
  const data = [];
  document.querySelectorAll(".list").forEach(col => {
    const colIndex = col.dataset.col;
    [...col.querySelectorAll(".cell")].forEach((el, rowIndex) => {
      data.push({
        id: el.dataset.id,
        col: colIndex,
        row: rowIndex,
        status: el.querySelector("input:checked")?.value || "pending"
      });
    });
  });
  return JSON.stringify(data);
}

function applySnapshot(json) {
  const data = JSON.parse(json);

  const grouped = {};
  data.forEach(d => {
    if (!grouped[d.col]) grouped[d.col] = [];
    grouped[d.col].push(d);
  });

  Object.keys(grouped).forEach(col => {
    const container = document.getElementById("col" + col);
    const sorted = grouped[col].sort((a,b)=>a.row-b.row);

    sorted.forEach(d => {
      const el = document.querySelector(`.cell[data-id="${d.id}"]`);
      if (el) container.appendChild(el);
      const radio = el.querySelector(`input[value="${d.status}"]`);
      if (radio) radio.checked = true;
    });

    recalcColumn(container);
  });
}

function saveHistory() {
  historyStack.push(snapshot());
  if (historyStack.length > 100) historyStack.shift();
  updateUndoUI();
}

function undo() {
  if (historyStack.length <= 1) return;

  historyStack.pop();
  applySnapshot(historyStack[historyStack.length - 1]);

  updateUndoUI();
  setDirty();
}

// Undo UI更新
function updateUndoUI() {
  const btn = document.getElementById("undoBtn");
  const info = document.getElementById("historyInfo");

  btn.disabled = historyStack.length <= 1;
  info.textContent = `履歴: ${historyStack.length}`;
}

// current制御（列単位）
function enforceSingleCurrent(selectedCell) {
  const col = selectedCell.closest(".list");
  col.querySelectorAll(".cell").forEach(c => {
    if (c !== selectedCell) {
      const r = c.querySelector("input[value='current']");
      if (r) r.checked = false;
    }
  });
}

// 列再計算（クラス更新＋未選択セルは pending）
function recalcColumn(col) {
  const cells = [...col.querySelectorAll(".cell")];
  let currentIndex = cells.findIndex(c => c.querySelector("input[value='current']")?.checked);

  cells.forEach((c, i) => {
    c.classList.remove("pending","current","done");

    // 未選択のセルは pending に
    let radio = c.querySelector("input:checked");
    if (!radio) {
      radio = c.querySelector("input[value='pending']");
      radio.checked = true;
    }

    if (currentIndex === -1) {
      // current がない場合はラジオ状態を反映
      c.classList.add(c.querySelector("input:checked").value);
    } else {
      // current がある場合、前は done、current は current、後ろは pending
      if (i < currentIndex) {
        c.classList.add("done");
        c.querySelector("input[value='done']").checked = true;
      } else if (i === currentIndex) {
        c.classList.add("current");
        c.querySelector("input[value='current']").checked = true;
      } else {
        c.classList.add("pending");
        c.querySelector("input[value='pending']").checked = true;
      }
    }
  });
}

// Drag
["col0","col1","col2"].forEach(id => {
  new Sortable(document.getElementById(id), {
    group: "shared",
    handle: ".handle",
    animation: 150,
    onEnd: function () {
      document.querySelectorAll(".list").forEach(recalcColumn);
      saveHistory();
      setDirty();
    }
  });
});

// radio変更
document.querySelectorAll("input[type=radio]").forEach(input => {
  input.addEventListener("change", e => {
    const cell = e.target.closest(".cell");
    const col = cell.closest(".list");

    if (e.target.value === "current") {
      enforceSingleCurrent(cell);
    }

    recalcColumn(col);
    saveHistory();
    setDirty();
  });
});

// 保存
function save() {
  const result = [];

  document.querySelectorAll(".list").forEach(col => {
    const colIndex = col.dataset.col;
    [...col.querySelectorAll(".cell")].forEach((el, rowIndex) => {
      result.push({
        id: parseInt(el.dataset.id),
        col: parseInt(colIndex),
        row: rowIndex,
        status: el.querySelector("input:checked").value
      });
    });
  });

  console.log("送信データ:", result);

  fetch("/api/reorder", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({result})
  })
  .then(res => {
    if (!res.ok) throw new Error();
    clearDirty();
    alert("保存しました");
  })
  .catch(() => alert("保存失敗"));
}

// 初期化
window.addEventListener("load", () => {
  document.querySelectorAll(".list").forEach(recalcColumn);
  saveHistory();
  updateUndoUI();
});