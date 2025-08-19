# -*- coding: utf-8 -*-
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, playbyplayv2
import pandas as pd
import time
import re
import os

# --- 分析対象の選手とシーズンを定義 ---
PLAYERS_TO_ANALYZE = {
    # "Luka Dončić": ["2023-24", "2024-25"], "Cade Cunningham": ["2023-24", "2024-25"],
    # "Jamal Murray": ["2023-24", "2024-25"], "LeBron James": ["2023-24", "2024-25"],
    # "Jayson Tatum": ["2023-24", "2024-25"], "Nikola Jokić": ["2023-24", "2024-25"],
    # "Fred VanVleet": ["2023-24", "2024-25"], "James Harden": ["2023-24", "2024-25"],
    # "Paolo Banchero": ["2023-24", "2024-25"], "Mikal Bridges": ["2023-24", "2024-25"],
    # "Austin Reaves": ["2023-24", "2024-25"], "OG Anunoby": ["2023-24", "2024-25"],
    # "Anthony Edwards": ["2023-24", "2024-25"], "Franz Wagner": ["2023-24", "2024-25"],
    # "Christian Braun": ["2023-24", "2024-25"], "Tobias Harris": ["2023-24", "2024-25"],
    # "Bam Adebayo": ["2023-24", "2024-25"], "Kawhi Leonard": ["2023-24", "2024-25"],
    # "Jalen Brunson": ["2023-24", "2024-25"], "Derrick White": ["2023-24", "2024-25"],
    # "Giannis Antetokounmpo": ["2023-24", "2024-25"], "Aaron Gordon": ["2023-24", "2024-25"],
    # "Shai Gilgeous-Alexander": ["2023-24", "2024-25"], "Alperen Sengun": ["2023-24", "2024-25"],
    # "Ivica Zubac": ["2023-24", "2024-25"], "Jaylen Brown": ["2023-24", "2024-25"],
    # "Rui Hachimura": ["2023-24", "2024-25"], "Jimmy Butler": ["2023-24", "2024-25"],
    # "Tyler Herro": ["2023-24", "2024-25"], "Josh Hart": ["2023-24", "2024-25"],
    # "Kevin Durant": ["2023-24", "2024-25"], "Devin Booker": ["2023-24", "2024-25"],
    # "Damian Lillard": ["2023-24", "2024-25"], "Stephen Curry": ["2023-24", "2024-25"],
    # "Trae Young": ["2023-24", "2024-25"], "Donovan Mitchell": ["2023-24", "2024-25"],
    # "De'Aaron Fox": ["2023-24", "2024-25"], "Zach LaVine": ["2023-24", "2024-25"],
    # "DeMar DeRozan": ["2023-24", "2024-25"], "RJ Barrett": ["2023-24", "2024-25"],
    # "Jalen Green": ["2023-24", "2024-25"], "Darius Garland": ["2023-24", "2024-25"],
    # "Jordan Poole": ["2023-24", "2024-25"], "Coby White": ["2023-24", "2024-25"],
    # "Miles Bridges": ["2023-24", "2024-25"], "Scottie Barnes": ["2023-24", "2024-25"],
    # "Anfernee Simons": ["2023-24", "2024-25"], "Domantas Sabonis": ["2023-24", "2024-25"],
    # "Shaedon Sharpe": ["2023-24", "2024-25"], "Nikola Vučević": ["2023-24", "2024-25"],
    # "Collin Sexton": ["2023-24", "2024-25"], "Michael Porter Jr.": ["2023-24", "2024-25"],
    # "Andrew Wiggins": ["2023-24", "2024-25"], "Buddy Hield": ["2023-24", "2024-25"],
    # "Moses Moody": ["2023-24", "2024-25"],
    # "Julius Randle": ["2023-24", "2024-25"], "Davion Mitchell": ["2023-24", "2024-25"],
    # "Karl-Anthony Towns": ["2023-24", "2024-25"], "Desmond Bane": ["2023-24", "2024-25"],
    # "Jalen Williams": ["2023-24", "2024-25"], "Jaren Jackson Jr.": ["2023-24", "2024-25"],
    # "Gary Trent Jr.": ["2023-24", "2024-25"], "Dorian Finney-Smith": ["2023-24", "2024-25"],
    # "Norman Powell": ["2023-24", "2024-25"], "Jalen Duren": ["2023-24", "2024-25"],
    # "Tyrese Haliburton": ["2023-24", "2024-25"], "Pascal Siakam": ["2023-24", "2024-25"],
    # "Andrew Nembhard": ["2023-24", "2024-25"], "Jaden McDaniels": ["2023-24", "2024-25"],
    "Amen Thompson": ["2023-24", "2024-25"], "Jrue Holiday": ["2023-24", "2024-25"],
    "Kentavious Caldwell-Pope": ["2023-24", "2024-25"], "Draymond Green": ["2023-24", "2024-25"],
    "Wendell Carter Jr.": ["2023-24", "2024-25"], "Scotty Pippen Jr.": ["2023-24", "2024-25"],
    "Evan Mobley": ["2023-24", "2024-25"], "Brandin Podziemski": ["2023-24", "2024-25"]
}

# PLAYERS_TO_ANALYZE = {
#     "Jayson Tatum": ["2023-24", "2024-25"],
#     "Mikal Bridges": ["2023-24", "2024-25"],
#     # 他の50人の選手は一時的にコメントアウトするか削除
# }

def get_scoring_data():
    output_csv_path = 'player_scoring_timeline.csv'
    players_to_analyze = list(PLAYERS_TO_ANALYZE.keys())
    
    processed_players = set()
    if os.path.exists(output_csv_path):
        try:
            processed_df = pd.read_csv(output_csv_path)
            if not processed_df.empty:
                processed_players = set(processed_df['Player'].unique())
                print(f"'{output_csv_path}' を発見しました。{len(processed_players)}人の処理済み選手をスキップします。")
        except pd.errors.EmptyDataError:
            print(f"'{output_csv_path}' は空です。最初から処理を開始します。")
        except Exception as e:
            print(f"'{output_csv_path}' の読み込み中にエラー: {e}")

    total_players = len(players_to_analyze)
    
    for i, player_name in enumerate(players_to_analyze):
        if player_name in processed_players:
            print(f"\n--- [{i+1}/{total_players}] {player_name} は処理済みのためスキップします ---")
            continue

        player_all_seasons_df = pd.DataFrame()
        seasons = PLAYERS_TO_ANALYZE[player_name]

        for season in seasons:
            try:
                print(f"\n--- [{i+1}/{total_players}] {player_name} ({season}) のデータを取得開始 ---")
                
                player_info = players.find_players_by_full_name(player_name)
                if not player_info:
                    print(f"警告: {player_name} が見つかりません。")
                    continue
                player_id = player_info[0]['id']

                gamelog_df = None
                for attempt in range(3):
                    try:
                        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season, timeout=90)
                        gamelog_df = gamelog.get_data_frames()[0]
                        break 
                    except Exception as e:
                        if attempt < 2:
                            print(f"エラー発生。15秒待機して再試行します... ({attempt + 2}/3回目)")
                            time.sleep(15)
                        else:
                            print(f"ゲームログの取得に3回失敗。スキップします。エラー: {e}")
                            gamelog_df = None
                
                if gamelog_df is None or gamelog_df.empty:
                    print(f"情報: {season}シーズンに {player_name} の試合データはありませんでした。")
                    continue
                
                game_ids = gamelog_df['Game_ID']
                all_shot_plays = []
                print(f"シーズン{len(game_ids)}試合のデータを処理します...")

                for game_id in game_ids:
                    pbp_df = None
                    for attempt in range(3):
                        try:
                            pbp = playbyplayv2.PlayByPlayV2(game_id=game_id, timeout=90)
                            pbp_df = pbp.get_data_frames()[0]
                            break
                        except Exception as e:
                            if attempt < 2:
                                print(f"  (試合ID:{game_id} 取得エラー。15秒待機して再試行...)")
                                time.sleep(15)
                            else:
                                print(f"  (試合ID:{game_id} の取得に3回失敗。この試合をスキップします。)")
                                pbp_df = None
                    
                    if pbp_df is None:
                        continue
                    
                    pbp_df['Game_ID'] = game_id # Game_ID列を追加
                    shot_plays = pbp_df[
                        (pbp_df['EVENTMSGTYPE'].isin([1, 2, 3])) & 
                        (pbp_df['PLAYER1_ID'] == player_id)
                    ].copy()
                    
                    all_shot_plays.append(shot_plays)
                    time.sleep(1.2)

                if not all_shot_plays:
                    continue

                season_df = pd.concat(all_shot_plays, ignore_index=True)
                
                season_df['SHOT_TYPE'] = season_df['HOMEDESCRIPTION'].fillna(season_df['VISITORDESCRIPTION']).apply(
                    lambda x: '3PT' if '3PT' in str(x) else ('FT' if 'Free Throw' in str(x) else '2PT')
                )
                season_df['MADE_FLAG'] = season_df['EVENTMSGTYPE'].apply(lambda x: 1 if x in [1, 3] else 0)
                
                def calculate_absolute_minute(row):
                    try:
                        remaining_minutes = int(row['PCTIMESTRING'].split(':')[0])
                        quarter = row['PERIOD']
                        if quarter <= 4:
                            return ((quarter - 1) * 12) + (11 - remaining_minutes)
                        else:
                            return 48 + ((quarter - 5) * 5) + (4 - remaining_minutes)
                    except:
                        return -1
                
                season_df['absolute_minute'] = season_df.apply(calculate_absolute_minute, axis=1)
                
                season_df['Player'] = player_name
                season_df['Season'] = season
                
                player_all_seasons_df = pd.concat([player_all_seasons_df, season_df])

            except Exception as e:
                print(f"エラー: {player_name} ({season}) の処理中に問題が発生: {e}")

        if not player_all_seasons_df.empty:
            # ★★★ ここを修正 ★★★
            output_df = player_all_seasons_df[['Player', 'Season', 'Game_ID', 'absolute_minute', 'SHOT_TYPE', 'MADE_FLAG']]
            file_exists = os.path.exists(output_csv_path) and os.path.getsize(output_csv_path) > 0
            output_df.to_csv(output_csv_path, mode='a', header=not file_exists, index=False)
            print(f"--- {player_name} のデータをCSVに追記しました ---")

    print("\n--- 全選手のデータ処理が完了しました ---")

if __name__ == "__main__":
    get_scoring_data()