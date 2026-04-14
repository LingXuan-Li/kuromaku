import csv

game_number = 0

# CSVファイルを読み込む関数
def load_csv_data(filepath):
    """CSVファイルからデータを読み込む"""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        pass
    return data

matchesA = load_csv_data('data/field_a.csv')
current_matchA = matchesA[game_number] if matchesA and game_number < len(matchesA) else None
if matchesA and game_number + 1 < len(matchesA):
    next_matchA = matchesA[game_number + 1]["Team-A"] + " vs " + matchesA[game_number + 1]["Team-B"]
    next_gameA = matchesA[game_number + 1]["Game"]
else:
    next_matchA = "次の試合はありません"
    next_gameA = None

if matchesA and game_number + 2 < len(matchesA):
    gathering_matchA = matchesA[game_number + 2]["Team-A"] + " vs " + matchesA[game_number + 2]["Team-B"]
else:
    gathering_matchA = "集合する団体はありません"

print(f"Current Match: {current_matchA}")
print(f"Next Match: {next_matchA}")
print(f"Next Game: {next_gameA}")
print(f"Gathering Match: {gathering_matchA}")