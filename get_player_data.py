# data_acquisition/get_player_data.py

import pandas as pd
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import unicodedata
import re

def normalize_name(name):
    """選手名から特殊文字や接尾辞を除去して正規化する"""
    if not isinstance(name, str):
        return ""
    name = "".join(c for c in unicodedadata.normalize('NFKD', name) if not unicodedata.combining(c))
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

        while True:
            try:
                time.sleep(2)
                show_more_button = driver.find_element(by=By.CSS_SELECTOR, value=".loadMore")
                driver.execute_script("arguments[0].click();", show_more_button)
                print("「Show More」ボタンをクリックしました。")
            except Exception:
                print("「Show More」ボタンが見つからないか、クリックが完了しました。")
                break
        
        html = driver.page_source
        print("ページの全データ読み込みが完了しました。")

        all_tables = pd.read_html(StringIO(html), flavor='html5lib')
        
        if len(all_tables) < 2:
            raise ValueError("必要な選手スタッツのテーブルがページに見つかりませんでした。")

        df_part1 = all_tables[0]
        df_part2 = all_tables[1]
        final_df = pd.concat([df_part1, df_part2], axis=1)
        
        # ★★★ ここからデータ抽出ロジックを修正 ★★★
        # 列名が不安定なため、列の位置（インデックス）で操作する
        
        # 2列目（インデックス1）に選手名とチーム名が含まれている
        name_team_col = final_df.iloc[:, 1]
        
        # 選手名とチーム名を分離して新しい列を作成
        final_df['Player'] = name_team_col.apply(lambda x: x.split(', ')[0])
        final_df['Team'] = name_team_col.apply(lambda x: x.split(', ')[-1] if ', ' in x else '')
        
        # 選手名を正規化
        final_df['Player'] = final_df['Player'].apply(normalize_name)
        
        # 元の不要な列（0列目のRKと1列目のName）を削除
        final_df = final_df.drop(final_df.columns[[0, 1]], axis=1)

        # statsの列名をクリーンアップ (例: ('GP', 'GP') -> 'GP')
        final_df.columns = [col[1] if isinstance(col, tuple) else col for col in final_df.columns]
        
        # 列の順番を整理
        cols_to_move = ['Player', 'Team']
        final_df = final_df[cols_to_move + [col for col in final_df.columns if col not in cols_to_move]]
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