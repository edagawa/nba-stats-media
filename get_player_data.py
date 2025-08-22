# data_acquisition/get_player_data.py

import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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

def fetch_player_stats(year, url):
    season_str = f"{year-1}-{str(year)[-2:]}"
    print(f"\n--- {season_str} シーズンの選手データを取得しています ---")
    print(f"URL: {url}")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        # 「Show More」ボタンがなくなるまでクリックし続ける
        while True:
            try:
                # ボタンが表示されるまで少し待つ
                time.sleep(2)
                show_more_button = driver.find_element(by=By.CSS_SELECTOR, value=".loadMore")
                driver.execute_script("arguments[0].click();", show_more_button)
                print("「Show More」ボタンをクリックしました。")
            except Exception:
                print("「Show More」ボタンが見つからないか、クリックが完了しました。")
                break
        
        html = driver.page_source
        print("ページの全データ読み込みが完了しました。")

        # ★★★ ここからデータ抽出ロジックを修正 ★★★
        all_tables = pd.read_html(StringIO(html), flavor='html5lib')
        
        if len(all_tables) < 2:
            raise ValueError("必要な選手スタッツのテーブルがページに見つかりませんでした。")

        # ESPNのスタッツページは通常2つのテーブルに分かれている
        df_part1 = all_tables[0]
        df_part2 = all_tables[1]

        # 2つのテーブルを水平に結合
        final_df = pd.concat([df_part1, df_part2], axis=1)
        
        # 不要な列やヘッダー行をクリーンアップ
        final_df.columns = final_df.columns.droplevel(0) # 複数レベルのヘッダーを単純化
        final_df = final_df.drop('RK', axis=1) # RK列を削除
        
        # Name列からチーム名を取得し、Player名をクリーンアップ
        # 例: "Jalen Brunson, NYK" -> Player: "Jalen Brunson", Team: "NYK"
        final_df['Team'] = final_df['Name'].apply(lambda x: x.split(', ')[-1] if ', ' in x else '')
        final_df['Player'] = final_df['Name'].apply(lambda x: x.split(', ')[0])

        # Player列の名前を正規化
        final_df['Player'] = final_df['Player'].apply(normalize_name)
        
        # 不要になった元のName列を削除
        final_df = final_df.drop('Name', axis=1)
        # ★★★ データ抽出ロジックの修正ここまで ★★★
        
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