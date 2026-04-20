from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import sqlite3
import json
import csv
import re

app = Flask(__name__)

FIELDS_CSV = {
    "field_a": "data/field_a.csv",
    "field_b": "data/field_b.csv",
    "field_c": "data/field_c.csv",
}

FIELDS_DB = {
    "field_a": int,
    "field_b": int,
    "field_c": int
}

DB_PATH = "data/values.db"

# SQLite
def get_conn():
    return sqlite3.connect(DB_PATH)

# DB初期化
def init_db():
    with get_conn() as conn:
        # 値保存用テーブル
        conn.execute("""
        CREATE TABLE IF NOT EXISTS values_table (
            key TEXT PRIMARY KEY,
            value INTEGER
        )
        """)
        # 初期値入力
        for k in FIELDS_DB.keys():
            conn.execute(
                "INSERT OR IGNORE INTO values_table (key, value) VALUES (?, ?)",
                (k, 0)
            )
        conn.commit()

        # メッセージ用テーブル
        conn.execute("""
        CREATE TABLE IF NOT EXISTS message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT
        )
        """)
        conn.commit()

# メッセージ保存
def save_message(data):
    messages = json.loads(data)

    with get_conn() as conn:
        # 既存データ削除
        conn.execute("DELETE FROM message")

        # 新規データ保存
        for msg in messages:
            if not msg.strip():
                continue
            conn.execute(
                "INSERT INTO message (message) VALUES (?)",
                (msg,)
            )

        conn.commit()

def load_message():
    with get_conn() as conn:
        cursor = conn.execute(
            "SELECT message FROM message ORDER BY id ASC"
        )
        rows = cursor.fetchall()

        messages = [row[0] for row in rows]
        return json.dumps(messages, ensure_ascii=False)

def load_values():
    with get_conn() as conn:
        cursor = conn.execute("SELECT key, value FROM values_table")
        return {k: v for k, v in cursor.fetchall()}

def save_values(values):
    with get_conn() as conn:
        for k, v in values.items():
            conn.execute(
                """
                INSERT INTO values_table (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
                """,
                (k, v)
            )
        conn.commit()

# CSV
def load_csv(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []

# フィールドごとのデータ取得
def get_field_data(field_name):
    game_number = load_values().get(field_name, 0)
    matches = load_csv(FIELDS_CSV[field_name])

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
        gathering = f"{g['Team-A']} ・ {g['Team-B']}"
    else:
        gathering = "集合する団体はありません"

    return current, next_match, next_game, gathering

def message_parse(text: str) -> str:
    # RED
    text = re.sub(r'\*(.*?)\*', r'<span style="color: red;">\1</span>', text)

    # GREEN
    text = re.sub(r'#(.*?)#', r'<span style="color: green;">\1</span>', text)

    # ORANGE
    text = re.sub(r'\@(.*?)\@', r'<span style="color: orange;">\1</span>', text)

    return text

# main root "Information Dashboard"
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
        gathering_matchC=gatheringC
    )

# "Dashboard Editor"
@app.route("/edit", methods=["GET", "POST"])
def edit():
    values = load_values()

    matchA, next_matchA, next_gameA, gatheringA = get_field_data("field_a")
    matchB, next_matchB, next_gameB, gatheringB = get_field_data("field_b")
    matchC, next_matchC, next_gameC, gatheringC = get_field_data("field_c")

    if request.method == "POST":
        print("FORM:", request.form)
        for k in FIELDS_CSV.keys():
            values[k] = int(request.form.get(k, 0))

        save_values(values)
        return redirect(url_for("edit"))

    return render_template(
        "edit.html",
        values=values,
                           
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
        gathering_matchC=gatheringC
        )

# "Message Editor"
@app.route("/message")
def message():
    message = load_message()
    return render_template("message.html", message=message)

# Message Preview API
@app.route("/api/message_preview", methods=["POST"])
def preview():
    data = request.json
    text = data.get("text", "")
    html = message_parse(text)
    return jsonify({"html": html})

@app.route("/api/message_save", methods=["POST"])
def save():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    lines = text.splitlines()
    cleaned = [line.strip() for line in lines if line.strip()]

    save_message(json.dumps(cleaned, ensure_ascii=False))

    return jsonify({"status": "ok"})

@app.route("/api/message_load", methods=["GET"])
def load():
    data = load_message()
    return jsonify({"text": "\n".join(json.loads(data))})

# Preview Field Data API
def field_data_api(field_name, game_number=None):
    if game_number is None:
        game_number = load_values().get(field_name, 0)

    matches = load_csv(FIELDS_CSV[field_name])

    current = matches[game_number] if 0 <= game_number < len(matches) else None

    # NOW
    if current:
        match_text = f"{current['Team-A']} vs {current['Team-B']} ({current['Game']})"
    else:
        match_text = "試合データなし"

    # NEXT
    if game_number + 1 < len(matches):
        nxt = matches[game_number + 1]
        next_match = f"{nxt['Team-A']} vs {nxt['Team-B']} ({nxt['Game']})"
    else:
        next_match = "次の試合はありません"

    # GATHERING
    if game_number + 2 < len(matches):
        g = matches[game_number + 2]
        gathering = f"{g['Team-A']} ・ {g['Team-B']} ({g['Game']})"
    else:
        gathering = "集合する団体はありません"

    return match_text, next_match, gathering

@app.route("/api/preview", methods=["POST"])
def api_preview():
    data = request.get_json()
    results = {}

    for field in FIELDS_CSV:
        game_number = int(data.get(field, 0))

        match_text, next_match, gathering = field_data_api(field, game_number)

        results[field] = {
            "match": match_text,
            "next_match": next_match,
            "gathering": gathering
        }

    return jsonify(results)

# 開発用
@app.route("/exit")
def exit_app():
    os._exit(0)

@app.route("/check")
def check():
    message = load_message()
    html = f'<!DOCTYPE html>\n<html lang="ja">\n<head>\n<meta charset="UTF-8">\n</head>\n<body>\n<h1>Check API</h1>\n<p>{message}</p>\n</body>\n</html>'
    return html

if __name__ == "__main__":
    init_db()
    app.run(debug=True)