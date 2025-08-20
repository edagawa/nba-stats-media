# -*- coding: utf-8 -*-
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import unicodedata
import re  # ★★★ この行を追加 ★★★

def normalize_name(name):
    """選手名から特殊文字や接尾辞を除去して正規化する"""
    if not isinstance(name, str):
        return ""
    name = "".join(c for c in unicodedata.normalize('NFKD', name) if not unicodedata.combining(c))
    name = re.sub(r'\s+(Jr|Sr|II|III|IV|V)\.?$', '', name, flags=re.IGNORECASE)
    return name.strip()

def fetch_player_stats(year, url):
    season_str = f"{year-1}-{str(year)[-2:]}"
    print(f"\n--- {season_str} シーズンの選手データを取得しています ---")
    print(f"URL: {url}")
    print("（自動でChromeブラウザが起動します...）")

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        while True:
            try:
                show_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".loadMore"))
                )
                driver.execute_script("arguments[0].click();", show_more_button)
                print("「Show More」ボタンをクリックしました。")
                time.sleep(2)
            except Exception:
                print("「Show More」ボタンが見つからないか、クリックが完了しました。")
                break
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        print("ページの全データ読み込みと解析が完了しました。")

        all_tables = pd.read_html(StringIO(html), flavor='html5lib')
        
        player_info_df = all_tables[0]
        player_stats_df = all_tables[1]

        player_names = [a.text for a in soup.select('a.AnchorLink[data-player-uid]')]
        player_teams = [span.text for span in soup.select('span.pl2.ns10.athleteCell__teamAbbrev')]

        if len(player_names) != len(player_info_df):
            player_info_df = player_info_df.iloc[1:]
        
        if len(player_names) != len(player_info_df):
             raise ValueError(f"選手名リスト({len(player_names)})と情報テーブル({len(player_info_df)})の数が一致しません。")
        
        player_info_df['Player'] = player_names
        player_info_df['TeamAbbrev'] = player_teams
        
        player_info_df = player_info_df[['Player', 'TeamAbbrev']]
        player_stats_df = player_stats_df.drop(player_stats_df.columns[0], axis=1)

        final_df = pd.concat([player_info_df.reset_index(drop=True), player_stats_df.reset_index(drop=True)], axis=1)
        
        final_df.rename(columns={'TeamAbbrev': 'Team'}, inplace=True)
        
        # Player列の名前を正規化
        final_df['Player'] = final_df['Player'].apply(normalize_name)
        
        file_path = f"player_stats_{season_str}.csv"
        final_df.to_csv(file_path, index=False)
        print(f"データを '{file_path}' に正常に保存しました。")

    except Exception as e:
        print(f"データの取得中にエラーが発生しました: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    fetch_player_stats(2024, "https://www.espn.com/nba/stats/player/_/season/2024/seasontype/2")
    fetch_player_stats(2025, "https://www.espn.com/nba/stats/player")