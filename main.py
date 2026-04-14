from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import csv

app = Flask(__name__)

FIELDS = {
    "field_a": "data/field_a.csv",
    "field_b": "data/field_b.csv",
    "field_c": "data/field_c.csv",
}

JSON_PATH = "data/value.json"


# =========================
# JSON
# =========================
def load_values():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 欠損対策
        for k in FIELDS.keys():
            data.setdefault(k, 0)
        return data
    except FileNotFoundError:
        return {k: 0 for k in FIELDS.keys()}


def save_values(values):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(values, f, ensure_ascii=False, indent=2)


# =========================
# CSV
# =========================
def load_csv(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


# =========================
# 共通ロジック
# =========================
def get_field_data(field_name):
    game_number = load_values().get(field_name, 0)
    matches = load_csv(FIELDS[field_name])

    current = matches[game_number] if 0 <= game_number < len(matches) else None

    # NEXT
    if game_number + 1 < len(matches):
        nxt = matches[game_number + 1]
        next_match = f"{nxt['Team-A']} vs {nxt['Team-B']}"
        next_game = nxt["Game"]
    else:
        next_match = "次の試合はありません"
        next_game = None

    # GATHERING
    if game_number + 2 < len(matches):
        g = matches[game_number + 2]
        gathering = f"{g['Team-A']} vs {g['Team-B']}"
    else:
        gathering = "集合する団体はありません"

    return current, next_match, next_game, gathering


# =========================
# ダッシュボード
# =========================
@app.route("/")
def dashboard():
    matchA, next_matchA, next_gameA, gatheringA = get_field_data("field_a")
    matchB, next_matchB, next_gameB, gatheringB = get_field_data("field_b")
    matchC, next_matchC, next_gameC, gatheringC = get_field_data("field_c")

    return render_template(
        "dashboard.html",
        matchA=matchA,
        next_matchA=next_matchA,
        next_gameA=next_gameA,
        gathering_matchA=gatheringA,

        matchB=matchB,
        next_matchB=next_matchB,
        next_gameB=next_gameB,
        gathering_matchB=gatheringB,

        matchC=matchC,
        next_matchC=next_matchC,
        next_gameC=next_gameC,
        gathering_matchC=gatheringC,
    )


# =========================
# 編集画面（+/-対応）
# =========================
from flask import redirect, url_for  # ← これを先頭に追加

@app.route("/edit", methods=["GET", "POST"])
def edit():
    values = load_values()

    if request.method == "POST":
        for k in FIELDS.keys():
            values[k] = int(request.form.get(k, 0))

        save_values(values)
        return redirect(url_for("dashboard"))  # ← ここに入れる

    return render_template("edit.html", values=values)


# =========================
# 終了（開発用）
# =========================
@app.route("/exit")
def exit_app():
    os._exit(0)


# =========================
# 起動
# =========================
if __name__ == "__main__":
    app.run(debug=True)