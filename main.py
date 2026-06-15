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

GAME_PATH = "data/tournaments.csv"
CULTURE_CLUB_PATH = "data/culture_club.csv"
SPORTS_CLUB_PATH = "data/sports_club.csv"
CLASS_RELAY_PATH = "data/class_relay.csv"

MESSAGE_INDEX = 0

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

class CultureClub(BaseModel):
    team_name = peewee.CharField()
    first = peewee.CharField()
    second = peewee.CharField()
    third = peewee.CharField()
    fourth = peewee.CharField()
    fifth = peewee.CharField()
    sixth = peewee.CharField()

    class Meta:
        table_name = "culture_club"

class SportsClub(BaseModel):
    team_name = peewee.CharField()
    first = peewee.CharField()
    second = peewee.CharField()
    third = peewee.CharField()
    fourth = peewee.CharField()
    fifth = peewee.CharField()
    sixth = peewee.CharField()

    class Meta:
        table_name = "sports_club"

class Relay(BaseModel):
    team_name = peewee.CharField()
    first = peewee.CharField()
    second = peewee.CharField()
    third = peewee.CharField()
    fourth = peewee.CharField()
    fifth = peewee.CharField()
    sixth = peewee.CharField()

    class Meta:
        table_name = "relay"

class Category(BaseModel):
    category = peewee.CharField()
    category_name = peewee.TextField()

    class Meta:
        table_name = "category"

class ClassRelay(BaseModel):
    team_name = peewee.CharField()
    first = peewee.CharField()
    second = peewee.CharField()
    third = peewee.CharField()
    fourth = peewee.CharField()
    fifth = peewee.CharField()
    sixth = peewee.CharField()
    seventh = peewee.CharField()
    eighth = peewee.CharField()
    ninth = peewee.CharField()
    tenth = peewee.CharField()

    class Meta:
        table_name = "class_relay"


class PageStyle(BaseModel):
    style = peewee.CharField()
    style_name = peewee.TextField()

    class Meta:
        table_name = "page_style"

MODELS = [
    Tournament,
    TournamentProgress,
    Message,
    DashboardData,
    CultureClub,
    SportsClub,
    Relay,
    Category,
    ClassRelay,
    PageStyle
]

# DB初期化
def init_db():
    with db:
        db.create_tables(MODELS)

# CSV初期投入
def init_games_from_csv():
    if Tournament.select().count() > 0:
        return

    with open(GAME_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Tournament.create(
                team_name=row['team_name'],
                game_name=row['game_name'],
                tournament_number=int(row['tournament_number']),
                seed=int(row['seed'])
            )

def init_relay_from_csv():
    if CultureClub.select().count() > 0 and SportsClub.select().count() > 0:
        return

    with open(CULTURE_CLUB_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            CultureClub.create(
                team_name=row['team_name'],
                first=row['first'],
                second=row['second'],
                third=row['third'],
                fourth=row['fourth'],
                fifth=row['fifth'],
                sixth=row['sixth']
            )

    with open(SPORTS_CLUB_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            SportsClub.create(
                team_name=row['team_name'],
                first=row['first'],
                second=row['second'],
                third=row['third'],
                fourth=row['fourth'],
                fifth=row['fifth'],
                sixth=row['sixth']
            )

    with open(CLASS_RELAY_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ClassRelay.create(
                team_name=row['team_name'],
                first=row['first'],
                second=row['second'],
                third=row['third'],
                fourth=row['fourth'],
                fifth=row['fifth'],
                sixth=row['sixth'],
                seventh=row['seventh'],
                eighth=row['eighth'],
                ninth=row['ninth'],
                tenth=row['tenth']
            )

def init_category():
    if not Category.select().where(Category.id == 1).exists():
        Category.create(
            id=1,
            category="culture",
            category_name="予選 文化部"
        )

def init_page_style():
    if not PageStyle.select().where(PageStyle.id == 1).exists():
        PageStyle.create(
            id=1,
            style="tournament",
            style_name="トーナメント"
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
        game=g.game,
        status=g.status
    ) for g in games]

# メッセージ機能
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
    text = re.sub(r'\@\@(.*?)\@\@', r'<span style="color: #666ae1;">\1</span>', text)

    text = f'<span style="color: orange;">{text}</span>'
    return text

# ダッシュボード
@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/api/page_style")
def page_style():
    style = PageStyle.get_by_id(1)
    return jsonify({ "style": style.style })

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

    current_idx = next(
        (i for i, g in enumerate(dashboard_data) if g.get("status") == "current"),
        None
    )

    if current_idx is None:
        current = None
        team_x = None
        team_y = None
        game = None
        nxt = dashboard_data[0] if len(dashboard_data) > 0 else None
        g = dashboard_data[1] if len(dashboard_data) > 1 else None

    else:
        current = dashboard_data[current_idx]
        team_x = current.get("team_x")
        team_y = current.get("team_y")
        game = current.get("game")

        nxt = dashboard_data[current_idx + 1] if current_idx + 1 < len(dashboard_data) else None
        g = dashboard_data[current_idx + 2] if current_idx + 2 < len(dashboard_data) else None

    return {
        "teamX": team_x,
        "teamY": team_y,
        "game": game,
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

# トーナメントエディタ
@app.route("/tournaments_editor")
def tournaments_editor():
    return render_template("tournament.html")

# /edit ルートはトーナメントエディタエディタとリレーエディタ用のハブページに変更
@app.route("/edit")
def edit():
    return render_template("edit.html")

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

# リレーエディタ
@app.route("/relay_editor")
def relay_editor():
    # print("Culture Club:", [c.__data__ for c in culture_club])
    # print("Sports Club:", [s.__data__ for s in sports_club])
    return render_template("relay.html")

@app.route("/api/culture_load", methods=["GET"])
def culture_load():
    culture = CultureClub.select().order_by(CultureClub.id.asc())
    return jsonify([model_to_dict(c) for c in culture])

@app.route("/api/sports_load", methods=["GET"])
def sports_load():
    sports = SportsClub.select().order_by(SportsClub.id.asc())
    return jsonify([model_to_dict(s) for s in sports])

@app.route("/api/relay_load", methods=["GET"])
def relay_load():
    relay = Relay.select().order_by(Relay.id.asc())
    return jsonify([model_to_dict(r) for r in relay])

@app.route("/api/culture_save", methods=["POST"])
def culture_save():
    data = request.get_json(silent=True) or {}

    with db.atomic():
        CultureClub.delete().execute()

        items = data.get("items", [])

        if items:
            CultureClub.insert_many([
                {
                    "team_name": item.get("team_name", ""),
                    "first": item.get("first", ""),
                    "second": item.get("second", ""),
                    "third": item.get("third", ""),
                    "fourth": item.get("fourth", ""),
                    "fifth": item.get("fifth", ""),
                    "sixth": item.get("sixth", "")
                }
                for item in items
            ]).execute()

    return jsonify({"status": "ok"})

@app.route("/api/sports_save", methods=["POST"])
def sports_save():
    data = request.get_json(silent=True) or {}
    # print(data)

    with db.atomic():
        SportsClub.delete().execute()

        items = data.get("items", [])

        if items:
            SportsClub.insert_many([
                {
                    "team_name": item.get("team_name", ""),
                    "first": item.get("first", ""),
                    "second": item.get("second", ""),
                    "third": item.get("third", ""),
                    "fourth": item.get("fourth", ""),
                    "fifth": item.get("fifth", ""),
                    "sixth": item.get("sixth", "")
                }
                for item in items
            ]).execute()

    return jsonify({"status": "ok"})

@app.route("/api/relay_save", methods=["POST"])
def relay_save():
    data = request.get_json(silent=True) or {}
    category = data.get("category")

    if category == "culture":
        model = CultureClub

    elif category == "sports":
        model = SportsClub

    elif category == "relay":
        model = Relay

    else:
        return jsonify({
            "status": "error",
            "message": "Invalid category"
        }), 400

    with db.atomic():
        model.delete().execute()

        items = data.get("items", [])

        if items:
            model.insert_many([
                {
                    "team_name": item.get("team_name", ""),
                    "first": item.get("first", ""),
                    "second": item.get("second", ""),
                    "third": item.get("third", ""),
                    "fourth": item.get("fourth", ""),
                    "fifth": item.get("fifth", ""),
                    "sixth": item.get("sixth", "")
                }
                for item in items
            ]).execute()

    return jsonify({"status": "ok"})

@app.route("/api/category_save", methods=["POST"])
def category_save():
    data = request.get_json(silent=True) or {}
    
    with db.atomic():
        category = data.get("category", "")
        if category == "culture":
            category_name = "予選 文化部"
        elif category == "sports":
            category_name = "予選 運動部"
        elif category == "relay":
            category_name = "本戦"
        # elif category == "hidden":
        #     category_name = "非表示"
        else:
            category_name = ""

        Category.update(category=category).where(Category.id == 1).execute()
        Category.update(category_name=category_name).where(Category.id == 1).execute()

    return jsonify({"status": "ok"})

@app.route("/api/category_load", methods=["GET"])
def category_load():

    category = Category.get_by_id(1)
    # print("Current Category:", category.category, category.category_name)

    return jsonify({
        "category": category.category,
        "category_name": category.category_name
    })

@app.route("/api/relay_data", methods=["GET"])
def relay_data():
    category = Category.get_by_id(1)

    if category.category == "culture":
        items = list(CultureClub.select().dicts())
    elif category.category == "sports":
        items = list(SportsClub.select().dicts())
    elif category.category == "relay":
        items = list(Relay.select().dicts())
    else:
        items = []
    
    return jsonify({
        "category": category.category,
        "category_name": category.category_name,
        "items": items
    })

# 選抜リレーエディタ
@app.route("/class_relay")
def class_relay():
    return render_template("class_relay.html")

@app.route("/api/class_relay_save", methods=["POST"])
def class_relay_save():
    data = request.get_json(silent=True) or {}
    # print(data)

    with db.atomic():
        ClassRelay.delete().execute()

        items = data.get("items", [])

        if items:
            ClassRelay.insert_many([
                {
                    "team_name": item.get("team_name", ""),
                    "first": item.get("first", ""),
                    "second": item.get("second", ""),
                    "third": item.get("third", ""),
                    "fourth": item.get("fourth", ""),
                    "fifth": item.get("fifth", ""),
                    "sixth": item.get("sixth", ""),
                    "seventh": item.get("seventh", ""),
                    "eighth": item.get("eighth", ""),
                    "ninth": item.get("ninth", ""),
                    "tenth": item.get("tenth", "")
                }
                for item in items
            ]).execute()

    return jsonify({"status": "ok"})

@app.route("/api/class_relay_load", methods=["GET"])
def class_relay_load():
    relay = ClassRelay.select().order_by(ClassRelay.id.asc())
    return jsonify([model_to_dict(r) for r in relay])

@app.route("/api/class_relay_data", methods=["GET"])
def class_relay_data():
    items = list(ClassRelay.select().dicts())
    # print(items)
    return jsonify({
        "items": items
    })

# メッセージエディタ
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

@app.route("/page_changer")
def page_changer():
    return render_template("page_changer.html")

@app.route("/api/page_style_save", methods=["POST"])
def page_style_save():
    data = request.get_json(silent=True) or {}
    
    with db.atomic():
        style = data.get("style", "")
        if style == "opening":
            style_name = "開会式"
        elif style == "1G-game":
            style_name = "1学年競技"
        elif style == "2G-game":
            style_name = "2学年競技"
        elif style == "3G-game":
            style_name = "3学年競技"
        elif style == "4G-game":
            style_name = "4学年競技"
        elif style == "5G-game":
            style_name = "5学年競技"
        elif style == "jump":
            style_name = "大縄跳び"
        elif style == "lunch":
            style_name = "昼休憩"
        elif style == "tournament":
            style_name = "トーナメント"
        elif style == "club_relay":
            style_name = "部活対抗リレー"
        elif style == "class_relay":
            style_name = "選抜リレー"
        elif style == "closing":
            style_name = "閉会式"
        else:
            style_name = ""

        PageStyle.update(style=style).where(PageStyle.id == 1).execute()
        PageStyle.update(style_name=style_name).where(PageStyle.id == 1).execute()

    return jsonify({"status": "ok"})

@app.route("/api/page_style_load", methods=["GET"])
def page_style_load():

    style = PageStyle.get_by_id(1)

    return jsonify({
        "style": style.style,
        "style_name": style.style_name
    })

@app.route("/admin")
def admin():
    routes = sorted([f"{rule.endpoint} → {rule.rule}" for rule in app.url_map.iter_rules()])
    return render_template("admin.html", routes=routes)

@app.route("/help")
def helper():
    return redirect(url_for("admin"))

# DB確認
@app.route("/db")
def db_view():

    data = []

    for model in MODELS:
        rows = list(model.select().dicts())

        if rows:
            columns = list(rows[0].keys())
        else:
            columns = []

        data.append({
            "name": model.__name__,
            "rows": rows,
            "columns": columns
        })

    return render_template("db.html", data=data)

# アプリ終了API（テスト用）
@app.route("/exit")
def exit_app():
    os._exit(0)

# 起動
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    init_db()
    init_games_from_csv()
    init_relay_from_csv()
    init_category()
    init_page_style()
    print(f"Starting server on port {PORT}...")
    print(f"Access the admin panel at http://localhost:{PORT}/admin")
    app.run(debug=DEBUG, port=PORT)