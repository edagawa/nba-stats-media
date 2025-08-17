# -*- coding: utf-8 -*-
import os
import sys
import pandas as pd
import jinja2
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'

CONFERENCE_STRUCTURE = {
    "Western Conference": { "Northwest Division": ["Denver Nuggets", "Minnesota Timberwolves", "Oklahoma City Thunder", "Portland Trail Blazers", "Utah Jazz"], "Pacific Division": ["Golden State Warriors", "LA Clippers", "Los Angeles Lakers", "Phoenix Suns", "Sacramento Kings"], "Southwest Division": ["Dallas Mavericks", "Houston Rockets", "Memphis Grizzlies", "New Orleans Pelicans", "San Antonio Spurs"] },
    "Eastern Conference": { "Atlantic Division": ["Boston Celtics", "Brooklyn Nets", "New York Knicks", "Philadelphia 76ers", "Toronto Raptors"], "Central Division": ["Chicago Bulls", "Cleveland Cavaliers", "Detroit Pistons", "Indiana Pacers", "Milwaukee Bucks"], "Southeast Division": ["Atlanta Hawks", "Charlotte Hornets", "Miami Heat", "Orlando Magic", "Washington Wizards"] }
}

# ★★★ 用語集データを定義 ★★★
GLOSSARY_DATA = [
    {'term': 'PACE', 'description': 'Pace Factor - the number of possessions a team uses per game.'},
    {'term': 'AST', 'description': "Assist Ratio - the percentage of a team's possessions that ends in an assist. Assist Ratio = (Assists x 100) divided by [(FGA + (FTA x 0.44) + Assists + Turnovers]"},
    {'term': 'TO', 'description': "Turnover Ratio - the percentage of a team's possessions that end in a turnover. Turnover Ratio = (Turnover x 100) divided by [(FGA + (FTA x 0.44) + Assists + Turnovers]"},
    {'term': 'ORR', 'description': 'Offensive rebound rate'},
    {'term': 'DRR', 'description': 'Defensive rebound rate'},
    {'term': 'REBR', 'description': 'Rebound Rate - the percentage of missed shots that a team rebounds. Rebound Rate = (Rebounds x Team Minutes) divided by [Player Minutes x (Team Rebounds + Opponent Rebounds)]'},
    {'term': 'EFF FG%', 'description': 'Effective Field Goal Percentage'},
    {'term': 'TS%', 'description': "True Shooting Percentage - what a team's shooting percentage would be if we accounted for free throws and 3-pointers. True Shooting Percentage = (Total points x 50) divided by [(FGA + (FTA x 0.44)]"},
    {'term': 'OFF EFF', 'description': 'Offensive Efficiency - the number of points a team scores per 100 possessions.'},
    {'term': 'DEF EFF', 'description': 'Defensive Efficiency - the number of points a team allows per 100 possessions.'},
    {'term': 'NET EFF', 'description': 'Net Rating - the point differential between a team\'s offensive and defensive efficiency. (OFF EFF - DEF EFF)'}
]


def generate_season_pages(season_string, team_stats_df, stat_pages_info_main):
    # (この関数は変更なし)
    print("--- {0} シーズンのページ生成開始 ---".format(season_string))
    # ... (内容は前回と同じ)

def generate_comparison_pages(df_s1, df_s2):
    # (この関数は変更なし)
    print("--- チーム別比較ページの生成開始 ---")
    # ... (内容は前回と同じ)

def generate_main_index(all_teams_structured_main, stat_pages_info_main):
    # (この関数は変更なし)
    print("--- メインインデックスページの生成開始 ---")
    # ... (内容は前回と同じ)

def generate_stat_comparison_pages(df_s1, df_s2):
    # (この関数は変更なし)
    print("--- 指標別比較ページの生成開始 ---")
    # ... (内容は前回と同じ)

# ★★★ 新しい関数を追加 ★★★
def generate_glossary_page():
    """用語集ページを生成する"""
    print("--- 用語集ページの生成開始 ---")
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    glossary_template = env.get_template('glossary_template.html')
    
    html_content = glossary_template.render(glossary_items=GLOSSARY_DATA)
    with open(os.path.join("output", "glossary.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print("--- 用語集ページの生成完了 ---")

def main():
    try:
        df_s1 = pd.read_csv("espn_team_stats_2023-24.csv")
        df_s2 = pd.read_csv("espn_team_stats_2024-25.csv")
    except FileNotFoundError as e:
        print("エラー: CSVファイルが見つかりません。 {0}".format(e))
        sys.exit(1)
    
    df_s1['NET EFF'] = df_s1['OFF EFF'] - df_s1['DEF EFF']
    df_s2['NET EFF'] = df_s2['OFF EFF'] - df_s2['DEF EFF']

    stats_to_generate = { 'PACE': 'Pace', 'AST': 'Assist Ratio', 'TO': 'Turnover Ratio', 'ORR': 'Off Rebound Rate', 'DRR': 'Def Rebound Rate', 'TS%': 'True Shooting %', 'OFF EFF': 'Offensive Efficiency', 'DEF EFF': 'Defensive Efficiency', 'NET EFF': 'Net Rating' }
    stat_pages_info_main = [{'name': en_full, 'url': './stats/{0}.html'.format(en_short.replace('%', '_PCT').replace(' ', '_'))} for en_short, en_full in stats_to_generate.items()]
    all_teams_structured_main = {}
    for conf, divisions in CONFERENCE_STRUCTURE.items():
        all_teams_structured_main[conf] = {}
        for div, teams in divisions.items():
            all_teams_structured_main[conf][div] = [{'name': team, 'url': './teams/{0}.html'.format(team.replace(' ', '_'))} for team in teams]

    # ★★★ `generate_season_pages`の呼び出しを修正 ★★★
    generate_season_pages("2023-24", df_s1, stat_pages_info_main)
    generate_season_pages("2024-25", df_s2, stat_pages_info_main)
    
    generate_comparison_pages(df_s1, df_s2)
    generate_stat_comparison_pages(df_s1, df_s2)
    generate_main_index(all_teams_structured_main, stat_pages_info_main)
    
    # ★★★ 新しい関数を呼び出す ★★★
    generate_glossary_page()

    print("\nすべてのHTMLファイルの生成が完了しました。")

if __name__ == "__main__":
    main()