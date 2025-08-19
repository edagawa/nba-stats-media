# -*- coding: utf-8 -*-
import os
import sys
import pandas as pd
import jinja2
import matplotlib.pyplot as plt
import numpy as np
import re  # ★★★ この行を追加 ★★★
import json

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
    'OFF EFF': 'Offensive Efficiency', 'DEF EFF': 'Defensive Efficiency', 'NET EFF': 'Net Rating'
}

TEAM_NAME_MAP = {
    "Atlanta": "Atlanta Hawks", "Boston": "Boston Celtics", "Brooklyn": "Brooklyn Nets",
    "Charlotte": "Charlotte Hornets", "Chicago": "Chicago Bulls", "Cleveland": "Cleveland Cavaliers",
    "Dallas": "Dallas Mavericks", "Denver": "Denver Nuggets", "Detroit": "Detroit Pistons",
    "Golden State": "Golden State Warriors", "Houston": "Houston Rockets", "Indiana": "Indiana Pacers",
    "LA Clippers": "LA Clippers", "LA Lakers": "Los Angeles Lakers", "Memphis": "Memphis Grizzlies",
    "Miami": "Miami Heat", "Milwaukee": "Milwaukee Bucks", "Minnesota": "Minnesota Timberwolves",
    "New Orleans": "New Orleans Pelicans", "New York": "New York Knicks", "Oklahoma City": "Oklahoma City Thunder",
    "Orlando": "Orlando Magic", "Philadelphia": "Philadelphia 76ers", "Phoenix": "Phoenix Suns",
    "Portland": "Portland Trail Blazers", "Sacramento": "Sacramento Kings", "San Antonio": "San Antonio Spurs",
    "Toronto": "Toronto Raptors", "Utah": "Utah Jazz", "Washington": "Washington Wizards"
}

# ★★★ 選手ページ生成関数を追加 ★★★
def generate_player_pages(env, scoring_timeline_data):
    """選手比較ページを生成する"""
    print("--- 選手ページの生成開始 ---")
    try:
        df_s1 = pd.read_csv("player_stats_2023-24.csv")
        df_s2 = pd.read_csv("player_stats_2024-25.csv")
    except FileNotFoundError:
        print("警告: 選手データ(CSV)が見つかりません。get_player_data.py を実行してください。")
        return

    team_abbr_map = {
        'ATL': 'Atlanta Hawks', 'BOS': 'Boston Celtics', 'BKN': 'Brooklyn Nets', 'CHA': 'Charlotte Hornets', 'CHI': 'Chicago Bulls',
        'CLE': 'Cleveland Cavaliers', 'DAL': 'Dallas Mavericks', 'DEN': 'Denver Nuggets', 'DET': 'Detroit Pistons', 'GS': 'Golden State Warriors',
        'HOU': 'Houston Rockets', 'IND': 'Indiana Pacers', 'LAC': 'LA Clippers', 'LAL': 'Los Angeles Lakers', 'MEM': 'Memphis Grizzlies',
        'MIA': 'Miami Heat', 'MIL': 'Milwaukee Bucks', 'MIN': 'Minnesota Timberwolves', 'NO': 'New Orleans Pelicans', 'NY': 'New York Knicks',
        'OKC': 'Oklahoma City Thunder', 'ORL': 'Orlando Magic', 'PHI': 'Philadelphia 76ers', 'PHX': 'Phoenix Suns', 'POR': 'Portland Trail Blazers',
        'SAC': 'Sacramento Kings', 'SA': 'San Antonio Spurs', 'TOR': 'Toronto Raptors', 'UTAH': 'Utah Jazz', 'WSH': 'Washington Wizards'
    }
    df_s2['full_team_name'] = df_s2['Team'].apply(lambda x: team_abbr_map.get(str(x).split('/')[0].strip().upper()))

    df_merged = pd.merge(df_s2, df_s1, on='Player', how='left', suffixes=('_s2', '_s1'))
    template = env.get_template('player_comparison_template.html')
    stats_to_compare = ['PTS', 'REB', 'AST', 'STL', 'BLK']
    
    stat_pages_footer, all_teams_structured_footer = get_footer_data('../teams/', '../stats/')

    for index, player_data in df_merged.iterrows():
        player_name = player_data.get('Player', 'Unknown')
        try:
            player_filename = re.sub(r'[\\/*?:"<>|]', "", player_name).replace(' ', '_')

            stats_s2_table = pd.DataFrame(player_data.filter(like='_s2')).rename(index=lambda x: x.replace('_s2', ''))
            stats_s1_table = pd.DataFrame(player_data.filter(like='_s1')).rename(index=lambda x: x.replace('_s1', ''))
            
            graph_stats_s2_series = pd.to_numeric(stats_s2_table.loc[stats_to_compare].squeeze(), errors='coerce')
            graph_stats_s1_series = pd.to_numeric(stats_s1_table.loc[stats_to_compare].squeeze(), errors='coerce')
            graph_stats_s2 = graph_stats_s2_series.fillna(0).values
            graph_stats_s1 = graph_stats_s1_series.fillna(0).values

            x = np.arange(len(stats_to_compare))
            width = 0.35
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(x - width/2, graph_stats_s1, width, label='2023-24')
            ax.bar(x + width/2, graph_stats_s2, width, label='2024-25')
            ax.set_ylabel('Value')
            ax.set_title(f'Key Stats Comparison: {player_name}')
            ax.set_xticks(x)
            ax.set_xticklabels(stats_to_compare)
            ax.legend()
            fig.tight_layout()
            plt.savefig(f"output/images/players/comparison_{player_filename}.svg", format="svg")
            plt.close()
            
            for season_str_short in ["23-24", "24-25"]:
                season_str_long = f"20{season_str_short}"
                player_timeline = scoring_timeline_data[
                    (scoring_timeline_data['Player'] == player_name) & 
                    (scoring_timeline_data['Season'] == season_str_long)
                ]

                if player_timeline.empty:
                    continue

                # --- グラフ1: ゴール機会 ---
                attempts_agg = pd.DataFrame({'absolute_minute': range(48)})
                attempts_pivot = player_timeline.pivot_table(
                    index='absolute_minute', 
                    columns=['SHOT_TYPE', 'MADE_FLAG'], 
                    aggfunc='size', 
                    fill_value=0
                )
                
                # ★★★ この部分がエラーを解決する重要なコードです ★★★
                # pivot_tableで生成された階層的な列名を単純な文字列に変換
                attempts_pivot.columns = ['_'.join(map(str, col)) for col in attempts_pivot.columns]
                attempts_agg = pd.merge(attempts_agg, attempts_pivot, on='absolute_minute', how='left').fillna(0)
                
                fig, ax = plt.subplots(figsize=(15, 7))
                bottom = np.zeros(48)
                
                miss_3pt = attempts_agg.get('3PT_0', 0)
                miss_2pt = attempts_agg.get('2PT_0', 0)
                miss_ft = attempts_agg.get('FT_0', 0)
                ax.bar(attempts_agg['absolute_minute'], miss_3pt, bottom=bottom, color='#aec7e8', label='3PT Miss')
                bottom += miss_3pt
                ax.bar(attempts_agg['absolute_minute'], miss_2pt, bottom=bottom, color='#ffbb78', label='2PT Miss')
                bottom += miss_2pt
                ax.bar(attempts_agg['absolute_minute'], miss_ft, bottom=bottom, color='#ff9896', label='FT Miss')
                bottom += miss_ft
                
                made_3pt = attempts_agg.get('3PT_1', 0)
                made_2pt = attempts_agg.get('2PT_1', 0)
                made_ft = attempts_agg.get('FT_1', 0)
                ax.bar(attempts_agg['absolute_minute'], made_3pt, bottom=bottom, color='#1f77b4', label='3PT Made')
                bottom += made_3pt
                ax.bar(attempts_agg['absolute_minute'], made_2pt, bottom=bottom, color='#ff7f0e', label='2PT Made')
                bottom += made_2pt
                ax.bar(attempts_agg['absolute_minute'], made_ft, bottom=bottom, color='#d62728', label='FT Made')

                ax.set_title(f'{player_name} - Shot Attempts (Made/Miss) Timeline ({season_str_long})')
                ax.set_xlabel('Game Minute'); ax.set_ylabel('Number of Attempts')
                ax.set_xticks([0, 12, 24, 36, 47]); ax.grid(axis='y', linestyle='--', alpha=0.7); ax.legend()
                plt.savefig(f"output/images/players/timeline_attempts_{season_str_short}_{player_filename}.svg", format="svg")
                plt.close()

                # --- グラフ2: 得点 ---
                points_agg = pd.DataFrame({'absolute_minute': range(48)})
                made_shots = player_timeline[player_timeline['MADE_FLAG'] == 1]
                if not made_shots.empty:
                    point_map = {'3PT': 3, '2PT': 2, 'FT': 1}
                    made_shots = made_shots.copy()
                    made_shots['POINTS'] = made_shots['SHOT_TYPE'].map(point_map)
                    points_by_type = made_shots.groupby(['absolute_minute', 'SHOT_TYPE'])['POINTS'].sum().unstack(fill_value=0)
                    points_agg = pd.merge(points_agg, points_by_type, on='absolute_minute', how='left').fillna(0)

                fig, ax = plt.subplots(figsize=(15, 7))
                ax.bar(points_agg['absolute_minute'], points_agg.get('3PT', 0), color='#1f77b4', label='3-Pointers')
                ax.bar(points_agg['absolute_minute'], points_agg.get('2PT', 0), bottom=points_agg.get('3PT', 0), color='#ff7f0e', label='2-Pointers')
                ax.bar(points_agg['absolute_minute'], points_agg.get('FT', 0), bottom=points_agg.get('3PT', 0) + points_agg.get('2PT', 0), color='#2ca02c', label='Free Throws')
                ax.set_title(f'{player_name} - Points Scored Timeline ({season_str_long})')
                ax.set_xlabel('Game Minute'); ax.set_ylabel('Points Scored')
                ax.set_xticks([0, 12, 24, 36, 47]); ax.grid(axis='y', linestyle='--', alpha=0.7); ax.legend()
                plt.savefig(f"output/images/players/timeline_points_{season_str_short}_{player_filename}.svg", format="svg")
                plt.close()
            
            team_name = player_data.get('full_team_name', '')
            team_url = ""
            if team_name:
                team_url = f"../teams/comparison_{team_name.replace(' ', '_')}.html"

            render_data = {
                'player_name': player_name,
                'player_filename': player_filename,
                'player_info': stats_s2_table.T.to_dict('records')[0],
                'stats_s1': stats_s1_table.to_html(header=False, na_rep='-'),
                'stats_s2': stats_s2_table.to_html(header=False, na_rep='-'),
                'stat_pages': stat_pages_footer,
                'all_teams_structured': all_teams_structured_footer,
                'team_name': team_name,
                'team_url': team_url
            }
            output_path = f"output/players/{player_filename}.html"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(template.render(render_data))
        except Exception as e:
            print(f"警告: {player_name} のページ生成中にエラー: {e}")
    print("--- 選手ページの生成完了 ---")

# --- ヘルパー関数 ---
def generate_team_summary(s1_stats, s2_stats):
    """2シーズン分のデータからポジティブなサマリーテキストを生成する"""
    
    # 日本語の指標名とポジティブ/ネガティブな変化の表現
    STAT_INFO = {
        'OFF EFF': {'jp': 'オフェンス', 'good_change': '向上', 'bad_change': '低下'},
        'DEF EFF': {'jp': 'ディフェンス', 'good_change': '改善', 'bad_change': '悪化'},
        'PACE': {'jp': '試合のペース', 'good_change': '高速化', 'bad_change': '低速化'}
    }
    
    # 2024-25シーズンの各指標のランクを取得
    ranks = {
        'OFF EFF': s2_stats['OFF EFF_rank'],
        'DEF EFF': s2_stats['DEF EFF_rank'],
        'PACE': s2_stats['PACE_rank']
    }
    
    # ランクが最も良いもの（数値が小さい）をチームの強みとする
    best_strength_stat = min(ranks, key=ranks.get)
    best_rank = ranks[best_strength_stat]
    
    # ランクが最も悪いもの（数値が大きい）をチームの課題とする
    biggest_challenge_stat = max(ranks, key=ranks.get)
    worst_rank = ranks[biggest_challenge_stat]

    positive_sentence = ""
    challenge_sentence = ""

    # --- 1. ポジティブな要素から文章を組み立てる ---
    if best_rank <= 10:
        strength_desc = "リーグ屈指の" if best_rank <= 5 else "リーグ上位の"
        positive_sentence = f"今シーズンのチームの最大の武器は、{strength_desc}{STAT_INFO[best_strength_stat]['jp']}です。"
        
        # 強みに関する昨シーズンからの変化を追記
        if best_strength_stat == 'OFF EFF' and s2_stats['OFF EFF'] > s1_stats['OFF EFF']:
            positive_sentence += " 前年からさらに磨きがかかり、リーグを代表する攻撃力を手に入れました。"
        elif best_strength_stat == 'DEF EFF' and s2_stats['DEF EFF'] < s1_stats['DEF EFF']: # 低い方が良い
            positive_sentence += " 鉄壁の守備は前年からさらに堅固なものとなり、相手チームを苦しめています。"
            
    else: # 뚜렷한 강점이 없는 경우
        positive_sentence = "今シーズンは攻守両面でバランスの取れた、安定感のあるパフォーマンスを見せています。"

    # --- 2. 課題と成長の可能性について文章を組み立てる ---
    # 強みと課題が同じ指標でない場合に、課題を明確に記述する
    if worst_rank >= 21 and best_strength_stat != biggest_challenge_stat:
        challenge_desc = "リーグ下位に苦しむ" if worst_rank >= 26 else "改善が待たれる"
        challenge_sentence = f"一方で、今後の更なる飛躍のためには、{challenge_desc}{STAT_INFO[biggest_challenge_stat]['jp']}の立て直しが鍵となるでしょう。"

        # 課題に関する昨シーズンからの変化を追記
        if biggest_challenge_stat == 'DEF EFF' and s2_stats['DEF EFF'] > s1_stats['DEF EFF']: # 高い方が悪い
            challenge_sentence += " 前年に比べ失点が増加傾向にあり、ここを修正できれば一気に上位進出が見えてきます。"
        elif biggest_challenge_stat == 'OFF EFF' and s2_stats['OFF EFF'] < s1_stats['OFF EFF']:
            challenge_sentence += " やや得点力に課題を残しており、攻撃のバリエーションを増やすことが期待されます。"
    else:
        # 뚜렷한 약점이 없는 경우
        challenge_sentence = "この安定感をシーズン通して維持し、さらに一段階レベルアップできれば、素晴らしい結果が期待できます。"

    return positive_sentence + " " + challenge_sentence


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
        {'term': 'Net Rating (NET EFF)', 'description': 'Offensive EfficiencyとDefensive Efficiencyの差。100ポゼッションあたりの得失点差を示す。'},
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

# ★★★ チームページ生成関数を修正 ★★★
def generate_comparison_pages(df_s1, df_s2, df_players, video_data, env):
    """チーム別比較ページを生成する"""
    print("--- チーム別比較ページの生成開始 ---")
    df_s1_indexed = df_s1.set_index('Team')
    df_s2_indexed = df_s2.set_index('Team')
    all_teams = sorted(list(df_s1_indexed.index.union(df_s2_indexed.index)))
    template = env.get_template('comparison_template.html')
    
    stats_to_compare = ['PACE', 'OFF EFF', 'DEF EFF', 'NET EFF', 'TS%', 'AST', 'TO']
    stat_pages_footer, all_teams_structured_footer = get_footer_data('./', '../stats/')

    for team in all_teams:
        try:
            stats1 = df_s1_indexed.loc[team]
            stats2 = df_s2_indexed.loc[team]

            # グラフ生成
            stats_for_graph1 = stats1[stats_to_compare]
            stats_for_graph2 = stats2[stats_to_compare]
            x = np.arange(len(stats_to_compare))
            width = 0.35
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(x - width/2, stats_for_graph1, width, label='2023-24')
            ax.bar(x + width/2, stats_for_graph2, width, label='2024-25')
            ax.set_ylabel('Value')
            ax.set_title(f'Key Stats Comparison: {team}')
            ax.set_xticks(x)
            ax.set_xticklabels(stats_to_compare, rotation=45, ha="right")
            ax.legend()
            fig.tight_layout()
            
            image_filename = team.replace(' ', '_')
            plt.savefig(f"output/images/comparison_{image_filename}.svg", format="svg")
            plt.close()

            summary = generate_team_summary(stats1, stats2)
            
            player_list = []
            if df_players is not None:
                team_roster = df_players[df_players['full_team_name'] == team]
                for _, player in team_roster.iterrows():
                    player_name = player['Player']
                    player_filename = re.sub(r'[\\/*?:"<>|]', "", player_name).replace(' ', '_')
                    player_list.append({
                        'name': player_name,
                        'url': f"../players/{player_filename}.html"
                    })

            video_id = video_data.get(team)
            video_embed_url = f"https://www.youtube.com/embed/{video_id}" if video_id else None
            
            render_data = { 
                'team_name': team,
                'image_filename': image_filename, 
                'stats_s1': stats1.to_frame(name='Value').to_html(), 
                'stats_s2': stats2.to_frame(name='Value').to_html(),
                'details': TEAM_DETAILS.get(team, {}),
                'all_teams_structured': all_teams_structured_footer, 
                'stat_pages': stat_pages_footer,
                'summary_text': summary,
                'player_list': player_list,
                'video_embed_url': video_embed_url,
            }

            output_path = f"output/teams/comparison_{image_filename}.html"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(template.render(render_data))
        except Exception as e:
            print(f"警告: {team} の比較ページ生成中にエラーが発生しました。詳細: {e}")
    print("--- チーム別比較ページの生成完了 ---")

def generate_stat_pages(df_s1, df_s2, env):
    """指標別ランキングページを生成する"""
    print("--- 指標別ランキングページの生成開始 ---")
    template = env.get_template('stat_comparison_template.html')

    for stat_short, stat_full in STATS_TO_GENERATE.items():
        try:
            # ★★★ ここを修正 ★★★
            # DEF EFFとTO(Turnover Ratio)の場合だけ昇順ソート
            sort_ascending = True if stat_short in ('DEF EFF', 'TO') else False

            # データ準備
            df_merged = pd.merge(
                df_s1[['Team', stat_short]],
                df_s2[['Team', stat_short]],
                on='Team',
                suffixes=('_s1', '_s2')
            ).set_index('Team').sort_values(by=f"{stat_short}_s2", ascending=sort_ascending)
            
            # (以降のグラフ生成、HTML生成は変更なし)
            # ...
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

# def generate_player_pages(env, scoring_timeline_data):
#     """選手比較ページを生成する"""
#     print("--- 選手ページの生成開始 ---")
#     try:
#         df_s1 = pd.read_csv("player_stats_2023-24.csv")
#         df_s2 = pd.read_csv("player_stats_2024-25.csv")
#     except FileNotFoundError:
#         print("警告: 選手データ(CSV)が見つかりません。get_player_data.py を実行してください。")
#         return

#     # チーム名の正式名称をマッピングに追加
#     team_abbr_map = {
#         'ATL': 'Atlanta Hawks', 'BOS': 'Boston Celtics', 'BKN': 'Brooklyn Nets', 'CHA': 'Charlotte Hornets', 'CHI': 'Chicago Bulls',
#         'CLE': 'Cleveland Cavaliers', 'DAL': 'Dallas Mavericks', 'DEN': 'Denver Nuggets', 'DET': 'Detroit Pistons', 'GS': 'Golden State Warriors',
#         'HOU': 'Houston Rockets', 'IND': 'Indiana Pacers', 'LAC': 'LA Clippers', 'LAL': 'Los Angeles Lakers', 'MEM': 'Memphis Grizzlies',
#         'MIA': 'Miami Heat', 'MIL': 'Milwaukee Bucks', 'MIN': 'Minnesota Timberwolves', 'NO': 'New Orleans Pelicans', 'NY': 'New York Knicks',
#         'OKC': 'Oklahoma City Thunder', 'ORL': 'Orlando Magic', 'PHI': 'Philadelphia 76ers', 'PHX': 'Phoenix Suns', 'POR': 'Portland Trail Blazers',
#         'SAC': 'Sacramento Kings', 'SA': 'San Antonio Spurs', 'TOR': 'Toronto Raptors', 'UTAH': 'Utah Jazz', 'WSH': 'Washington Wizards'
#     }
#     df_s2['full_team_name'] = df_s2['Team'].apply(lambda x: team_abbr_map.get(str(x).split('/')[0].strip().upper()))

#     df_merged = pd.merge(df_s2, df_s1, on='Player', how='left', suffixes=('_s2', '_s1'))
#     template = env.get_template('player_comparison_template.html')
#     stats_to_compare = ['PTS', 'REB', 'AST', 'STL', 'BLK']
    
#     stat_pages_footer, all_teams_structured_footer = get_footer_data('../teams/', '../stats/')

#     for index, player_data in df_merged.iterrows():
#         player_name = player_data.get('Player', 'Unknown')
#         try:
#             player_filename = re.sub(r'[\\/*?:"<>|]', "", player_name).replace(' ', '_')

#             stats_s2_table = pd.DataFrame(player_data.filter(like='_s2')).rename(index=lambda x: x.replace('_s2', ''))
#             stats_s1_table = pd.DataFrame(player_data.filter(like='_s1')).rename(index=lambda x: x.replace('_s1', ''))
            
#             graph_stats_s2_series = pd.to_numeric(stats_s2_table.loc[stats_to_compare].squeeze(), errors='coerce')
#             graph_stats_s1_series = pd.to_numeric(stats_s1_table.loc[stats_to_compare].squeeze(), errors='coerce')
#             graph_stats_s2 = graph_stats_s2_series.fillna(0).values
#             graph_stats_s1 = graph_stats_s1_series.fillna(0).values

#             x = np.arange(len(stats_to_compare))
#             width = 0.35
#             fig, ax = plt.subplots(figsize=(10, 6))
#             ax.bar(x - width/2, graph_stats_s1, width, label='2023-24')
#             ax.bar(x + width/2, graph_stats_s2, width, label='2024-25')
#             ax.set_ylabel('Value')
#             ax.set_title(f'Key Stats Comparison: {player_name}')
#             ax.set_xticks(x)
#             ax.set_xticklabels(stats_to_compare)
#             ax.legend()
#             fig.tight_layout()
#             plt.savefig(f"output/images/players/comparison_{player_filename}.svg", format="svg")
#             plt.close()
            
#             # 2シーズン分、2種類のグラフ（合計4つ）を作成
#             for season_str_short in ["23-24", "24-25"]:
#                 season_str_long = f"20{season_str_short}"
#                 player_timeline = scoring_timeline_data[
#                     (scoring_timeline_data['Player'] == player_name) & 
#                     (scoring_timeline_data['Season'] == season_str_long)
#                 ]

#                 if player_timeline.empty:
#                     continue

#                 # --- グラフ1: ゴール機会（成功・失敗の内訳）---
#                 attempts_agg = pd.DataFrame({'absolute_minute': range(48)})
#                 attempts_pivot = player_timeline.pivot_table(
#                     index='absolute_minute', 
#                     columns=['SHOT_TYPE', 'MADE_FLAG'], 
#                     aggfunc='size', 
#                     fill_value=0
#                 )
#                 attempts_agg = pd.merge(attempts_agg, attempts_pivot, on='absolute_minute', how='left').fillna(0)
#                 # pivot_tableの列名はタプルになるため、アクセスしやすいように文字列に変換
#                 attempts_agg.columns = ['_'.join(map(str, col)) if isinstance(col, tuple) else col for col in attempts_agg.columns]

#                 fig, ax = plt.subplots(figsize=(15, 7))
                
#                 # 積み上げグラフの底辺を管理
#                 bottom = np.zeros(48)
                
#                 # 失敗したシュートを描画
#                 miss_3pt = attempts_agg.get('3PT_0', 0)
#                 miss_2pt = attempts_agg.get('2PT_0', 0)
#                 miss_ft = attempts_agg.get('FT_0', 0)
#                 ax.bar(attempts_agg['absolute_minute'], miss_3pt, bottom=bottom, color='#aec7e8', label='3PT Miss')
#                 bottom += miss_3pt
#                 ax.bar(attempts_agg['absolute_minute'], miss_2pt, bottom=bottom, color='#ffbb78', label='2PT Miss')
#                 bottom += miss_2pt
#                 ax.bar(attempts_agg['absolute_minute'], miss_ft, bottom=bottom, color='#ff9896', label='FT Miss')
#                 bottom += miss_ft
                
#                 # 成功したシュートを描画
#                 made_3pt = attempts_agg.get('3PT_1', 0)
#                 made_2pt = attempts_agg.get('2PT_1', 0)
#                 made_ft = attempts_agg.get('FT_1', 0)
#                 ax.bar(attempts_agg['absolute_minute'], made_3pt, bottom=bottom, color='#1f77b4', label='3PT Made')
#                 bottom += made_3pt
#                 ax.bar(attempts_agg['absolute_minute'], made_2pt, bottom=bottom, color='#ff7f0e', label='2PT Made')
#                 bottom += made_2pt
#                 ax.bar(attempts_agg['absolute_minute'], made_ft, bottom=bottom, color='#d62728', label='FT Made')

#                 ax.set_title(f'{player_name} - Shot Attempts (Made/Miss) Timeline ({season_str_long})')
#                 ax.set_xlabel('Game Minute'); ax.set_ylabel('Number of Attempts')
#                 ax.set_xticks([0, 12, 24, 36, 47]); ax.grid(axis='y', linestyle='--', alpha=0.7); ax.legend()
#                 plt.savefig(f"output/images/players/timeline_attempts_{season_str_short}_{player_filename}.svg", format="svg")
#                 plt.close()

#                 # --- グラフ2: 得点 ---
#                 points_agg = pd.DataFrame({'absolute_minute': range(48)})
#                 made_shots = player_timeline[player_timeline['MADE_FLAG'] == 1]
#                 if not made_shots.empty:
#                     point_map = {'3PT': 3, '2PT': 2, 'FT': 1}
#                     made_shots = made_shots.copy()
#                     made_shots['POINTS'] = made_shots['SHOT_TYPE'].map(point_map)
#                     points_by_type = made_shots.groupby(['absolute_minute', 'SHOT_TYPE'])['POINTS'].sum().unstack(fill_value=0)
#                     points_agg = pd.merge(points_agg, points_by_type, on='absolute_minute', how='left').fillna(0)

#                 fig, ax = plt.subplots(figsize=(15, 7))
#                 ax.bar(points_agg['absolute_minute'], points_agg.get('3PT', 0), color='#1f77b4', label='3-Pointers')
#                 ax.bar(points_agg['absolute_minute'], points_agg.get('2PT', 0), bottom=points_agg.get('3PT', 0), color='#ff7f0e', label='2-Pointers')
#                 ax.bar(points_agg['absolute_minute'], points_agg.get('FT', 0), bottom=points_agg.get('3PT', 0) + points_agg.get('2PT', 0), color='#2ca02c', label='Free Throws')
#                 ax.set_title(f'{player_name} - Points Scored Timeline ({season_str_long})')
#                 ax.set_xlabel('Game Minute'); ax.set_ylabel('Points Scored')
#                 ax.set_xticks([0, 12, 24, 36, 47]); ax.grid(axis='y', linestyle='--', alpha=0.7); ax.legend()
#                 plt.savefig(f"output/images/players/timeline_points_{season_str_short}_{player_filename}.svg", format="svg")
#                 plt.close()
            
#             team_name = player_data.get('full_team_name', '')
#             team_url = ""
#             if team_name:
#                 team_url = f"../teams/comparison_{team_name.replace(' ', '_')}.html"

#             render_data = {
#                 'player_name': player_name,
#                 'player_filename': player_filename,
#                 'player_info': stats_s2_table.T.to_dict('records')[0],
#                 'stats_s1': stats_s1_table.to_html(header=False, na_rep='-'),
#                 'stats_s2': stats_s2_table.to_html(header=False, na_rep='-'),
#                 'stat_pages': stat_pages_footer,
#                 'all_teams_structured': all_teams_structured_footer,
#                 'team_name': team_name,
#                 'team_url': team_url
#             }
#             output_path = f"output/players/{player_filename}.html"
#             with open(output_path, "w", encoding="utf-8") as f:
#                 f.write(template.render(render_data))
#         except Exception as e:
#             print(f"警告: {player_name} のページ生成中にエラー: {e}")
#     print("--- 選手ページの生成完了 ---")

# --- メイン処理 ---
if __name__ == "__main__":
    print("--- HTML生成スクリプトを開始します ---")
    
    # --- 1. ディレクトリ構造の確認と作成 ---
    os.makedirs("output/teams", exist_ok=True)
    os.makedirs("output/images", exist_ok=True)
    os.makedirs("output/stats", exist_ok=True)
    os.makedirs("output/logos", exist_ok=True)
    os.makedirs("output/css", exist_ok=True)
    os.makedirs("output/players", exist_ok=True)
    os.makedirs("output/images/players", exist_ok=True)
    print("出力ディレクトリの準備が完了しました。")

    # --- 2. データファイルの読み込み ---
    try:
        df_23_24 = pd.read_csv("espn_team_stats_2023-24.csv")
        df_24_25 = pd.read_csv("espn_team_stats_2024-25.csv")
        print("CSVファイルの読み込みに成功しました。")

        df_23_24['Team'] = df_23_24['Team'].replace(TEAM_NAME_MAP)
        df_24_25['Team'] = df_24_25['Team'].replace(TEAM_NAME_MAP)
        print("チーム名を正式名称に統一しました。")


        df_23_24['NET EFF'] = df_23_24['OFF EFF'] - df_23_24['DEF EFF']
        df_24_25['NET EFF'] = df_24_25['OFF EFF'] - df_24_25['DEF EFF']
        print("NET EFF列の計算が完了しました。")

        df_24_25['PACE_rank'] = df_24_25['PACE'].rank(method='min', ascending=False)
        df_24_25['OFF EFF_rank'] = df_24_25['OFF EFF'].rank(method='min', ascending=False)
        df_24_25['DEF EFF_rank'] = df_24_25['DEF EFF'].rank(method='min', ascending=True) 
        print("2024-25シーズンのリーグ内ランクを計算しました。")

    except FileNotFoundError as e:
        print(f"エラー: データファイルが見つかりません。{e}")
        sys.exit(1)
    except KeyError as e:
        print(f"エラー: CSVファイルに必要な列が存在しません。{e}")
        sys.exit(1)
    
    try:
        df_players_24_25 = pd.read_csv("player_stats_2024-25.csv")
        team_abbr_map = {
            'ATL': 'Atlanta Hawks', 'BOS': 'Boston Celtics', 'BKN': 'Brooklyn Nets', 'CHA': 'Charlotte Hornets', 'CHI': 'Chicago Bulls',
            'CLE': 'Cleveland Cavaliers', 'DAL': 'Dallas Mavericks', 'DEN': 'Denver Nuggets', 'DET': 'Detroit Pistons', 'GS': 'Golden State Warriors',
            'HOU': 'Houston Rockets', 'IND': 'Indiana Pacers', 'LAC': 'LA Clippers', 'LAL': 'Los Angeles Lakers', 'MEM': 'Memphis Grizzlies',
            'MIA': 'Miami Heat', 'MIL': 'Milwaukee Bucks', 'MIN': 'Minnesota Timberwolves', 'NO': 'New Orleans Pelicans', 'NY': 'New York Knicks',
            'OKC': 'Oklahoma City Thunder', 'ORL': 'Orlando Magic', 'PHI': 'Philadelphia 76ers', 'PHX': 'Phoenix Suns', 'POR': 'Portland Trail Blazers',
            'SAC': 'Sacramento Kings', 'SA': 'San Antonio Spurs', 'TOR': 'Toronto Raptors', 'UTAH': 'Utah Jazz', 'WSH': 'Washington Wizards'
        }
        df_players_24_25['full_team_name'] = df_players_24_25['Team'].apply(lambda x: team_abbr_map.get(str(x).split('/')[-1].strip().upper()))
    except FileNotFoundError:
        df_players_24_25 = None
        print("警告: 選手データが見つかりませんでした。チームページの選手一覧は表示されません。")
        
    try:
        with open('youtube_videos.json', 'r') as f:
            video_data = json.load(f)
        print("youtube_videos.json の読み込みに成功しました。")
    except FileNotFoundError:
        video_data = {}
        print("警告: youtube_videos.jsonが見つかりません。動画は表示されません。")

    # ★★★ ここから追加 ★★★
    try:
        scoring_timeline_data = pd.read_csv('player_scoring_timeline.csv')
    except FileNotFoundError:
        scoring_timeline_data = pd.DataFrame() # ファイルがなくてもエラーにしない
        print("警告: player_scoring_timeline.csvが見つかりません。得点タイムラインは表示されません。")
    # ★★★ ここまで追加 ★★★

    # --- 3. Jinja2テンプレートエンジン初期化 ---
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    print("テンプレートエンジンの準備が完了しました。")

    # --- 4. 各種HTMLページの生成 ---
    generate_main_index(env)
    generate_glossary_page(env)
    generate_stat_pages(df_23_24, df_24_25, env)
    # ★★★ ここを修正 ★★★
    generate_comparison_pages(df_23_24, df_24_25, df_players_24_25, video_data, env)
    generate_player_pages(env, scoring_timeline_data)

    
    print("\n--- すべての処理が完了しました ---")