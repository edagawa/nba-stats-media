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

def fetch_hollinger_stats(driver, year):
    """Hollinger StatsページからOFF EFFとDEF EFFを取得する"""
    season_string = "{0}-{1}".format(year - 1, str(year)[-2:])
    url = f"https://www.espn.com/nba/hollinger/teamstats/_/year/{year}"
    if year > 2024: # The current season URL has a different format
        url = "https://www.espn.com/nba/hollinger/teamstats"
        
    print(f"Hollinger Stats ({season_string}) を取得しています...")
    driver.get(url)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "Table__TBODY")))
    time.sleep(2)
    
    html = driver.page_source
    tables = pd.read_html(StringIO(html))
    
    hollinger_df = None
    for table in tables:
        if 'RK' in table.columns:
            hollinger_df = table
            break
            
    if hollinger_df is None:
        raise ValueError("Hollinger Statsのテーブルが見つかりませんでした。")
        
    hollinger_df = hollinger_df[['Team', 'OFF EFF', 'DEF EFF']]
    hollinger_df['Team'] = hollinger_df['Team'].apply(lambda x: x.split('. ', 1)[1] if '. ' in str(x) else x)
    
    print(f"Hollinger Statsを {hollinger_df.shape[0]} 件取得しました。")
    return hollinger_df

def fetch_main_stats(driver, year):
    """メインの統計ページからデータを取得する"""
    season_string = "{0}-{1}".format(year - 1, str(year)[-2:])
    url = f"https://www.espn.com/nba/stats/team/_/season/{year}/seasontype/2"
    
    print(f"メインスタッツ ({season_string}) を取得しています...")
    driver.get(url)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "Table__TBODY")))
    time.sleep(3)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    
    # ★★★ ここを以前成功したロジックに修正 ★★★
    team_names = []
    team_logo_spans = soup.select('span.TeamLink__Logo')
    for span in team_logo_spans:
        img_tag = span.find('img')
        if img_tag and img_tag.has_attr('title'):
            team_name = img_tag['title']
            if team_name not in team_names:
                team_names.append(team_name)
    
    if not team_names:
         raise ValueError("チーム名が取得できませんでした。")
    
    stats_df = None
    all_tables = pd.read_html(StringIO(html))
    for table in all_tables:
        if table.shape[1] == 19:
            stats_df = table
            break
    
    if stats_df is None:
        raise ValueError("統計データのテーブルが見つかりませんでした。")

    if len(team_names) != stats_df.shape[0]:
        raise ValueError("チーム名の数 ({0}) と統計データの行数 ({1}) が一致しません。".format(len(team_names), stats_df.shape[0]))

    stats_df.insert(0, 'Team', team_names)
    columns = ['Team', 'GP', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'OR', 'DR', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PF']
    stats_df.columns = columns
    print(f"メインスタッツを {stats_df.shape[0]} 件取得しました。")
    return stats_df

def process_season(year):
    """指定されたシーズンのデータを取得、結合、保存する"""
    season_string = "{0}-{1}".format(year - 1, str(year)[-2:])
    print(f"\n--- {season_string} シーズンの処理を開始 ---")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        main_stats = fetch_main_stats(driver, year)
        hollinger_stats = fetch_hollinger_stats(driver, year)
        
        combined_df = pd.merge(main_stats, hollinger_stats, on="Team")
        
        file_path = f"espn_team_stats_{season_string}.csv"
        combined_df.to_csv(file_path, index=False)
        print(f"結合データを '{file_path}' に正常に保存しました。")

    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    process_season(2024)
    process_season(2025)