import sqlite3
import csv
import os
import json

DB_PATH = "data/data.db"

csv_files = [
    "data/field_a.csv",
    "data/field_b.csv",
    "data/field_c.csv"
]

FIELDS_TABLE = {
    "field_a": "field_a",
    "field_b": "field_b",
    "field_c": "field_c",
}

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
                print(f"❌ 見つかりません: {csv_file}")
                continue

            table_name = os.path.splitext(os.path.basename(csv_file))[0]
            print(f"\n📥 処理中: {csv_file} → テーブル {table_name}")

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
            print(f"✅ 保存完了: {table_name}")

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

def main():
    print("===== DB初期化 =====")
    init_db()

    print("\n===== CSV読み込み =====")
    load_csv_to_db(csv_files)

    print("\n===== values確認 =====")
    values = load_values()
    print(values)

    print("\n===== メッセージ保存テスト =====")
    sample_messages = json.dumps([
        "テスト1",
        "テスト2",
        "テスト3"
    ], ensure_ascii=False)

    save_message(sample_messages)
    print(load_message())

    print("\n===== fieldデータ取得テスト =====")
    for field in FIELDS_TABLE.keys():
        print(f"\n--- {field} ---")
        current, next_match, next_game, gathering = get_field_data(field)

        print("current:", current)
        print("next_match:", next_match)
        print("next_game:", next_game)
        print("gathering:", gathering)


if __name__ == "__main__":
    main()