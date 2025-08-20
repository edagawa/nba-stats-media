# -*- coding: utf-8 -*-
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import unicodedata
import re

def normalize_name(name):
    """選手名から特殊文字や接尾辞を除去して正規化する"""
    if not isinstance(name, str):
        return ""
    name = "".join(c for c in unicodedata.normalize('NFKD', name) if not unicodedata.combining(c))
    name = re.sub(r'\s+(Jr|Sr|II|III|IV|V)\.?$', '', name, flags=re.IGNORECASE)
    return name.strip()

TEAM_ROSTER_URLS = {
    "Boston Celtics": "https://www.espn.com/nba/team/roster/_/name/bos/boston-celtics",
    "Brooklyn Nets": "https://www.espn.com/nba/team/roster/_/name/bkn/brooklyn-nets",
    "New York Knicks": "https://www.espn.com/nba/team/roster/_/name/ny/new-york-knicks",
    "Philadelphia 76ers": "https://www.espn.com/nba/team/roster/_/name/phi/philadelphia-76ers",
    "Toronto Raptors": "https://www.espn.com/nba/team/roster/_/name/tor/toronto-raptors",
    "Chicago Bulls": "https://www.espn.com/nba/team/roster/_/name/chi/chicago-bulls",
    "Cleveland Cavaliers": "https://www.espn.com/nba/team/roster/_/name/cle/cleveland-cavaliers",
    "Detroit Pistons": "https://www.espn.com/nba/team/roster/_/name/det/detroit-pistons",
    "Indiana Pacers": "https://www.espn.com/nba/team/roster/_/name/ind/indiana-pacers",
    "Milwaukee Bucks": "https://www.espn.com/nba/team/roster/_/name/mil/milwaukee-bucks",
    "Denver Nuggets": "https://www.espn.com/nba/team/roster/_/name/den/denver-nuggets",
    "Minnesota Timberwolves": "https://www.espn.com/nba/team/roster/_/name/min/minnesota-timberwolves",
    "Oklahoma City Thunder": "https://www.espn.com/nba/team/roster/_/name/okc/oklahoma-city-thunder",
    "Portland Trail Blazers": "https://www.espn.com/nba/team/roster/_/name/por/portland-trail-blazers",
    "Utah Jazz": "https://www.espn.com/nba/team/roster/_/name/utah/utah-jazz",
    "Golden State Warriors": "https://www.espn.com/nba/team/roster/_/name/gs/golden-state-warriors",
    "LA Clippers": "https://www.espn.com/nba/team/roster/_/name/lac/la-clippers",
    "Los Angeles Lakers": "https://www.espn.com/nba/team/roster/_/name/lal/los-angeles-lakers",
    "Phoenix Suns": "https://www.espn.com/nba/team/roster/_/name/phx/phoenix-suns",
    "Sacramento Kings": "https://www.espn.com/nba/team/roster/_/name/sac/sacramento-kings",
    "Atlanta Hawks": "https://www.espn.com/nba/team/roster/_/name/atl/atlanta-hawks",
    "Charlotte Hornets": "https://www.espn.com/nba/team/roster/_/name/cha/charlotte-hornets",
    "Miami Heat": "https://www.espn.com/nba/team/roster/_/name/mia/miami-heat",
    "Orlando Magic": "https://www.espn.com/nba/team/roster/_/name/orl/orlando-magic",
    "Washington Wizards": "https://www.espn.com/nba/team/roster/_/name/wsh/washington-wizards",
    "Dallas Mavericks": "https://www.espn.com/nba/team/roster/_/name/dal/dallas-mavericks",
    "Houston Rockets": "https://www.espn.com/nba/team/roster/_/name/hou/houston-rockets",
    "Memphis Grizzlies": "https://www.espn.com/nba/team/roster/_/name/mem/memphis-grizzlies",
    "New Orleans Pelicans": "https://www.espn.com/nba/team/roster/_/name/no/new-orleans-pelicans",
    "San Antonio Spurs": "https://www.espn.com/nba/team/roster/_/name/sa/san-antonio-spurs"
}

def create_player_team_map():
    """全チームのロスターページをスクレイピングし、選手とチームの対応表CSVを作成する"""
    player_team_list = []
    
    print("--- 全チームのロスターデータを取得しています ---")
    for team_name, url in TEAM_ROSTER_URLS.items():
        try:
            print(f"処理中: {team_name}")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 選手名が含まれるリンク要素をすべて取得
            player_links = soup.select('a[href*="player/_/id/"]')
            
            for link in player_links:
                player_name = link.get_text(strip=True)
                # "Two-Way"などの不要なテキストを除外
                if player_name and not any(char.isdigit() for char in player_name):
                    normalized_name = normalize_name(player_name)
                    player_team_list.append({'Player': normalized_name, 'Team': team_name})
            
            time.sleep(1) # サーバーへの負荷を考慮

        except Exception as e:
            print(f"エラー: {team_name} の処理中に問題が発生しました: {e}")
            
    # DataFrameに変換し、重複を削除
    player_team_df = pd.DataFrame(player_team_list).drop_duplicates()
    
    file_path = "player_team_map.csv"
    player_team_df.to_csv(file_path, index=False)
    print(f"\n--- 選手とチームの対応表を '{file_path}' に正常に保存しました ---")

if __name__ == "__main__":
    create_player_team_map()