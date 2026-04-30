from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
import csv
import json
import re

app = Flask(__name__)

PORT = 8520
DEBUG = True

DB_PATH = "data/data.db"

csv_files = [
    "data/field_a.csv",
    "data/field_b.csv",
    "data/field_c.csv"
]

# DB共通処理
def execute_db(fn):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return fn(conn)

# DB初期化
def init_db():
    def _job(conn):
        conn.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field TEXT,
            label TEXT,
            team_x TEXT,
            team_y TEXT,
            game TEXT,
            col INTEGER,
            row INTEGER,
            status TEXT DEFAULT 'pending'
        )
        """)
        conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS one_current_per_col
        ON games(col, status)
        WHERE status = 'current';
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT
        )
        """)
        conn.commit()
    execute_db(_job)

# CSV初期投入
def init_games_from_csv():
    def _job(conn):
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM games")
        if cur.fetchone()[0] > 0:
            return
        col_index = 0
        for csv_file in csv_files:
            if not os.path.exists(csv_file):
                continue
            field_name = os.path.splitext(os.path.basename(csv_file))[0]
            with open(csv_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row_index, row in enumerate(reader):
                    cur.execute("""
                        INSERT INTO games
                        (field, label, team_x, team_y, game, col, row, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        field_name,
                        row.get("label", ""),
                        row.get("Team-X", ""),
                        row.get("Team-Y", ""),
                        row.get("Game", ""),
                        col_index,
                        row_index,
                        "pending"
                    ))
            col_index += 1
        conn.commit()
    execute_db(_job)

# ゲーム取得
def get_games(col_index):
    def _job(conn):
        cur = conn.execute("""
            SELECT * FROM games
            WHERE col=?
            ORDER BY row
        """, (col_index,))
        return [dict(r) for r in cur.fetchall()]
    return execute_db(_job)

# ダッシュボード
@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/api/dashboard")
def api_dashboard():
    col_map = {0: "A", 1: "B", 2: "C"}

    def build_for_col(col_index):
        games = get_games(col_index)  # col で取得する関数に変更
        if not games:
            return {
                "teamX": None,
                "teamY": None,
                "game": None,
                "next": None,
                "next_game": None,
                "gathering": None
            }

        # current を列内で探す
        current = next((g for g in games if g["status"] == "current"), None)
        idx = games.index(current) if current else 0

        nxt = games[idx + 1] if idx + 1 < len(games) else None
        g = games[idx + 2] if idx + 2 < len(games) else None

        return {
            "teamX": current["team_x"] if current else None,
            "teamY": current["team_y"] if current else None,
            "game": current["game"] if current else None,
            "next": f'{nxt["team_x"]} vs {nxt["team_y"]}' if nxt else None,
            "next_game": nxt["game"] if nxt else None,
            "gathering": f'{g["team_x"]} ・ {g["team_y"]}' if g else None
        }

    # 各列のデータを返す
    dashboard = {}
    for col_index, col_name in col_map.items():
        dashboard[col_name] = build_for_col(col_index)

    return jsonify(dashboard)

@app.route("/api/info")
def api_info():
    global MESSAGE_INDEX

    messages = json.loads(load_message())

    if not messages:
        messages = ["塩分・水分補給を忘れずに！"]

    msg = messages[MESSAGE_INDEX]
    msg = message_parse(msg)

    MESSAGE_INDEX = (MESSAGE_INDEX + 1) % len(messages)

    return jsonify({
        "message": msg
    })

# テーブルエディタ
@app.route("/table_editor")
def table_editor():
    def _job(conn):
        cur = conn.execute("""
            SELECT * FROM games
            ORDER BY col, row
        """)
        return [dict(r) for r in cur.fetchall()]

    return render_template("edit_table.html", data=execute_db(_job))

# 旧 /edit ルートはリダイレクトに変更
@app.route("/edit", methods=["GET", "POST"])
def edit():
    '''
    # 値初期化
    def load_values():
        default_values = {"field_a": 0, "field_b": 0, "field_c": 0}
        # DBから現在の試合番号をロード
        def _job(conn):
            cur = conn.execute("SELECT key, value FROM values_table")
            return {k: v for k, v in cur.fetchall()}
        try:
            values_from_db = execute_db(_job)
            default_values.update(values_from_db)
        except:
            pass
        return default_values

    values = load_values()

    # current games
    def load_current():
        cur = {}
        for field in ["field_a", "field_b", "field_c"]:
            games = get_games(field)
            cur[field] = next((g for g in games if g["status"]=="current"), None)
        return cur
    current_games = load_current()

    if request.method == "POST":
        items = request.get_json(silent=True) or []
        def _job(conn):
            conn.execute("UPDATE games SET status='pending' WHERE status='current'")
            for item in items:
                if item.get("status") == "current":
                    conn.execute("""
                        UPDATE games SET status='done'
                        WHERE field=? AND col=? AND row < ?
                    """, (item["field"], item["col"], item["row"]))
                    conn.execute("""
                        UPDATE games SET status='pending'
                        WHERE field=? AND col=? AND row > ?
                    """, (item["field"], item["col"], item["row"]))
                conn.execute("""
                    UPDATE games SET col=?, row=?, status=?, field=?
                    WHERE id=?
                """, (
                    item["col"],
                    item["row"],
                    item["status"],
                    item["field"],
                    item["id"]
                ))
            conn.commit()
        execute_db(_job)
        return jsonify({"status": "ok"})

    return render_template("edit.html",
                           values=values,
                           current_games=current_games)
    '''
    return redirect(url_for('table_editor'))

# reorder API
@app.route("/api/reorder", methods=["POST"])
def reorder():
    items = request.get_json()["result"]
    print("Received items:", items)

    def _job(conn):
        conn.execute("BEGIN")

        # 型を保証
        for item in items:
            item["col"] = int(item["col"])
            item["row"] = int(item["row"])
            item["id"] = int(item["id"])

        # 列ごとの current の位置を取得
        current_map = {}
        for item in items:
            if item["status"] == "current":
                current_map[item["col"]] = item["row"]

        # 列単位で前の試合を done、後ろを pending に
        for col, row in current_map.items():
            conn.execute("""
                UPDATE games
                SET status='done'
                WHERE col=? AND row < ?
            """, (col, row))

            conn.execute("""
                UPDATE games
                SET status='pending'
                WHERE col=? AND row > ?
            """, (col, row))

        # すべての行を更新
        for item in items:
            conn.execute("""
                UPDATE games
                SET col=?, row=?, status=?
                WHERE id=?
            """, (
                item["col"],
                item["row"],
                item["status"],
                item["id"]
            ))

        conn.commit()

    execute_db(_job)
    return jsonify({"status": "ok"})

# メッセージ機能
MESSAGE_INDEX = 0
def save_message(data):
    messages = json.loads(data)
    def _job(conn):
        conn.execute("DELETE FROM message")
        for msg in messages:
            if msg.strip():
                conn.execute("INSERT INTO message (message) VALUES (?)", (msg,))
        conn.commit()
    execute_db(_job)

def load_message():
    def _job(conn):
        cur = conn.execute("SELECT message FROM message ORDER BY id ASC")
        return json.dumps([r[0] for r in cur.fetchall()], ensure_ascii=False)
    return execute_db(_job)

def message_parse(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'<span style="color: red;">\1</span>', text)
    text = re.sub(r'\$\$(.*?)\$\$', r'<span style="color: #61c802;">\1</span>', text)
    text = re.sub(r'\@\@(.*?)\@\@', r'<span style="color: orange;">\1</span>', text)
    return text

@app.route("/api/message_save", methods=["POST"])
def message_save():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    lines = text.splitlines()
    cleaned = [line.strip() for line in lines if line.strip()]
    save_message(json.dumps(cleaned, ensure_ascii=False))
    return jsonify({"status": "ok"})

@app.route("/api/message_load", methods=["GET"])
def message_load():
    data = load_message()
    return jsonify({"text": "\n".join(json.loads(data))})

@app.route("/api/message_preview", methods=["POST"])
def message_preview():
    data = request.json
    text = data.get("text", "")
    html = message_parse(text)
    return jsonify({"html": html})

@app.route("/message")
def message():
    message = load_message()
    return render_template("message.html", message=message)

@app.route("/admin")
def admin():
    routes = sorted([f"{rule.endpoint} → {rule.rule}" for rule in app.url_map.iter_rules()])
    return render_template("admin.html", routes=routes)

@app.route("/help")
def helper():
    return redirect(url_for("admin"))

# TEST用のチェックAPI（ブラウザで動作確認するためのもの）
@app.route("/check")
def check():
    message = load_message()
    return f"<h1>Check API</h1><p>{message}</p>"

# アプリ終了API（テスト用）
@app.route("/exit")
def exit_app():
    os._exit(0)

# 起動
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    init_db()
    init_games_from_csv()
    app.run(debug=DEBUG, port=PORT)