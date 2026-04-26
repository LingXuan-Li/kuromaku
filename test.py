from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import csv

app = Flask(__name__)

DB_PATH = "data/data.db"

csv_files = [
    "data/field_a.csv",
    "data/field_b.csv",
    "data/field_c.csv"
]

# =========================
# DB共通処理
# =========================
def execute_db(fn):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return fn(conn)

# =========================
# DB初期化
# =========================
def init_db():
    def _job(conn):
        conn.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        CREATE UNIQUE INDEX IF NOT EXISTS one_current_only
        ON games(status)
        WHERE status = 'current'
        """)

        conn.commit()

    execute_db(_job)

# =========================
# CSV初期投入
# =========================
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

            with open(csv_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row_index, row in enumerate(reader):
                    cur.execute("""
                        INSERT INTO games
                        (label, team_x, team_y, game, col, row, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
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

# =========================
# 画面
# =========================
@app.route("/")
def index():
    def _job(conn):
        cur = conn.execute("""
            SELECT * FROM games
            ORDER BY col, row
        """)
        return [dict(r) for r in cur.fetchall()]

    return render_template("edit_table.html", data=execute_db(_job))

# =========================
# 保存API
# =========================
@app.route("/api/reorder", methods=["POST"])
def reorder():
    items = request.get_json()["result"]

    def _job(conn):
        conn.execute("BEGIN")

        # currentリセット
        conn.execute("UPDATE games SET status='pending' WHERE status='current'")

        for item in items:

            if item["status"] == "current":

                # 前 → done
                conn.execute("""
                    UPDATE games
                    SET status='done'
                    WHERE col=? AND row < ?
                """, (item["col"], item["row"]))

                # 後 → pending
                conn.execute("""
                    UPDATE games
                    SET status='pending'
                    WHERE col=? AND row > ?
                """, (item["col"], item["row"]))

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

# =========================
# 起動
# =========================
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    init_db()
    init_games_from_csv()

    app.run(debug=True)