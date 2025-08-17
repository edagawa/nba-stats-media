# -*- coding: utf-8 -*-
import os
import sys
import pandas as pd
import jinja2
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'

# (CONFERENCE_STRUCTUREは変更なし)
CONFERENCE_STRUCTURE = {
    "Western Conference": { "Northwest Division": ["Denver Nuggets", "Minnesota Timberwolves", "Oklahoma City Thunder", "Portland Trail Blazers", "Utah Jazz"], "Pacific Division": ["Golden State Warriors", "LA Clippers", "Los Angeles Lakers", "Phoenix Suns", "Sacramento Kings"], "Southwest Division": ["Dallas Mavericks", "Houston Rockets", "Memphis Grizzlies", "New Orleans Pelicans", "San Antonio Spurs"] },
    "Eastern Conference": { "Atlantic Division": ["Boston Celtics", "Brooklyn Nets", "New York Knicks", "Philadelphia 76ers", "Toronto Raptors"], "Central Division": ["Chicago Bulls", "Cleveland Cavaliers", "Detroit Pistons", "Indiana Pacers", "Milwaukee Bucks"], "Southeast Division": ["Atlanta Hawks", "Charlotte Hornets", "Miami Heat", "Orlando Magic", "Washington Wizards"] }
}

# ★★★ チーム詳細データを定義 ★★★
TEAM_DETAILS = {
    "Atlanta Hawks": {"conference": "Eastern", "division": "Southeast", "arena": "State Farm Arena", "location": "Atlanta, Georgia", "championships": "1 (1958)"},
    "Boston Celtics": {"conference": "Eastern", "division": "Atlantic", "arena": "TD Garden", "location": "Boston, Massachusetts", "championships": "18 (Most recent: 2024)"},
    "Brooklyn Nets": {"conference": "Eastern", "division": "Atlantic", "arena": "Barclays Center", "location": "Brooklyn, New York", "championships": "0"},
    "Charlotte Hornets": {"conference": "Eastern", "division": "Southeast", "arena": "Spectrum Center", "location": "Charlotte, North Carolina", "championships": "0"},
    "Chicago Bulls": {"conference": "Eastern", "division": "Central", "arena": "United Center", "location": "Chicago, Illinois", "championships": "6 (Most recent: 1998)"},
    "Cleveland Cavaliers": {"conference": "Eastern", "division": "Central", "arena": "Rocket Mortgage FieldHouse", "location": "Cleveland, Ohio", "championships": "1 (2016)"},
    "Dallas Mavericks": {"conference": "Western", "division": "Southwest", "arena": "American Airlines Center", "location": "Dallas, Texas", "championships": "1 (2011)"},
    "Denver Nuggets": {"conference": "Western", "division": "Northwest", "arena": "Ball Arena", "location": "Denver, Colorado", "championships": "1 (2023)"},
    "Detroit Pistons": {"conference": "Eastern", "division": "Central", "arena": "Little Caesars Arena", "location": "Detroit, Michigan", "championships": "3 (Most recent: 2004)"},
    "Golden State Warriors": {"conference": "Western", "division": "Pacific", "arena": "Chase Center", "location": "San Francisco, California", "championships": "7 (Most recent: 2022)"},
    "Houston Rockets": {"conference": "Western", "division": "Southwest", "arena": "Toyota Center", "location": "Houston, Texas", "championships": "2 (Most recent: 1995)"},
    "Indiana Pacers": {"conference": "Eastern", "division": "Central", "arena": "Gainbridge Fieldhouse", "location": "Indianapolis, Indiana", "championships": "0"},
    "LA Clippers": {"conference": "Western", "division": "Pacific", "arena": "Intuit Dome", "location": "Inglewood, California", "championships": "0"},
    "Los Angeles Lakers": {"conference": "Western", "division": "Pacific", "arena": "Crypto.com Arena", "location": "Los Angeles, California", "championships": "17 (Most recent: 2020)"},
    "Memphis Grizzlies": {"conference": "Western", "division": "Southwest", "arena": "FedExForum", "location": "Memphis, Tennessee", "championships": "0"},
    "Miami Heat": {"conference": "Eastern", "division": "Southeast", "arena": "Kaseya Center", "location": "Miami, Florida", "championships": "3 (Most recent: 2013)"},
    "Milwaukee Bucks": {"conference": "Eastern", "division": "Central", "arena": "Fiserv Forum", "location": "Milwaukee, Wisconsin", "championships": "2 (Most recent: 2021)"},
    "Minnesota Timberwolves": {"conference": "Western", "division": "Northwest", "arena": "Target Center", "location": "Minneapolis, Minnesota", "championships": "0"},
    "New Orleans Pelicans": {"conference": "Western", "division": "Southwest", "arena": "Smoothie King Center", "location": "New Orleans, Louisiana", "championships": "0"},
    "New York Knicks": {"conference": "Eastern", "division": "Atlantic", "arena": "Madison Square Garden", "location": "New York, New York", "championships": "2 (Most recent: 1973)"},
    "Oklahoma City Thunder": {"conference": "Western", "division": "Northwest", "arena": "Paycom Center", "location": "Oklahoma City, Oklahoma", "championships": "1 (1979 as Seattle SuperSonics)"},
    "Orlando Magic": {"conference": "Eastern", "division": "Southeast", "arena": "Kia Center", "location": "Orlando, Florida", "championships": "0"},
    "Philadelphia 76ers": {"conference": "Eastern", "division": "Atlantic", "arena": "Wells Fargo Center", "location": "Philadelphia, Pennsylvania", "championships": "3 (Most recent: 1983)"},
    "Phoenix Suns": {"conference": "Western", "division": "Pacific", "arena": "Footprint Center", "location": "Phoenix, Arizona", "championships": "0"},
    "Portland Trail Blazers": {"conference": "Western", "division": "Northwest", "arena": "Moda Center", "location": "Portland, Oregon", "championships": "1 (1977)"},
    "Sacramento Kings": {"conference": "Western", "division": "Pacific", "arena": "Golden 1 Center", "location": "Sacramento, California", "championships": "1 (1951 as Rochester Royals)"},
    "San Antonio Spurs": {"conference": "Western", "division": "Southwest", "arena": "Frost Bank Center", "location": "San Antonio, Texas", "championships": "5 (Most recent: 2014)"},
    "Toronto Raptors": {"conference": "Eastern", "division": "Atlantic", "arena": "Scotiabank Arena", "location": "Toronto, Ontario", "championships": "1 (2019)"},
    "Utah Jazz": {"conference": "Western", "division": "Northwest", "arena": "Delta Center", "location": "Salt Lake City, Utah", "championships": "0"},
    "Washington Wizards": {"conference": "Eastern", "division": "Southeast", "arena": "Capital One Arena", "location": "Washington, D.C.", "championships": "1 (1978 as Washington Bullets)"},
}

# (generate_season_pages, generate_main_index, etc. は変更なし)

def generate_comparison_pages(df_s1, df_s2):
    print("--- チーム別比較ページの生成開始 ---")
    df_s1 = df_s1.set_index('Team'); df_s2 = df_s2.set_index('Team')
    all_teams = sorted(list(df_s1.index.union(df_s2.index)))
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'); env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    comparison_template = env.get_template('comparison_template.html')
    output_dir_teams = "output/teams"; output_dir_images = "output/images"
    os.makedirs(output_dir_teams, exist_ok=True); os.makedirs(output_dir_images, exist_ok=True)
    stats_to_compare = ['PACE', 'OFF EFF', 'DEF EFF', 'NET EFF', 'TS%', 'AST', 'TO']
    stats_to_generate = { 'PACE': 'Pace', 'AST': 'Assist Ratio', 'TO': 'Turnover Ratio', 'ORR': 'Off Rebound Rate', 'DRR': 'Def Rebound Rate', 'TS%': 'True Shooting %', 'OFF EFF': 'Offensive Efficiency', 'DEF EFF': 'Defensive Efficiency', 'NET EFF': 'Net Rating' }
    stat_pages_info_footer = [{'name': en_full, 'url': '../stats/{0}.html'.format(en_short.replace('%', '_PCT').replace(' ', '_'))} for en_short, en_full in stats_to_generate.items()]
    all_teams_structured_footer = {}
    for conf, divisions in CONFERENCE_STRUCTURE.items():
        all_teams_structured_footer[conf] = {};
        for div, teams_in_div in divisions.items():
            all_teams_structured_footer[conf][div] = [{'name': team, 'url': './{0}.html'.format(team.replace(' ', '_'))} for team in teams_in_div]
            
    for team in all_teams:
        try:
            stats1 = df_s1.loc[team, stats_to_compare]; stats2 = df_s2.loc[team, stats_to_compare]
            x = np.arange(len(stats_to_compare)); width = 0.35
            fig, ax = plt.subplots(figsize=(10, 6)); rects1 = ax.bar(x - width/2, stats1, width, label='2023-24'); rects2 = ax.bar(x + width/2, stats2, width, label='2024-25')
            ax.set_ylabel('Value'); ax.set_title('Key Stats Comparison: {0}'.format(team)); ax.set_xticks(x); ax.set_xticklabels(stats_to_compare, rotation=45, ha="right"); ax.legend(); fig.tight_layout()
            image_filename = team.replace(' ', '_')
            plt.savefig(os.path.join(output_dir_images, "comparison_{0}.svg".format(image_filename)), format="svg"); plt.close()
            
            # ★★★ テンプレートにチーム詳細情報を渡す ★★★
            render_data = { 
                'team_name': team, 'image_filename': image_filename, 
                'stats_s1': df_s1.loc[team].to_frame().to_html(), 
                'stats_s2': df_s2.loc[team].to_frame().to_html(),
                'details': TEAM_DETAILS.get(team, {}), # 見つからない場合は空の辞書を渡す
                'all_teams_structured': all_teams_structured_footer, 
                'stat_pages': stat_pages_info_footer 
            }
            html_content = comparison_template.render(render_data)
            with open(os.path.join(output_dir_teams, "{0}.html".format(image_filename)), "w", encoding="utf-8") as f: f.write(html_content)
        except KeyError: print("'{0}' のデータが片方のシーズンにしか存在しないため、比較ページは生成されません。".format(team))
    print("--- チーム別比較ページの生成完了 ---")

# ... (他の関数は変更なし) ...