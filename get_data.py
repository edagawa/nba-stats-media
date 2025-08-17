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

def fetch_and_save_espn_stats():
    """
    Seleniumでブラウザを操作してESPNのページを完全に読み込み、
    チーム統計をスクレイピングしてCSVファイルに保存する。
    """
    url = "https://www.espn.com/nba/stats/team/_/season/2024/seasontype/2"
    print("ESPNから2023-24シーズンのデータを取得しています...")
    print("（自動でChromeブラウザが起動します...）")

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
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Table__TBODY"))
        )
        
        time.sleep(3)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        
        print("ページの読み込みと解析が完了しました。")

        # ★★★ ここから修正箇所 ★★★
        # ご提示のHTML構造に合わせて、imgタグのtitleからチーム名を取得
        team_names = []
        team_logo_spans = soup.select('span.TeamLink__Logo')

        for span in team_logo_spans:
            img_tag = span.find('img')
            if img_tag and img_tag.has_attr('title'):
                team_names.append(img_tag['title'])
        # ★★★ ここまで修正箇所 ★★★
        
        if not team_names:
             raise ValueError("チーム名が取得できませんでした。")
        
        print("チーム名を {0} 件取得しました。".format(len(team_names)))

        stats_df = None
        all_tables = pd.read_html(StringIO(html))
        for table in all_tables:
            if table.shape[1] == 19:
                stats_df = table
                break
        
        if stats_df is None:
            raise ValueError("統計データのテーブルが見つかりませんでした。")

        print("統計データを {0} 行取得しました。".format(stats_df.shape[0]))

        if len(team_names) != stats_df.shape[0]:
            raise ValueError("チーム名の数 ({0}) と統計データの行数 ({1}) が一致しません。".format(len(team_names), stats_df.shape[0]))

        stats_df.insert(0, 'Team', team_names)
        
        columns = ['Team', 'GP', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'OR', 'DR', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PF']
        stats_df.columns = columns

        file_path = "espn_team_stats_23-24.csv"
        stats_df.to_csv(file_path, index=False)
        print("データを '{0}' に正常に保存しました。".format(file_path))

    except Exception as e:
        print("データの取得中にエラーが発生しました: {0}".format(e))
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    fetch_and_save_espn_stats()