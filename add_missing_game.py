# -*- coding: utf-8 -*-
from nba_api.stats.static import players
from nba_api.stats.endpoints import playbyplayv2
import pandas as pd
import time
import re
import os

# --- 補完したい試合の情報をリスト形式で定義 ---
# ここに欠損している試合情報を追加していくだけでOK
MISSING_GAMES = [
    {'player': "Kentavious Caldwell-Pope", 'season': "2024-25", 'game_id': "0022400934"},
    {'player': "Brandin Podziemski", 'season': "2024-25", 'game_id': "0022400901"},
    # {'player': "Davion Mitchell", 'season': "2023-24", 'game_id': "0022300512"},
    # {'player': "Davion Mitchell", 'season': "2023-24", 'game_id': "0022300651"},
    # {'player': "Davion Mitchell", 'season': "2023-24", 'game_id': "0022301228"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400043"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400053"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400065"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400077"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400092"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400102"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400123"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400153"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400289"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400305"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400322"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400333"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400352"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400361"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400377"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400393"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400411"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400419"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400436"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400455"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400470"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400490"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400496"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400519"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400526"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400544"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400564"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400577"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400593"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400608"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400622"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400638"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400652"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400678"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400687"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400708"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400727"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400730"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400743"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400756"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400770"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400790"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400798"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400815"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400830"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400845"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400870"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400883"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400917"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400934"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400944"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400963"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400979"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400988"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022400999"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022401014"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022401038"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022401045"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022401060"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022401074"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022401091"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022401112"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022401141"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022401149"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022401156"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022401186"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022401201"},
    {'player': "Wendell Carter Jr.", 'season': "2024-25", 'game_id': "0022401227"},
    {'player': "Scotty Pippen Jr.", 'season': "2024-25", 'game_id': "0022400520"},
    {'player': "Brandin Podziemski", 'season': "2023-24", 'game_id': "0022300145"},
    {'player': "Draymond Green", 'season': "2023-24", 'game_id': "0022300025"},
    {'player': "Draymond Green", 'season': "2023-24", 'game_id': "0022301182"},
    {'player': "Jalen Duren", 'season': "2023-24", 'game_id': "0022301088"},
]
# -----------------------------------------

def add_missing_games_data():
    """指定された複数試合のデータを取得し、既存のCSVに追記する"""
    
    output_csv_path = 'player_scoring_timeline.csv'
    
    if not os.path.exists(output_csv_path):
        print(f"エラー: '{output_csv_path}' が見つかりません。")
        return
    
    print(f"--- {len(MISSING_GAMES)}件の欠損データの補完を開始します ---")

    for game in MISSING_GAMES:
        player_name = game['player']
        season = game['season']
        game_id = game['game_id']
        
        print(f"\n処理中: {player_name} ({season}) - Game ID: {game_id}")
        
        try:
            player_info = players.find_players_by_full_name(player_name)
            if not player_info:
                print(f"エラー: 選手 {player_name} が見つかりません。")
                continue
            player_id = player_info[0]['id']

            pbp_df = None
            for attempt in range(3):
                try:
                    pbp = playbyplayv2.PlayByPlayV2(game_id=game_id, timeout=90)
                    pbp_df = pbp.get_data_frames()[0]
                    break
                except Exception as e:
                    if attempt < 2:
                        print(f"  (取得エラー。15秒待機して再試行...)")
                        time.sleep(15)
                    else:
                        print(f"  (取得に3回失敗しました。スキップします。)")
                        pbp_df = None
            
            if pbp_df is None:
                continue
                
            pbp_df['Game_ID'] = game_id
            shot_plays = pbp_df[
                (pbp_df['EVENTMSGTYPE'].isin([1, 2, 3])) & 
                (pbp_df['PLAYER1_ID'] == player_id)
            ].copy()
            
            if shot_plays.empty:
                print("情報: この試合では対象選手のシュート記録がありませんでした。")
                continue

            shot_plays['SHOT_TYPE'] = shot_plays['HOMEDESCRIPTION'].fillna(shot_plays['VISITORDESCRIPTION']).apply(
                lambda x: '3PT' if '3PT' in str(x) else ('FT' if 'Free Throw' in str(x) else '2PT')
            )
            shot_plays['MADE_FLAG'] = shot_plays['EVENTMSGTYPE'].apply(lambda x: 1 if x in [1, 3] else 0)
            
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
            
            shot_plays['absolute_minute'] = shot_plays.apply(calculate_absolute_minute, axis=1)
            shot_plays['Player'] = player_name
            shot_plays['Season'] = season
            
            output_df = shot_plays[['Player', 'Season', 'Game_ID', 'absolute_minute', 'SHOT_TYPE', 'MADE_FLAG']]

            output_df.to_csv(output_csv_path, mode='a', header=False, index=False)
            print(f"✅ {len(output_df)}件のデータを追記しました。")

        except Exception as e:
            print(f"処理中に予期せぬエラーが発生しました: {e}")

    print("\n--- 全ての補完処理が完了しました ---")

if __name__ == "__main__":
    add_missing_games_data()