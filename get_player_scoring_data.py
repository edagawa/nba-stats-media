# -*- coding: utf-8 -*-
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, playbyplayv2
import pandas as pd
import time
import re
import os
import unicodedata


def normalize_name(name):
    """選手名から特殊文字や接尾辞を除去して正規化する"""
    if not isinstance(name, str):
        return ""
    name = "".join(c for c in unicodedata.normalize('NFKD', name) if not unicodedata.combining(c))
    name = re.sub(r'\s+(Jr|Sr|II|III|IV|V)\.?$', '', name, flags=re.IGNORECASE)
    return name.strip()

# --- 分析対象の選手とシーズンを定義 ---
# キー（選手名）の特殊文字をなくし、正規化しています
PLAYERS_TO_ANALYZE = {
    "Jaren Jackson": ["2023-24", "2024-25"],     # 元の名前: Jaren Jackson Jr.
    "Gary Trent": ["2023-24", "2024-25"],        # 元の名前: Gary Trent Jr.
    "Wendell Carter": ["2023-24", "2024-25"],    # 元の名前: Wendell Carter Jr.
    "Scotty Pippen": ["2023-24", "2024-25"],     # 元の名前: Scotty Pippen Jr.
    "Michael Porter": ["2023-24", "2024-25"],    # 元の名前: Michael Porter Jr.
    "Jimmy Butler": ["2023-24", "2024-25"],      # 元の名前: Jimmy Butler III
    "Trey Murphy": ["2023-24", "2024-25"],       # 元の名前: Trey Murphy III
    "Robert Williams": ["2023-24", "2024-25"],   # 元の名前: Robert Williams III
    "Trey Jemison": ["2023-24", "2024-25"],      # 元の名前: Trey Jemison III
    "Kevin Porter": ["2023-24", "2024-25"],      # 元の名前: Kevin Porter Jr.
    "Craig Porter": ["2023-24", "2024-25"],      # 元の名前: Craig Porter Jr.
    "Jeff Dowtin": ["2023-24", "2024-25"],       # 元の名前: Jeff Dowtin Jr.
    "Vince Williams": ["2023-24", "2024-25"],    # 元の名前: Vince Williams Jr.
    "Wendell Moore": ["2023-24", "2024-25"],     # 元の名前: Wendell Moore Jr.
    "Kevin McCullar": ["2023-24", "2024-25"],    # 元の名前: Kevin McCullar Jr.
    "Andre Jackson": ["2023-24", "2024-25"],     # 元の名前: Andre Jackson Jr.
    "Jaime Jaquez": ["2023-24", "2024-25"],      # 元の名前: Jaime Jaquez Jr.
    "Derrick Jones": ["2023-24", "2024-25"],     # 元の名前: Derrick Jones Jr.
    "Jabari Smith": ["2023-24", "2024-25"],      # 元の名前: Jabari Smith Jr.
    "Ron Harper": ["2023-24", "2024-25"],        # 元の名前: Ron Harper Jr.
    "Keion Brooks": ["2023-24", "2024-25"],      # 元の名前: Keion Brooks Jr.
    "Tim Hardaway": ["2023-24", "2024-25"],      # 元の名前: Tim Hardaway Jr.
    "TyTy Washington": ["2023-24", "2024-25"],   # 元の名前: TyTy Washington Jr.
    "Patrick Baldwin": ["2023-24", "2024-25"],   # 元の名前: Patrick Baldwin Jr.
    "Ronald Holland": ["2023-24", "2024-25"],    # 元の名前: Ronald Holland II
    "Gary Payton": ["2023-24", "2024-25"],       # 元の名前: Gary Payton II
    "Dereck Lively": ["2023-24", "2024-25"],     # 元の名前: Dereck Lively II
}

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
        
        normalized_player_name = normalize_name(player_name)
        
        if normalized_player_name in processed_players:
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
                    
                    pbp_df['Game_ID'] = game_id
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
                
                season_df['Player'] = normalize_name(player_name)
                season_df['Season'] = season
                
                player_all_seasons_df = pd.concat([player_all_seasons_df, season_df])

            except Exception as e:
                print(f"エラー: {player_name} ({season}) の処理中に問題が発生: {e}")

        if not player_all_seasons_df.empty:
            output_df = player_all_seasons_df[['Player', 'Season', 'Game_ID', 'absolute_minute', 'SHOT_TYPE', 'MADE_FLAG']]
            file_exists = os.path.exists(output_csv_path) and os.path.getsize(output_csv_path) > 0
            output_df.to_csv(output_csv_path, mode='a', header=not file_exists, index=False)
            print(f"--- {player_name} のデータをCSVに追記しました ---")

    print("\n--- 全選手のデータ処理が完了しました ---")

if __name__ == "__main__":
    get_scoring_data()