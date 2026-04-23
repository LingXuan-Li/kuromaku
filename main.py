from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import sqlite3
import json
import csv
import re

app = Flask(__name__)

MESSAGE_INDEX = 0

FIELDS_TABLE = {
    "field_a": "field_a",
    "field_b": "field_b",
    "field_c": "field_c",
}

csv_files = [
    "data/field_a.csv",
    "data/field_b.csv",
    "data/field_c.csv"
]

DB_PATH = "data/values.db"

# DBヘルパー（統一コア）
def execute_db(fn):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return fn(conn)

# DB初期化
def init_db():
    def _job(conn):
        # 値テーブル
        conn.execute("""
        CREATE TABLE IF NOT EXISTS values_table (
            key TEXT PRIMARY KEY,
            value INTEGER
        )
        """)

        for k in FIELDS_TABLE.keys():
            conn.execute(
                "INSERT OR IGNORE INTO values_table (key, value) VALUES (?, ?)",
                (k, 0)
            )

        # メッセージテーブル
        conn.execute("""
        CREATE TABLE IF NOT EXISTS message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT
        )
        """)

        conn.commit()

    execute_db(_job)

# values_table
def load_values():
    def _job(conn):
        cur = conn.execute("SELECT key, value FROM values_table")
        return {k: v for k, v in cur.fetchall()}

    return execute_db(_job)


def save_values(values):
    def _job(conn):
        for k, v in values.items():
            conn.execute("""
                INSERT INTO values_table (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, (k, v))
        conn.commit()

    execute_db(_job)

# メッセージ
def save_message(data):
    messages = json.loads(data)

    def _job(conn):
        conn.execute("DELETE FROM message")

        for msg in messages:
            if msg.strip():
                conn.execute(
                    "INSERT INTO message (message) VALUES (?)",
                    (msg,)
                )

        conn.commit()

    execute_db(_job)


def load_message():
    def _job(conn):
        cur = conn.execute("SELECT message FROM message ORDER BY id ASC")
        return json.dumps([r[0] for r in cur.fetchall()], ensure_ascii=False)

    return execute_db(_job)

# CSV → DB
def load_csv_to_db(csv_files):

    def _job(conn):
        cur = conn.cursor()

        for csv_file in csv_files:

            if not os.path.exists(csv_file):
                continue

            table_name = os.path.splitext(os.path.basename(csv_file))[0]

            with open(csv_file, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)

                columns_sql = ", ".join([f'"{col}" TEXT' for col in header])

                cur.execute(f'DROP TABLE IF EXISTS "{table_name}"')
                cur.execute(f'CREATE TABLE "{table_name}" ({columns_sql})')

                placeholders = ", ".join(["?"] * len(header))
                rows = list(reader)

                cur.executemany(
                    f'INSERT INTO "{table_name}" VALUES ({placeholders})',
                    rows
                )

            conn.commit()

    execute_db(_job)

# ゲームデータ用DB取得
def get_row(table, offset):
    def _job(conn):
        cur = conn.cursor()
        cur.execute(f'''
            SELECT * FROM "{table}"
            LIMIT 1 OFFSET ?
        ''', (offset,))
        return cur.fetchone()

    return execute_db(_job)

# ゲームデータ取得ロジック
def get_field_data(field_name):

    table = FIELDS_TABLE[field_name]
    game_number = load_values().get(field_name, 0)

    current_row = get_row(table, game_number)

    if current_row:
        current = {
            "label": current_row["label"],
            "Team-X": current_row["Team-X"],
            "Team-Y": current_row["Team-Y"],
            "Game": current_row["Game"],
        }
    else:
        current = None

    nxt = get_row(table, game_number + 1)
    if nxt:
        next_match = f"{nxt['Team-X']} vs {nxt['Team-Y']}"
        next_game = nxt["Game"]
    else:
        next_match = "次の試合はありません"
        next_game = None

    g = get_row(table, game_number + 2)
    if g:
        gathering = f"{g['Team-X']} ・ {g['Team-Y']}"
    else:
        gathering = "集合する団体はありません"

    return current, next_match, next_game, gathering

def message_parse(text: str) -> str:
    # RED
    text = re.sub(r'\*\*(.*?)\*\*', r'<span style="color: red;">\1</span>', text)
    # GREEN
    text = re.sub(r'\$\$(.*?)\$\$', r'<span style="color: springgreen;">\1</span>', text)
    # ORANGE
    text = re.sub(r'\@\@(.*?)\@\@', r'<span style="color: orange;">\1</span>', text)

    return text

# main root "Information Dashboard"
@app.route("/")
def dashboard():
    matchA, _, _, _ = get_field_data("field_a")
    matchB, _, _, _ = get_field_data("field_b")
    matchC, _, _, _ = get_field_data("field_c")
    return render_template("dashboard.html", matchA=matchA, matchB=matchB, matchC=matchC)

# Dashboard API
@app.route("/api/dashboard")
def dashboard_api():
    matchA, next_matchA, next_gameA, gathering_matchA = get_field_data("field_a")
    matchB, next_matchB, next_gameB, gathering_matchB = get_field_data("field_b")
    matchC, next_matchC, next_gameC, gathering_matchC = get_field_data("field_c")
    return jsonify({
        "A": {
            "teamX": matchA['Team-X'] if matchA else None,
            "teamY": matchA['Team-Y'] if matchA else None,
            "game": matchA['Game'] if matchA else None,
            "next": next_matchA,
            "next_game": next_gameA,
            "gathering": gathering_matchA
        },
        "B": {
            "teamX": matchB['Team-X'] if matchB else None,
            "teamY": matchB['Team-Y'] if matchB else None,
            "game": matchB['Game'] if matchB else None,
            "next": next_matchB,
            "next_game": next_gameB,
            "gathering": gathering_matchB
        },
        "C": {
            "teamX": matchC['Team-X'] if matchC else None,
            "teamY": matchC['Team-Y'] if matchC else None,
            "game": matchC['Game'] if matchC else None,
            "next": next_matchC,
            "next_game": next_gameC,
            "gathering": gathering_matchC
        }
    })

# Info API
@app.route("/api/info")
def get_info():
    global MESSAGE_INDEX
    messages = json.loads(load_message())
    if not messages:
        message = ["塩分補給・水分補給を忘れずに！"]
    else:
        message = messages[MESSAGE_INDEX]
        message = message_parse(message)

    MESSAGE_INDEX = (MESSAGE_INDEX + 1) % len(messages)
    return jsonify({
        "message": message
    })

# "Dashboard Editor"
@app.route("/edit", methods=["GET", "POST"])
def edit():
    values = load_values()

    matchA, next_matchA, next_gameA, gatheringA = get_field_data("field_a")
    matchB, next_matchB, next_gameB, gatheringB = get_field_data("field_b")
    matchC, next_matchC, next_gameC, gatheringC = get_field_data("field_c")

    if request.method == "POST":
        data = request.get_json(silent=True) or {}

        for k in FIELDS_TABLE.keys():
            try:
                values[k] = int(data.get(k, 0))
            except ValueError:
                values[k] = 0

        save_values(values)
        return jsonify({"status": "ok"})

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

    table = FIELDS_TABLE[field_name]

    current_row = get_row(table, game_number)

    if current_row:
        current = {
            "label": current_row["label"],
            "Team-X": current_row["Team-X"],
            "Team-Y": current_row["Team-Y"],
            "Game": current_row["Game"],
        }
    else:
        current = None

    # NOW
    if current:
        match_text = f"{current['Team-X']} vs {current['Team-Y']} ({current['Game']})"
    else:
        match_text = "試合データなし"

    nxt = get_row(table, game_number + 1)
    if nxt:
        next_match = f"{nxt['Team-X']} vs {nxt['Team-Y']}"
        next_game = nxt["Game"]
    else:
        next_match = "次の試合はありません"
        next_game = None

    g = get_row(table, game_number + 2)
    if g:
        gathering = f"{g['Team-X']} ・ {g['Team-Y']}"
    else:
        gathering = "集合する団体はありません"

    return match_text, next_game, gathering

@app.route("/api/preview", methods=["POST"])
def api_preview():
    data = request.get_json()
    results = {}

    for field in FIELDS_TABLE:
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
    load_csv_to_db(csv_files)
    app.run(debug=True)