# -*- coding: utf-8 -*-
import pandas as pd
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def process_season(year):
    """指定されたシーズンのHollingerデータを取得、整形、保存する"""
    season_string = "{0}-{1}".format(year - 1, str(year)[-2:])
    url = f"https://www.espn.com/nba/hollinger/teamstats/_/year/{year}"
    if year > 2024:
        url = "https://www.espn.com/nba/hollinger/teamstats"
        
    print(f"\n--- {season_string} シーズンのHollinger Statsを取得しています ---")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get(url)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "Table__TBODY")))
        time.sleep(2)
        
        html = driver.page_source
        tables = pd.read_html(StringIO(html))
        
        stats_df = None
        for table in tables:
            if 'RK' in table.columns and 'OFF EFF' in table.columns:
                stats_df = table
                break
        
        if stats_df is None:
            raise ValueError("Hollinger Statsのテーブルが見つかりませんでした。")
        
        # ユーザーが指定した列 + TEAM列を抽出
        required_columns = ['Team', 'PACE', 'AST', 'TO', 'ORR', 'DRR', 'REBR', 'EFF FG%', 'TS%', 'OFF EFF', 'DEF EFF']
        stats_df = stats_df[required_columns]
        
        # チーム名を整形
        stats_df['Team'] = stats_df['Team'].apply(lambda x: x.split('. ', 1)[1] if '. ' in str(x) else x)
        
        file_path = f"espn_team_stats_{season_string}.csv"
        stats_df.to_csv(file_path, index=False)
        print(f"データを '{file_path}' に正常に保存しました。")

    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    process_season(2024) # 2023-24シーズン
    process_season(2025) # 2024-25シーズン