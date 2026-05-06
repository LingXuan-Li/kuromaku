from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import csv
import json
import re
import peewee

app = Flask(__name__)

PORT = 8520
DEBUG = True

DB_PATH = "data/data.db"
db = peewee.SqliteDatabase(DB_PATH)

CSV_PATH = "data/tournaments.csv"

# DB共通処理
class BaseModel(peewee.Model):
    class Meta:
        database = db

class Tournament(BaseModel):
    # team_name,game_name,tournament_number,seed
    team_name = peewee.CharField()
    game_name = peewee.TextField()
    tournament_number = peewee.IntegerField()
    seed = peewee.IntegerField()

class TournamentProgress(BaseModel):
    tournament_number = peewee.IntegerField()
    match_id = peewee.CharField() # R1L, SemiL, Finalなど
    winner_seed = peewee.IntegerField(null=True)

class Message(BaseModel):
    message = peewee.TextField()

    class Meta:
        table_name = "message"

class DashboardData(BaseModel):
    tournament_number = peewee.IntegerField()
    match_id = peewee.CharField()
    field = peewee.CharField()
    label = peewee.CharField()
    team_x = peewee.CharField()
    team_y = peewee.CharField()
    game = peewee.CharField()
    col = peewee.IntegerField()
    row = peewee.IntegerField()
    status = peewee.CharField()

    class Meta:
        table_name = "dashboard_data"

# DB初期化
def init_db():
    with db:
        db.create_tables([Tournament,TournamentProgress, Message, DashboardData])

# CSV初期投入
def init_games_from_csv():
    if Tournament.select().count() > 0:
        return

    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Tournament.create(
                team_name=row['team_name'],
                game_name=row['game_name'],
                tournament_number=int(row['tournament_number']),
                seed=int(row['seed'])
            )

# ゲーム取得
def get_games(col_index):
    games = (DashboardData
             .select()
             .where(DashboardData.col == col_index)
             .order_by(DashboardData.row.asc()))
    return [dict(
        team_x=g.team_x,
        team_y=g.team_y,
        game=g.game
    ) for g in games]

# ダッシュボード
@app.route("/")
def index():
    return render_template("dashboard.html")

def build_for_col(col_index):
    dashboard_data = get_games(col_index)
    if not dashboard_data:
        return {
            "teamX": None,
            "teamY": None,
            "game": None,
            "next": None,
            "next_game": None,
            "gathering": None
        }

    # status は使わないので、単純に最初のゲームを current とする
    current = dashboard_data[0]
    idx = 0

    nxt = dashboard_data[idx + 1] if idx + 1 < len(dashboard_data) else None
    g = dashboard_data[idx + 2] if idx + 2 < len(dashboard_data) else None

    return {
        "teamX": current.get("team_x"),
        "teamY": current.get("team_y"),
        "game": current.get("game"),
        "next": f'{nxt.get("team_x")} vs {nxt.get("team_y")}' if nxt else None,
        "next_game": nxt.get("game") if nxt else None,
        "gathering": f'{g.get("team_x")} ・ {g.get("team_y")}' if g else None
    }

@app.route("/api/dashboard")
def api_dashboard():
    col_map = {0: "A", 1: "B", 2: "C"}

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
    return render_template("tournament.html")

# 旧 /edit ルートはリダイレクトに変更
@app.route("/edit", methods=["GET", "POST"])
def edit():
    return redirect(url_for('table_editor'))

def model_to_dict(model_instance):
    # インスタンスが持っているフィールド名と値を取り出して辞書にする
    return {field.name: getattr(model_instance, field.name) 
            for field in model_instance._meta.sorted_fields}

@app.route('/api/tournaments_data', methods=['GET'])
def get_tournaments():
    teams = [model_to_dict(t) for t in Tournament.select()]
    progress = [model_to_dict(p) for p in TournamentProgress.select()]
    schedule = [model_to_dict(s) for s in DashboardData.select()] # スケジュールも返す
    return jsonify({"teams": teams, "progress": progress, "schedule": schedule})

# 試合スケジュールの保存
@app.route('/api/save_match', methods=['POST'])
def save_matches():
    data = request.json
    try:
        with db.atomic():
            # 1. コートスケジュールの保存
            DashboardData.delete().execute()
            if data.get('schedule'):
                DashboardData.insert_many(data['schedule']).execute()
            
            # 2. トーナメント進行（勝敗）の保存
            TournamentProgress.delete().execute()
            if data.get('progress'):
                TournamentProgress.insert_many(data['progress']).execute()
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# メッセージ機能
MESSAGE_INDEX = 0
def save_message(data):
    messages = json.loads(data)
    with db.atomic():
        Message.delete().execute()
        for msg in messages:
            Message.create(message=msg)


def load_message():
    messages = (Message
                .select()
                .order_by(Message.id.asc()))
    return json.dumps([m.message for m in messages], ensure_ascii=False)

def message_parse(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'<span style="color: #f01000;">\1</span>', text)
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
    tonaments = Tournament.select().order_by(Tournament.tournament_number.asc())
    print("Tournaments:", [t.__data__ for t in tonaments])
    print("Message:", message)
    return render_template("check.html", message=message, tournaments=tonaments)

# アプリ終了API（テスト用）
@app.route("/exit")
def exit_app():
    os._exit(0)

# 起動
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    init_db()
    init_games_from_csv()
    print(f"Starting server on port {PORT}...")
    app.run(debug=DEBUG, port=PORT)