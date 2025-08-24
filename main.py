# main.py (UI/UX改修対応版)

import os
import sys
import pandas as pd
import jinja2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import re
import json
import unicodedata
import traceback

def is_file_up_to_date(output_path, dependencies):
    if not os.path.exists(output_path):
        return False
    output_mtime = os.path.getmtime(output_path)
    for dep in dependencies:
        if os.path.exists(dep) and os.path.getmtime(dep) > output_mtime:
            return False
    return True

def normalize_name(name):
    if not isinstance(name, str): return ""
    name = "".join(c for c in unicodedata.normalize('NFKD', name) if not unicodedata.combining(c))
    name = re.sub(r'\s+(Jr|Sr|II|III|IV|V)\.?$', '', name, flags=re.IGNORECASE)
    return name.strip()

CONFERENCE_STRUCTURE = { "Western Conference": { "Northwest Division": ["Denver Nuggets", "Minnesota Timberwolves", "Oklahoma City Thunder", "Portland Trail Blazers", "Utah Jazz"], "Pacific Division": ["Golden State Warriors", "LA Clippers", "Los Angeles Lakers", "Phoenix Suns", "Sacramento Kings"], "Southwest Division": ["Dallas Mavericks", "Houston Rockets", "Memphis Grizzlies", "New Orleans Pelicans", "San Antonio Spurs"] }, "Eastern Conference": { "Atlantic Division": ["Boston Celtics", "Brooklyn Nets", "New York Knicks", "Philadelphia 76ers", "Toronto Raptors"], "Central Division": ["Chicago Bulls", "Cleveland Cavaliers", "Detroit Pistons", "Indiana Pacers", "Milwaukee Bucks"], "Southeast Division": ["Atlanta Hawks", "Charlotte Hornets", "Miami Heat", "Orlando Magic", "Washington Wizards"] } }
TEAM_DETAILS = {
    "Atlanta Hawks": {"conference": "Eastern", "division": "Southeast", "arena": "State Farm Arena", "location": "ジョージア州アトランタ", "championships": 1},
    "Boston Celtics": {"conference": "Eastern", "division": "Atlantic", "arena": "TD Garden", "location": "マサチューセッツ州ボストン", "championships": 17},
    "Brooklyn Nets": {"conference": "Eastern", "division": "Atlantic", "arena": "Barclays Center", "location": "ニューヨーク州ブルックリン", "championships": 0},
    "Charlotte Hornets": {"conference": "Eastern", "division": "Southeast", "arena": "Spectrum Center", "location": "ノースカロライナ州シャーロット", "championships": 0},
    "Chicago Bulls": {"conference": "Eastern", "division": "Central", "arena": "United Center", "location": "イリノイ州シカゴ", "championships": 6},
    "Cleveland Cavaliers": {"conference": "Eastern", "division": "Central", "arena": "Rocket Mortgage FieldHouse", "location": "オハイオ州クリーブランド", "championships": 1},
    "Dallas Mavericks": {"conference": "Western", "division": "Southwest", "arena": "American Airlines Center", "location": "テキサス州ダラス", "championships": 1},
    "Denver Nuggets": {"conference": "Western", "division": "Northwest", "arena": "Ball Arena", "location": "コロラド州デンバー", "championships": 1},
    "Detroit Pistons": {"conference": "Eastern", "division": "Central", "arena": "Little Caesars Arena", "location": "ミシガン州デトロイト", "championships": 3},
    "Golden State Warriors": {"conference": "Western", "division": "Pacific", "arena": "Chase Center", "location": "カリフォルニア州サンフランシスコ", "championships": 7},
    "Houston Rockets": {"conference": "Western", "division": "Southwest", "arena": "Toyota Center", "location": "テキサス州ヒューストン", "championships": 2},
    "Indiana Pacers": {"conference": "Eastern", "division": "Central", "arena": "Gainbridge Fieldhouse", "location": "インディアナ州インディアナポリス", "championships": 0},
    "LA Clippers": {"conference": "Western", "division": "Pacific", "arena": "Intuit Dome", "location": "カリフォルニア州イングルウッド", "championships": 0},
    "Los Angeles Lakers": {"conference": "Western", "division": "Pacific", "arena": "Crypto.com Arena", "location": "カリフォルニア州ロサンゼルス", "championships": 17},
    "Memphis Grizzlies": {"conference": "Western", "division": "Southwest", "arena": "FedExForum", "location": "テネシー州メンフィス", "championships": 0},
    "Miami Heat": {"conference": "Eastern", "division": "Southeast", "arena": "Kaseya Center", "location": "フロリダ州マイアミ", "championships": 3},
    "Milwaukee Bucks": {"conference": "Eastern", "division": "Central", "arena": "Fiserv Forum", "location": "ウィスコンシン州ミルウォーキー", "championships": 2},
    "Minnesota Timberwolves": {"conference": "Western", "division": "Northwest", "arena": "Target Center", "location": "ミネソタ州ミネアポリス", "championships": 0},
    "New Orleans Pelicans": {"conference": "Western", "division": "Southwest", "arena": "Smoothie King Center", "location": "ルイジアナ州ニューオーリンズ", "championships": 0},
    "New York Knicks": {"conference": "Eastern", "division": "Atlantic", "arena": "Madison Square Garden", "location": "ニューヨーク州ニューヨーク", "championships": 2},
    "Oklahoma City Thunder": {"conference": "Western", "division": "Northwest", "arena": "Paycom Center", "location": "オクラホマ州オクラホマシティ", "championships": 1},
    "Orlando Magic": {"conference": "Eastern", "division": "Southeast", "arena": "Kia Center", "location": "フロリダ州オーランド", "championships": 0},
    "Philadelphia 76ers": {"conference": "Eastern", "division": "Atlantic", "arena": "Wells Fargo Center", "location": "ペンシルベニア州フィラデルフィア", "championships": 3},
    "Phoenix Suns": {"conference": "Western", "division": "Pacific", "arena": "Footprint Center", "location": "アリゾナ州フェニックス", "championships": 0},
    "Portland Trail Blazers": {"conference": "Western", "division": "Northwest", "arena": "Moda Center", "location": "オレゴン州ポートランド", "championships": 1},
    "Sacramento Kings": {"conference": "Western", "division": "Pacific", "arena": "Golden 1 Center", "location": "カリフォルニア州サクラメント", "championships": 1},
    "San Antonio Spurs": {"conference": "Western", "division": "Southwest", "arena": "Frost Bank Center", "location": "テキサス州サンアントニオ", "championships": 5},
    "Toronto Raptors": {"conference": "Eastern", "division": "Atlantic", "arena": "Scotiabank Arena", "location": "オンタリオ州トロント", "championships": 1},
    "Utah Jazz": {"conference": "Western", "division": "Northwest", "arena": "Delta Center", "location": "ユタ州ソルトレイクシティ", "championships": 0},
    "Washington Wizards": {"conference": "Eastern", "division": "Southeast", "arena": "Capital One Arena", "location": "ワシントンD.C.", "championships": 1}
}
STATS_TO_GENERATE = { 'PACE': 'Pace', 'AST': 'Assist Ratio', 'TO': 'Turnover Ratio', 'ORR': 'Off Rebound Rate', 'DRR': 'Def Rebound Rate', 'TS%': 'True Shooting %', 'OFF EFF': 'Offensive Efficiency', 'DEF EFF': 'Defensive Efficiency', 'NET EFF': 'Net Rating' }
TEAM_NAME_MAP = { "Atlanta": "Atlanta Hawks", "Boston": "Boston Celtics", "Brooklyn": "Brooklyn Nets", "Charlotte": "Charlotte Hornets", "Chicago": "Chicago Bulls", "Cleveland": "Cleveland Cavaliers", "Dallas": "Dallas Mavericks", "Denver": "Denver Nuggets", "Detroit": "Detroit Pistons", "Golden State": "Golden State Warriors", "Houston": "Houston Rockets", "Indiana": "Indiana Pacers", "LA Clippers": "LA Clippers", "LA Lakers": "Los Angeles Lakers", "Memphis": "Memphis Grizzlies", "Miami": "Miami Heat", "Milwaukee": "Milwaukee Bucks", "Minnesota": "Minnesota Timberwolves", "New Orleans": "New Orleans Pelicans", "New York": "New York Knicks", "Oklahoma City": "Oklahoma City Thunder", "Orlando": "Orlando Magic", "Philadelphia": "Philadelphia 76ers", "Phoenix": "Phoenix Suns", "Portland": "Portland Trail Blazers", "Sacramento": "Sacramento Kings", "San Antonio": "San Antonio Spurs", "Toronto": "Toronto Raptors", "Utah": "Utah Jazz", "Washington": "Washington Wizards" }

# ★★★ 追加 ★★★
# CSSのチームテーマクラス名と紐付けるための略称マッピング
TEAM_ABBREVIATIONS = {
    "Atlanta Hawks": "atl", "Boston Celtics": "bos", "Brooklyn Nets": "bkn", "Charlotte Hornets": "cha",
    "Chicago Bulls": "chi", "Cleveland Cavaliers": "cle", "Dallas Mavericks": "dal", "Denver Nuggets": "den",
    "Detroit Pistons": "det", "Golden State Warriors": "gsw", "Houston Rockets": "hou", "Indiana Pacers": "ind",
    "LA Clippers": "lac", "Los Angeles Lakers": "lal", "Memphis Grizzlies": "mem", "Miami Heat": "mia",
    "Milwaukee Bucks": "mil", "Minnesota Timberwolves": "min", "New Orleans Pelicans": "nop", "New York Knicks": "nyk",
    "Oklahoma City Thunder": "okc", "Orlando Magic": "orl", "Philadelphia 76ers": "phi", "Phoenix Suns": "phx",
    "Portland Trail Blazers": "por", "Sacramento Kings": "sac", "San Antonio Spurs": "sas", "Toronto Raptors": "tor",
    "Utah Jazz": "uta", "Washington Wizards": "was"
}

def get_footer_data(base_path):
    stat_pages = [{'name': en_full, 'url': f"{base_path}/stats/{en_short.replace('%', '_PCT').replace(' ', '_')}.html"} for en_short, en_full in STATS_TO_GENERATE.items()]
    all_teams_structured = {}
    for conf, divisions in CONFERENCE_STRUCTURE.items():
        all_teams_structured[conf] = {}
        for div, teams_in_div in divisions.items():
            all_teams_structured[conf][div] = [{'name': team, 'url': f"{base_path}/teams/{team.replace(' ', '-').lower()}.html"} for team in teams_in_div]
    return stat_pages, all_teams_structured

def generate_main_index(env, base_path, df_teams_s1, df_teams_s2, df_players_s1, df_players_s2, video_data):
    print("--- トップページの生成開始 ---")
    template = env.get_template('index_template.html')
    top_teams_by_stat = {}
    team_stats_to_show = {'OFF EFF': 'オフェンス効率', 'DEF EFF': 'ディフェンス効率', 'PACE': 'ペース'}
    if df_teams_s1 is not None and df_teams_s2 is not None:
        df_teams_merged = pd.merge(df_teams_s2, df_teams_s1, on='Team', suffixes=('_s2', '_s1'), how='left')
        for stat, name in team_stats_to_show.items():
            stat_key_s2, stat_key_s1, stat_key_change = f'{stat}_s2', f'{stat}_s1', f'{stat}_change'
            sort_asc = True if stat in ['DEF EFF', 'TO'] else False
            df_teams_merged[stat_key_change] = df_teams_merged[stat_key_s2] - df_teams_merged[stat_key_s1]
            top_5_teams = df_teams_merged.sort_values(by=stat_key_s2, ascending=sort_asc).head(5)
            team_data_list = [{'Team': row['Team'], 'url': f"{base_path}/teams/{row['Team'].replace(' ', '-').lower()}.html", 'value': row[stat_key_s2], 'change': row[stat_key_change]} for _, row in top_5_teams.iterrows()]
            top_teams_by_stat[name] = {'data': team_data_list, 'url': f"{base_path}/stats/{stat.replace('%', '_PCT').replace(' ', '_')}.html"}
    top_players_by_stat = {}
    player_stats_to_show = {'PTS': '得点', 'REB': 'リバウンド', 'AST': 'アシスト'}
    if df_players_s1 is not None and df_players_s2 is not None:
        df_players_merged = pd.merge(df_players_s2, df_players_s1, on='Player', how='left', suffixes=('_s2', '_s1'))
        for stat, name in player_stats_to_show.items():
            stat_key_s2, stat_key_s1, stat_key_change = f'{stat}_s2', f'{stat}_s1', f'{stat}_change'
            for col in [stat_key_s1, stat_key_s2]: df_players_merged[col] = pd.to_numeric(df_players_merged[col], errors='coerce')
            df_players_merged[stat_key_change] = df_players_merged[stat_key_s2] - df_players_merged[stat_key_s1].fillna(0)
            top_5_players = df_players_merged.sort_values(by=stat_key_s2, ascending=False).head(5)
            player_data_list = []
            for _, row in top_5_players.iterrows():
                player_filename = re.sub(r'[^a-zA-Z0-9 -]', '', row['Player']).replace(' ', '-').lower()
                player_url = f"{base_path}/players/{player_filename}.html"
                player_data_list.append({'Player': row['Player'], 'url': player_url, 'value': row[stat_key_s2], 'change': row[stat_key_change]})
            top_players_by_stat[name] = {'data': player_data_list, 'url': f"{base_path}/2024-25/index.html"}
    main_video_id = video_data.get("NBA_MAIN")
    main_video_embed_url = f"https://www.youtube.com/embed/{main_video_id}" if main_video_id else None
    stat_pages_footer, all_teams_structured_footer = get_footer_data(base_path)
    render_data = {
        'base_path': base_path, 'page_title': "NBAスタッツ分析サイト", 'meta_description': "最新のNBAチームスタッツと選手スタッツを分析・可視化します。",
        'top_teams_by_stat': top_teams_by_stat, 'top_players_by_stat': top_players_by_stat, 'main_video_embed_url': main_video_embed_url,
        'stat_pages': stat_pages_footer, 'all_teams_structured': all_teams_structured_footer
    }
    with open("output/index.html", "w", encoding="utf-8") as f: f.write(template.render(render_data))
    print("--- トップページの生成完了 ---")

def generate_glossary_page(env, base_path):
    print("--- 指標解説ページの生成開始 ---")
    template = env.get_template('glossary_template.html')
    glossary_items = [{'term': 'Pace', 'description': '1試合あたり48分間のポゼッション（攻撃回数）の推定値。'}, {'term': 'Offensive Efficiency (OFF EFF)', 'description': '100ポゼッションあたりの得点。'}, {'term': 'Defensive Efficiency (DEF EFF)', 'description': '100ポゼッションあたりの失点。'}, {'term': 'Net Rating (NET EFF)', 'description': 'Offensive EfficiencyとDefensive Efficiencyの差。'}, {'term': 'True Shooting % (TS%)', 'description': 'フィールドゴール、3ポイント、フリースローを総合的に評価したシュート効率。'}, {'term': 'Assist Ratio (AST)', 'description': 'チームのフィールドゴール成功のうち、アシストが占める割合。'}, {'term': 'Turnover Ratio (TO)', 'description': '100ポゼッションあたりのターンオーバー数。'}, {'term': 'Off Rebound Rate (ORR)', 'description': 'オフェンスリバウンド機会のうち、実際にリバウンドを獲得した割合。'}, {'term': 'Def Rebound Rate (DRR)', 'description': 'ディフェンスリバウンド機会のうち、実際にリバウンドを獲得した割合。'}]
    stat_pages_footer, all_teams_structured_footer = get_footer_data(base_path)
    render_data = {
        'base_path': base_path, 'page_title': "指標解説 | NBAスタッツ分析サイト", 'meta_description': "NBAの各統計指標（Pace, Offensive Efficiencyなど）の意味を詳しく解説します。",
        'glossary_items': glossary_items, 'stat_pages': stat_pages_footer, 'all_teams_structured': all_teams_structured_footer
    }
    with open("output/glossary.html", "w", encoding="utf-8") as f: f.write(template.render(render_data))
    print("--- 指標解説ページの生成完了 ---")

def generate_team_pages(df_s1, df_s2, df_players, video_data, env, player_team_map, base_path):
    print("--- チーム別比較ページの生成開始 ---")
    df_s1_indexed = df_s1.set_index('Team')
    df_s2_indexed = df_s2.set_index('Team')
    all_teams = sorted(list(df_s1_indexed.index.union(df_s2_indexed.index)))
    template = env.get_template('team_template.html')
    stats_to_compare = ['PACE', 'OFF EFF', 'DEF EFF', 'NET EFF', 'TS%', 'AST', 'TO']
    stat_pages_footer, all_teams_structured_footer = get_footer_data(base_path)
    inverse_stats = ['DEF EFF', 'TO']
    active_players_s2 = set(df_players['Player']) if df_players is not None else set()

    for team in all_teams:
        try:
            team_filename = team.replace(' ', '-').lower()
            output_path = f"output/teams/{team_filename}.html"
            
            stats1 = df_s1_indexed.loc[team]
            stats2 = df_s2_indexed.loc[team]
            pct_change = ((stats2 - stats1) / stats1.abs()).fillna(0) * 100
            
            summary = generate_team_summary(stats1, stats2)
            player_list = []
            if player_team_map:
                for player_name, player_team in player_team_map.items():
                    if player_team == team and player_name in active_players_s2:
                        player_filename_p = re.sub(r'[^a-zA-Z0-9 -]', '', player_name).replace(' ', '-').lower()
                        player_list.append({'name': player_name, 'url': f"{base_path}/players/{player_filename_p}.html"})
            
            video_id = video_data.get(team)
            video_embed_url = f"https://www.youtube.com/embed/{video_id}" if video_id else None

            render_data = {
                'base_path': base_path, 'page_title': f"{team} | チームスタッツ分析", 'meta_description': f"{team}のシーズンスタッツ、選手一覧、最新情報を分析。",
                'team_name': team, 'team_class': f"team-{TEAM_ABBREVIATIONS.get(team, '')}",
                'stats_s1': stats1, 'stats_s2': stats2, 'pct_change': pct_change, 'inverse_stats': inverse_stats,
                'details': TEAM_DETAILS.get(team, {}), 'summary_text': summary, 'player_list': player_list, 'video_embed_url': video_embed_url,
                'stat_pages': stat_pages_footer, 'all_teams_structured': all_teams_structured_footer
            }
            with open(output_path, "w", encoding="utf-8") as f: f.write(template.render(render_data))
        except Exception as e: print(f"警告: {team} の比較ページ生成中にエラーが発生しました。詳細: {e}")
    print("--- チーム別比較ページの生成完了 ---")

# (generate_stat_pages, generate_player_pages, generate_season_player_index は後続で)
# ...