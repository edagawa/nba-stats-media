# -*- coding: utf-8 -*-
import pandas as pd
from io import StringIO
import requests

def process_season(year):
    """指定されたシーズンのHollingerデータを取得、整形、保存する"""
    season_string = "{0}-{1}".format(year - 1, str(year)[-2:])
    url = f"https://www.espn.com/nba/hollinger/teamstats/_/year/{year}"
    if year > 2024:
        url = "https://www.espn.com/nba/hollinger/teamstats"
        
    print(f"\n--- {season_string} シーズンのHollinger Statsを取得しています ---")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        # requestsで直接HTMLを取得
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # pandasのread_htmlでテーブルを直接読み込む
        tables = pd.read_html(StringIO(response.text))
        
        if not tables:
            raise ValueError("Hollinger Statsのテーブルが見つかりませんでした。")

        # 最初のテーブルが目的のデータ
        stats_df = tables[0]
        
        # 最初の2行（ヘッダー情報）を削除
        stats_df = stats_df.iloc[2:].copy()
        
        # 列名を正しく設定
        stats_df.columns = ['RK', 'TEAM', 'PACE', 'AST', 'TO', 'ORR', 'DRR', 'REBR', 'EFF FG%', 'TS%', 'OFF EFF', 'DEF EFF']
        
        # 不要な列を削除し、ユーザー指定の列のみを選択
        required_columns = ['TEAM', 'PACE', 'AST', 'TO', 'ORR', 'DRR', 'REBR', 'EFF FG%', 'TS%', 'OFF EFF', 'DEF EFF']
        stats_df = stats_df[required_columns]
        
        # 列名を'Team'に変更
        stats_df.rename(columns={'TEAM': 'Team'}, inplace=True)
        
        file_path = f"espn_team_stats_{season_string}.csv"
        stats_df.to_csv(file_path, index=False)
        print(f"データを '{file_path}' に正常に保存しました。")

    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")

if __name__ == "__main__":
    process_season(2024) # 2023-24シーズン
    process_season(2025) # 2024-25シーズン