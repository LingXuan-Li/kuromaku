import csv
import os

# 保存先フォルダ
os.makedirs("data", exist_ok=True)

# 作成したいCSVの定義
csv_files = {
    "sports_club.csv": [
        ["team_name","first","second","third","fourth","fifth","sixth"],
        ["野球部","蜂須賀","丸山","桜庭","土岐","鷹野","犬養"],
        ["弓道部","海老原","風間","尾崎","飯嶋","九条","有栖川"],
        ["卓球部","薄井","葛西","村雨","常盤","黒須","二階堂"],
        ["登山部","藍原","月岡","椎名","稲垣","霧島","橘"],
        ["柔道部","榊原","津田","南條","犬塚","望月","佐伯"],
        ["水球部","富樫","多田","大河内","琴吹","御影","桐生"],
    ],
    "culture_club.csv": [
        ["team_name","first","second","third","fourth","fifth","sixth"],
        ["PC部","久坂","恒藤","薙野","水無瀬","七瀬","八重樫"],
        ["文芸部","天野","白石","村上","高坂","中谷","菅原"],
        ["天文部","青木","小野寺","片桐","松本","西園寺","大窪"],
        ["陶芸部","高梨","田辺","井上","吉岡","長谷川","佐伯"],
        ["茶道部","藤原","大塚","望月","柴田","早川","黒川"],
        ["染料部","渡邊","渡邉","渡辺","齋藤","斉藤","齊籐"],
    ],
    "class_club.csv": [
        ["team_name","first","second","third","fourth","fifth","sixth","seventh","eighth","ninth","tenth"],
        ["1組","東雲","榊原","御影","柏木","有馬","冬木","柊木","篠宮","橘川","朝比奈"],
        ["2組","神崎","藤代","桐谷","真鍋","結城","如月","高梨","蓮見","鷹野","若槻"],
        ["3組","相沢","黒川","瀬戸","三雲","穂積","春日","早乙女","立花","羽鳥","御園"],
    ],
    "tournaments.csv": [
        ["team_name","game_name","tournament_number","seed"],
        ["9-8男子","後期バスケ","1","1"],
        ["7-5男子","後期バスケ","1","2"],
        ["1-7男子","後期バスケ","1","3"],
        ["8-1男子","後期バスケ","1","4"],
        ["7-6男子","後期バスケ","1","5"],
        ["3-4男子","後期バスケ","1","6"],
        ["2-9男子","バスケ","2","1"],
        ["5-3男子","バスケ","2","2"],
        ["6-1男子","バスケ","2","3"],
        ["4-8男子","バスケ","2","4"],
        ["1-2男子","バスケ","2","5"],
        ["7-9男子","バスケ","2","6"],
        ["3-9女子","ドッヂ","3","1"],
        ["5-3女子","ドッヂ","3","2"],
        ["6-1女子","ドッヂ","3","3"],
        ["4-8女子","ドッヂ","3","4"],
        ["1-3女子","ドッヂ","3","5"],
        ["6-9女子","ドッヂ","3","6"],
    ]
}

created_count = 0

# CSVを順番に作成
for filename, rows in csv_files.items():
    file_path = os.path.join("data", filename)

    # すでに存在する場合はスキップ
    if os.path.exists(file_path):
        print("スキップ（既存）:", file_path)
        continue

    # CSV作成
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    created_count += 1
    print("作成:", file_path)

# 全CSVが作成された場合のみ data.db を削除
if created_count == len(csv_files):
    db_path = os.path.join("data", "data.db")

    if os.path.exists(db_path):
        os.remove(db_path)
        print("削除:", db_path)
    else:
        print("data.db は存在しません")