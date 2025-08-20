from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

def verify_player_data(player_name, season):
    """指定された選手のデータ欠損をチェックする"""
    
    print(f"\n--- {player_name} ({season}) のデータ検証を開始 ---")
    
    # 1. NBA公式記録から、そのシーズンにプレイした全試合のIDを取得
    try:
        player_info = players.find_players_by_full_name(player_name)
        if not player_info:
            print(f"エラー: 選手 {player_name} が見つかりません。")
            return
        player_id = player_info[0]['id']

        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season, timeout=60)
        # Game_IDを文字列として扱う
        official_games_df = gamelog.get_data_frames()[0]
        official_games = set(official_games_df['Game_ID'].astype(str))
        
        if not official_games:
            print("情報: 公式記録では、このシーズンに出場試合はありませんでした。")
            return
        print(f"公式記録では、このシーズンに {len(official_games)} 試合出場しています。")
    except Exception as e:
        print(f"公式記録の取得中にエラーが発生しました: {e}")
        return

    # 2. あなたのCSVファイルから、保存されている試合のIDを取得
    try:
        # ★★★ ここを修正 ★★★
        # CSV読み込み時にGame_IDを文字列(string)として指定
        df = pd.read_csv("player_scoring_timeline.csv", dtype={'Game_ID': str})
        
        player_df = df[(df['Player'] == player_name) & (df['Season'] == season)]
        if player_df.empty:
            print("情報: あなたのCSVファイルに、この選手・シーズンのデータはありません。")
            saved_games = set()
        else:
            saved_games = set(player_df['Game_ID'].unique())
        print(f"あなたのCSVファイルには、{len(saved_games)} 試合分のデータが保存されています。")
    except FileNotFoundError:
        print("エラー: player_scoring_timeline.csv が見つかりません。")
        return
    except KeyError:
        print("エラー: CSVに 'Game_ID' 列がありません。get_player_scoring_data.pyを修正して再実行してください。")
        return

    # 3. 2つのリストを比較し、差分（欠損している試合ID）を表示
    missing_games = official_games - saved_games
    if not missing_games:
        print("✅ データ欠損はありません。すべての試合データが揃っています。")
    else:
        print(f"🚨 {len(missing_games)}試合分のデータが欠損しています。")
        print("欠損している試合ID:")
        for game_id in sorted(list(missing_games)):
            print(f" - {game_id}")

if __name__ == "__main__":
    # 今回処理した8人のリスト
    players_to_check = [
        "ALuka Doncic", "Nikola Jokic", "Nikola Vucevic"
    ]
    
    # 8人それぞれについて、2シーズン分のデータ検証を実行
    for player in players_to_check:
        verify_player_data(player_name=player, season="2023-24")
        verify_player_data(player_name=player, season="2024-25")