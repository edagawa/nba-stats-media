# -*- coding: utf-8 -*-
import os
import sys
import pandas as pd
import jinja2
import matplotlib.pyplot as plt
import numpy as np

# 日本語フォントがない環境でもエラーが出ないように、デフォルトのsans-serifを指定
plt.rcParams['font.family'] = 'sans-serif'

# --- 定数定義 ---
CONFERENCE_STRUCTURE = {
    "Western Conference": {
        "Northwest Division": ["Denver Nuggets", "Minnesota Timberwolves", "Oklahoma City Thunder", "Portland Trail Blazers", "Utah Jazz"],
        "Pacific Division": ["Golden State Warriors", "LA Clippers", "Los Angeles Lakers", "Phoenix Suns", "Sacramento Kings"],
        "Southwest Division": ["Dallas Mavericks", "Houston Rockets", "Memphis Grizzlies", "New Orleans Pelicans", "San Antonio Spurs"]
    },
    "Eastern Conference": {
        "Atlantic Division": ["Boston Celtics", "Brooklyn Nets", "New York Knicks", "Philadelphia 76ers", "Toronto Raptors"],
        "Central Division": ["Chicago Bulls", "Cleveland Cavaliers", "Detroit Pistons", "Indiana Pacers", "Milwaukee Bucks"],
        "Southeast Division": ["Atlanta Hawks", "Charlotte Hornets", "Miami Heat", "Orlando Magic", "Washington Wizards"]
    }
}

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

STATS_TO_GENERATE = {
    'PACE': 'Pace', 'AST': 'Assist Ratio', 'TO': 'Turnover Ratio',
    'ORR': 'Off Rebound Rate', 'DRR': 'Def Rebound Rate', 'TS%': 'True Shooting %',
    'OFF EFF': 'Offensive Efficiency', 'DEF EFF': 'Defensive Efficiency'
}

# --- ヘルパー関数 ---
def get_footer_data(team_path_prefix, stat_path_prefix):
    """フッター用のナビゲーションデータを、ページの階層に合わせて生成する"""
    stat_pages = [{'name': en_full, 'url': f"{stat_path_prefix}{en_short.replace('%', '_PCT').replace(' ', '_')}.html"} for en_short, en_full in STATS_TO_GENERATE.items()]
    all_teams_structured = {}
    for conf, divisions in CONFERENCE_STRUCTURE.items():
        all_teams_structured[conf] = {}
        for div, teams_in_div in divisions.items():
            all_teams_structured[conf][div] = [{'name': team, 'url': f"{team_path_prefix}comparison_{team.replace(' ', '_')}.html"} for team in teams_in_div]
    return stat_pages, all_teams_structured

# --- ページ生成関数 ---
def generate_main_index(env):
    """トップページ(index.html)を生成する"""
    print("--- トップページの生成開始 ---")
    template = env.get_template('index_template.html')
    stat_pages, all_teams_structured = get_footer_data('./teams/', './stats/')
    render_data = {
        'season_string': '2024-25 & 2023-24 シーズン比較',
        'stat_pages': stat_pages,
        'all_teams_structured': all_teams_structured
    }
    with open("output/index.html", "w", encoding="utf-8") as f:
        f.write(template.render(render_data))
    print("--- トップページの生成完了 ---")

def generate_glossary_page(env):
    """指標解説ページ(glossary.html)を生成する"""
    print("--- 指標解説ページの生成開始 ---")
    template = env.get_template('glossary_template.html')
    glossary_items = [
        {'term': 'Pace', 'description': '1試合あたり48分間のポゼッション（攻撃回数）の推定値。'},
        {'term': 'Offensive Efficiency (OFF EFF)', 'description': '100ポゼッションあたりの得点。'},
        {'term': 'Defensive Efficiency (DEF EFF)', 'description': '100ポゼッションあたりの失点。'},
        {'term': 'True Shooting % (TS%)', 'description': 'フィールドゴール、3ポイント、フリースローを総合的に評価したシュート効率。'},
        {'term': 'Assist Ratio (AST)', 'description': 'チームのフィールドゴール成功のうち、アシストが占める割合。'},
        {'term': 'Turnover Ratio (TO)', 'description': '100ポゼッションあたりのターンオーバー数。'},
        {'term': 'Off Rebound Rate (ORR)', 'description': 'オフェンスリバウンド機会のうち、実際にリバウンドを獲得した割合。'},
        {'term': 'Def Rebound Rate (DRR)', 'description': 'ディフェンスリバウンド機会のうち、実際にリバウンドを獲得した割合。'},
    ]
    stat_pages, all_teams_structured = get_footer_data('./teams/', './stats/')
    render_data = {
        'glossary_items': glossary_items,
        'stat_pages': stat_pages,
        'all_teams_structured': all_teams_structured
    }
    with open("output/glossary.html", "w", encoding="utf-8") as f:
        f.write(template.render(render_data))
    print("--- 指標解説ページの生成完了 ---")

def generate_comparison_pages(df_s1, df_s2, env):
    """チーム別比較ページを生成する"""
    print("--- チーム別比較ページの生成開始 ---")
    df_s1_indexed = df_s1.set_index('Team')
    df_s2_indexed = df_s2.set_index('Team')
    all_teams = sorted(list(df_s1_indexed.index.union(df_s2_indexed.index)))
    template = env.get_template('comparison_template.html')
    
    stats_to_compare = ['PACE', 'OFF EFF', 'DEF EFF', 'TS%', 'AST', 'TO']
    stat_pages, all_teams_structured = get_footer_data('./', '../stats/')

    for team in all_teams:
        try:
            stats1 = df_s1_indexed.loc[team, stats_to_compare]
            stats2 = df_s2_indexed.loc[team, stats_to_compare]

            # グラフ生成
            x = np.arange(len(stats_to_compare))
            width = 0.35
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(x - width/2, stats1, width, label='2023-24')
            ax.bar(x + width/2, stats2, width, label='2024-25')
            ax.set_ylabel('Value')
            ax.set_title(f'Key Stats Comparison: {team}')
            ax.set_xticks(x)
            ax.set_xticklabels(stats_to_compare, rotation=45, ha="right")
            ax.legend()
            fig.tight_layout()
            
            image_filename = team.replace(' ', '_')
            plt.savefig(f"output/images/comparison_{image_filename}.svg", format="svg")
            plt.close()
            
            # HTML生成
            render_data = { 
                'team_name': team,
                'image_filename': image_filename, 
                'stats_s1': df_s1_indexed.loc[team].to_frame(name='Value').to_html(), 
                'stats_s2': df_s2_indexed.loc[team].to_frame(name='Value').to_html(),
                'details': TEAM_DETAILS.get(team, {}),
                'all_teams_structured': all_teams_structured, 
                'stat_pages': stat_pages,
                'season1_url': f"{image_filename}_2023-24_season.html",
                'season2_url': f"{image_filename}_2024-25_season.html"
            }
            output_path = f"output/teams/comparison_{image_filename}.html"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(template.render(render_data))
        except KeyError:
            print(f"警告: '{team}' のデータが片方のシーズンにしか存在しないため、比較ページは生成されません。")
        except Exception as e:
            print(f"エラー: {team} のページ生成中に問題が発生しました: {e}")
    print("--- チーム別比較ページの生成完了 ---")

def generate_stat_pages(df_s1, df_s2, env):
    """指標別ランキングページを生成する"""
    print("--- 指標別ランキングページの生成開始 ---")
    template = env.get_template('stat_comparison_template.html')

    for stat_short, stat_full in STATS_TO_GENERATE.items():
        try:
            # データ準備
            df_merged = pd.merge(
                df_s1[['Team', stat_short]],
                df_s2[['Team', stat_short]],
                on='Team',
                suffixes=('_s1', '_s2')
            ).set_index('Team').sort_values(by=f"{stat_short}_s2", ascending=False)
            
            # グラフ生成
            y = np.arange(len(df_merged.index))
            height = 0.4
            fig, ax = plt.subplots(figsize=(10, 14))
            ax.barh(y + height/2, df_merged[f'{stat_short}_s1'], height, label='2023-24')
            ax.barh(y - height/2, df_merged[f'{stat_short}_s2'], height, label='2024-25')
            ax.set_xlabel('Value')
            ax.set_title(f'All Teams Comparison: {stat_full}')
            ax.set_yticks(y)
            ax.set_yticklabels(df_merged.index)
            ax.invert_yaxis()
            ax.legend()
            fig.tight_layout()
            
            stat_filename = stat_short.replace('%', '_PCT').replace(' ', '_')
            plt.savefig(f"output/images/stat_{stat_filename}.svg", format="svg")
            plt.close()
            
            # HTML生成
            stat_pages, all_teams_structured = get_footer_data('../teams/', './')
            render_data = {
                'stat_name_jp': stat_full,
                'stat_name_en': stat_filename,
                'data_table_html': df_merged.rename(columns={f'{stat_short}_s1': '2023-24', f'{stat_short}_s2': '2024-25'}).to_html(),
                'stat_pages': stat_pages,
                'all_teams_structured': all_teams_structured
            }
            output_path = f"output/stats/{stat_filename}.html"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(template.render(render_data))
        except Exception as e:
            print(f"エラー: {stat_full} のページ生成中に問題が発生しました: {e}")
    print("--- 指標別ランキングページの生成完了 ---")


# --- メイン処理 ---
if __name__ == "__main__":
    print("--- HTML生成スクリプトを開始します ---")
    
    # --- 1. ディレクトリ構造の確認と作成 ---
    os.makedirs("output/teams", exist_ok=True)
    os.makedirs("output/images", exist_ok=True)
    os.makedirs("output/stats", exist_ok=True)
    os.makedirs("output/logos", exist_ok=True)
    print("出力ディレクトリの準備が完了しました。")

    # --- 2. データファイルの読み込み ---
    try:
        df_23_24 = pd.read_csv("espn_team_stats_2023-24.csv")
        df_24_25 = pd.read_csv("espn_team_stats_2024-25.csv")
        print("CSVファイルの読み込みに成功しました。")
    except FileNotFoundError as e:
        print(f"エラー: データファイルが見つかりません。{e}")
        print("get_data.py と get_data_24-25.py を実行して、CSVファイルを先に生成してください。")
        sys.exit(1) # エラーが見つかったのでスクリプトを終了

    # --- 3. Jinja2テンプレートエンジン初期化 ---
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    print("テンプレートエンジンの準備が完了しました。")

    # --- 4. 各種HTMLページの生成 ---
    generate_main_index(env)
    generate_glossary_page(env)
    generate_stat_pages(df_23_24, df_24_25, env)
    generate_comparison_pages(df_23_24, df_24_25, env)
    
    print("\n--- すべての処理が完了しました ---")