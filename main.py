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
import shutil

def create_player_filename(player_name):
    """選手名から安全なファイル名を生成する"""
    s = str(player_name).strip()
    # 既存のロジックをベースに、より安全なファイル名を生成する
    filename = re.sub(r'[^a-zA-Z0-9 -]', '', s).replace(' ', '-').lower()
    # 連続するハイフンを1つにまとめる
    filename = re.sub(r'-+', '-', filename)
    # 先頭と末尾のハイフンを削除
    filename = filename.strip('-')
    # 結果が空になった場合のフォールバック
    return filename if filename else "unknown-player"

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
    return [{'name': en_full, 'url': f"{base_path}/stats/{en_short.replace('%', '_PCT').replace(' ', '_')}.html"} for en_short, en_full in STATS_TO_GENERATE.items()]

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
                player_filename = create_player_filename(row['Player'])
                player_url = f"{base_path}/players/{player_filename}.html"
                player_data_list.append({'Player': row['Player'], 'url': player_url, 'value': row[stat_key_s2], 'change': row[stat_key_change]})
            top_players_by_stat[name] = {'data': player_data_list, 'url': f"{base_path}/2024-25/index.html"}
    main_video_id = video_data.get("NBA_MAIN")
    main_video_embed_url = f"https://www.youtube.com/embed/{main_video_id}" if main_video_id else None
    stat_pages_footer = get_footer_data(base_path)
    render_data = {
        'base_path': base_path, 'page_title': "NBA Stats Media - チーム＆選手スタッツ比較サイト", 'meta_description': "NBAのチームと選手の詳細なスタッツを比較・分析。2023-24シーズンと2024-25シーズンのデータを基に、パフォーマンスの変動や特徴を可視化します。",
        'top_teams_by_stat': top_teams_by_stat, 'top_players_by_stat': top_players_by_stat, 'main_video_embed_url': main_video_embed_url,
        'stat_pages': stat_pages_footer, 'glossary_url': f'{base_path}/glossary.html'
    }
    with open("output/index.html", "w", encoding="utf-8") as f: f.write(template.render(render_data))
    print("--- トップページの生成完了 ---")

def generate_glossary_page(env, base_path):
    print("--- 指標解説ページの生成開始 ---")
    template = env.get_template('glossary_template.html')
    glossary_items = [{'term': 'Pace', 'description': '1試合あたり48分間のポゼッション（攻撃回数）の推定値。'}, {'term': 'Offensive Efficiency (OFF EFF)', 'description': '100ポゼッションあたりの得点。'}, {'term': 'Defensive Efficiency (DEF EFF)', 'description': '100ポゼッションあたりの失点。'}, {'term': 'Net Rating (NET EFF)', 'description': 'Offensive EfficiencyとDefensive Efficiencyの差。'}, {'term': 'True Shooting % (TS%)', 'description': 'フィールドゴール、3ポイント、フリースローを総合的に評価したシュート効率。'}, {'term': 'Assist Ratio (AST)', 'description': 'チームのフィールドゴール成功のうち、アシストが占める割合。'}, {'term': 'Turnover Ratio (TO)', 'description': '100ポゼッションあたりのターンオーバー数。'}, {'term': 'Off Rebound Rate (ORR)', 'description': 'オフェンスリバウンド機会のうち、実際にリバウンドを獲得した割合。'}, {'term': 'Def Rebound Rate (DRR)', 'description': 'ディフェンスリバウンド機会のうち、実際にリバウンドを獲得した割合。'}]
    stat_pages_footer = get_footer_data(base_path)
    render_data = {
        'base_path': base_path, 'page_title': "指標の解説 (Glossary) | NBA Stats", 'meta_description': "NBAの各統計指標（Pace, Offensive Efficiencyなど）の意味を詳しく解説します。",
        'glossary_items': glossary_items, 'stat_pages': stat_pages_footer
    }
    with open("output/glossary.html", "w", encoding="utf-8") as f: f.write(template.render(render_data))
    print("--- 指標解説ページの生成完了 ---")

def generate_team_pages(df_s1, df_s2, df_players, video_data, env, player_team_map, base_path):
    print("--- チーム別ページの生成開始 ---")
    df_s1_indexed = df_s1.set_index('Team')
    df_s2_indexed = df_s2.set_index('Team')
    all_teams = sorted(list(df_s1_indexed.index.union(df_s2_indexed.index)))
    template = env.get_template('team_template.html')
    stat_pages_footer = get_footer_data(base_path)
    inverse_stats = ['DEF EFF', 'TO']
    active_players_s2 = set(df_players['Player']) if df_players is not None else set()

    for team in all_teams:
        try:
            team_filename_slug = team.replace(' ', '-').lower()
            output_path = f"output/teams/{team_filename_slug}.html"
            
            stats1 = df_s1_indexed.loc[team]
            stats2 = df_s2_indexed.loc[team]
            pct_change = ((stats2 - stats1) / stats1.abs()).fillna(0) * 100
            
            stats_to_compare = ['PACE', 'OFF EFF', 'DEF EFF', 'NET EFF', 'TS%', 'AST', 'TO']
            stats_for_graph1 = stats1[stats_to_compare]
            stats_for_graph2 = stats2[stats_to_compare]
            x = np.arange(len(stats_to_compare)); width = 0.35
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(x - width/2, stats_for_graph1, width, label='2023-24')
            ax.bar(x + width/2, stats_for_graph2, width, label='2024-25')
            ax.set_ylabel('Value'); ax.set_title(f'Key Stats Comparison: {team}')
            ax.set_xticks(x); ax.set_xticklabels(stats_to_compare, rotation=45, ha="right"); ax.legend(); fig.tight_layout()
            plt.savefig(f"output/images/comparison_{team.replace(' ', '_')}.svg", format="svg"); plt.close(fig)
            
            player_list = []
            if player_team_map:
                for player_name, player_team in player_team_map.items():
                    if player_team == team and player_name in active_players_s2:
                        player_filename_p = create_player_filename(player_name)
                        player_list.append({'name': player_name, 'url': f"{base_path}/players/{player_filename_p}.html"})
            
            video_id = video_data.get(team)
            video_embed_url = f"https://www.youtube.com/embed/{video_id}" if video_id else None

            render_data = {
                'base_path': base_path, 'page_title': f"{team} | チームスタッツ分析", 'meta_description': f"{team}のシーズンスタッツ、選手一覧、最新情報を分析。",
                'team_name': team, 'team_class': f"team-{TEAM_ABBREVIATIONS.get(team, '')}",
                'stats_s1': stats1, 'stats_s2': stats2, 'pct_change': pct_change, 'inverse_stats': inverse_stats,
                'details': TEAM_DETAILS.get(team, {}), 'player_list': player_list, 'video_embed_url': video_embed_url,
                'stat_pages': stat_pages_footer
            }
            with open(output_path, "w", encoding="utf-8") as f: f.write(template.render(render_data))
        except Exception as e: print(f"警告: {team} のページ生成中にエラーが発生しました。詳細: {e}")
    print("--- チーム別ページの生成完了 ---")

def generate_stat_pages(df_s1, df_s2, env, base_path):
    print("--- 指標別ランキングページの生成開始 ---")
    template = env.get_template('stat_template.html')
    for stat_short, stat_full in STATS_TO_GENERATE.items():
        try:
            sort_ascending = True if stat_short in ('DEF EFF', 'TO') else False
            df_merged = pd.merge(df_s1[['Team', stat_short]], df_s2[['Team', stat_short]], on='Team', suffixes=('_s1', '_s2')).set_index('Team').sort_values(by=f"{stat_short}_s2", ascending=sort_ascending)
            stat_filename = stat_short.replace('%', '_PCT').replace(' ', '_')
            
            fig, ax = plt.subplots(figsize=(10, 14))
            y = np.arange(len(df_merged.index)); height = 0.4
            ax.barh(y + height/2, df_merged[f'{stat_short}_s1'], height, label='2023-24'); ax.barh(y - height/2, df_merged[f'{stat_short}_s2'], height, label='2024-25')
            ax.set_xlabel('Value'); ax.set_title(f'All Teams Comparison: {stat_full}'); ax.set_yticks(y); ax.set_yticklabels(df_merged.index); ax.invert_yaxis(); ax.legend(); fig.tight_layout()
            plt.savefig(f"output/images/stat_{stat_filename}.svg", format="svg"); plt.close(fig)

            stat_pages_footer = get_footer_data(base_path)
            render_data = {
                'base_path': base_path, 'page_title': f"指標別比較: {stat_full} | NBA Stats", 'meta_description': f"全NBAチームの{stat_full}を2023-24と2024-25シーズンで比較ランキング。",
                'stat_name_jp': stat_full, 'stat_name_en': stat_filename, 'data_table': df_merged.rename(columns={f'{stat_short}_s1': '2023-24', f'{stat_short}_s2': '2024-25'}),
                'stat_pages': stat_pages_footer
            }
            output_path = f"output/stats/{stat_filename}.html"
            with open(output_path, "w", encoding="utf-8") as f: f.write(template.render(render_data))
        except Exception as e: print(f"エラー: {stat_full} のページ生成中に問題が発生しました: {e}")
    print("--- 指標別ランキングページの生成完了 ---")

def generate_player_pages(env, scoring_timeline_data, df_s1_raw, df_s2_raw, player_team_map, base_path):
    print("--- 選手ページの生成開始 ---")
    if df_s1_raw is None or df_s2_raw is None: return

    def generate_player_comment(player_name, season_str_long, player_season_timeline):
        if player_season_timeline.empty: return f"{player_name}選手の{season_str_long}シーズンの詳細な得点データはありません。"
        point_map = {'3PT': 3, '2PT': 2, 'FT': 1}; made_shots = player_season_timeline[player_season_timeline['MADE_FLAG'] == 1].copy()
        if made_shots.empty: return f"{player_name}選手は{season_str_long}シーズン、このデータセットでは得点記録がありません。"
        made_shots['POINTS'] = made_shots['SHOT_TYPE'].map(point_map)
        q1_points = made_shots[made_shots['absolute_minute'] < 12]['POINTS'].sum(); q2_points = made_shots[(made_shots['absolute_minute'] >= 12) & (made_shots['absolute_minute'] < 24)]['POINTS'].sum(); q3_points = made_shots[(made_shots['absolute_minute'] >= 24) & (made_shots['absolute_minute'] < 36)]['POINTS'].sum(); q4_points = made_shots[made_shots['absolute_minute'] >= 36]['POINTS'].sum()
        total_points = made_shots['POINTS'].sum()
        if total_points == 0: return f"{player_name}選手は{season_str_long}シーズン、このデータセットでは得点記録がありません。"
        points_per_quarter = {1: q1_points, 2: q2_points, 3: q3_points, 4: q4_points}; best_quarter = max(points_per_quarter, key=points_per_quarter.get)
        shot_attempts = player_season_timeline['SHOT_TYPE'].value_counts(normalize=True); primary_style = "バランスの取れた攻撃が持ち味"
        if shot_attempts.get('3PT', 0) > 0.4: primary_style = "3ポイントシュートを多用するプレースタイル"
        elif shot_attempts.get('2PT', 0) > 0.55: primary_style = "2ポイントエリアでの得点を主体とするプレースタイル"
        comment_parts = []
        if best_quarter == 4 and (q4_points / total_points) > 0.3: comment_parts.append(f"{player_name}選手は、試合の勝敗が決まる第4クォーターに最も得点を集中させるクラッチパフォーマーです。")
        elif best_quarter == 1 and (q1_points / total_points) > 0.3: comment_parts.append(f"{player_name}選手は、試合序盤から積極的に得点を狙うスタートダッシュ型の選手です。")
        else: comment_parts.append(f"{player_name}選手は、シーズンを通して安定したパフォーマンスを見せ、特に第{best_quarter}クォーターで最も多くの得点を記録しています。")
        comment_parts.append(f"強みは{primary_style}です。"); return " ".join(comment_parts)
    
    def get_scoring_by_minute(timeline_df):
        made_shots = timeline_df[timeline_df['MADE_FLAG'] == 1].copy()
        if made_shots.empty: return pd.DataFrame()
        point_map = {'3PT': 3, '2PT': 2, 'FT': 1}
        made_shots['POINTS'] = made_shots['SHOT_TYPE'].map(point_map)
        made_shots['minute_bin'] = np.floor(made_shots['absolute_minute'])
        scoring_df = pd.pivot_table(made_shots, values='POINTS', index='minute_bin', columns='SHOT_TYPE', aggfunc='sum').fillna(0)
        for col in ['FT', '2PT', '3PT']:
            if col not in scoring_df.columns: scoring_df[col] = 0
        return scoring_df

    df_merged = pd.merge(df_s2_raw, df_s1_raw, on='Player', how='left', suffixes=('_s2', '_s1'))
    template = env.get_template('player_template.html')
    stat_pages_footer = get_footer_data(base_path)

    for index, player_data in df_merged.iterrows():
        player_name = player_data.get('Player', 'Unknown')
        try:
            player_filename = create_player_filename(player_name)
            output_path = f"output/players/{player_filename}.html"
            
            stats_s2_raw = player_data.filter(like='_s2').rename(lambda x: x.replace('_s2', ''))
            stats_s1_raw = player_data.filter(like='_s1').rename(lambda x: x.replace('_s1', ''))
            
            team_name = player_team_map.get(player_name, '')
            team_url = f"{base_path}/teams/{team_name.replace(' ', '-').lower()}.html" if team_name else ""
            team_class = f"team-{TEAM_ABBREVIATIONS.get(team_name, '')}" if team_name else ""
            
            render_data = { 
                'base_path': base_path, 'page_title': f"{player_name} | 選手スタッツ分析", 'meta_description': f"{player_name}選手のシーズン別スタッツと時間帯別得点パターンを分析。",
                'player_name': player_name, 'player_filename': player_filename, 
                'stats_s1': stats_s1_raw.to_dict(), 'stats_s2': stats_s2_raw.to_dict(),
                'team_name': team_name, 'team_url': team_url, 'team_class': team_class,
                'has_timeline_23_24': False, 'has_timeline_24_25': False, 'has_timeline_comparison': False,
                'stat_pages': stat_pages_footer
            }

            timeline_data_23_24 = scoring_timeline_data[(scoring_timeline_data['Player'] == player_name) & (scoring_timeline_data['Season'] == '2023-24')]
            timeline_data_24_25 = scoring_timeline_data[(scoring_timeline_data['Player'] == player_name) & (scoring_timeline_data['Season'] == '2024-25')]
            
            if not timeline_data_24_25.empty:
                render_data['has_timeline_24_25'] = True
                render_data['comment_24_25'] = generate_player_comment(player_name, '2024-25', timeline_data_24_25)
            
            if not timeline_data_23_24.empty:
                render_data['has_timeline_23_24'] = True
                render_data['comment_23_24'] = generate_player_comment(player_name, '2023-24', timeline_data_23_24)

            if render_data['has_timeline_23_24'] and render_data['has_timeline_24_25']:
                scoring_23_24 = get_scoring_by_minute(timeline_data_23_24)
                scoring_24_25 = get_scoring_by_minute(timeline_data_24_25)

                if not scoring_23_24.empty and not scoring_24_25.empty:
                    render_data['has_timeline_comparison'] = True
            
            with open(output_path, "w", encoding="utf-8") as f: f.write(template.render(render_data))
        except Exception as e:
            print(f"警告: {player_name} のページ生成中にエラー: {e}")
            traceback.print_exc()
    print("--- 選手ページの生成完了 ---")

def generate_season_player_index(env, base_path, season_str, df_current, df_previous):
    print(f"--- {season_str}シーズン 選手ランキングページの生成開始 ---")
    template = env.get_template('season_player_index_template.html')
    if df_current is None:
        print(f"警告: {season_str}の選手データがないため、ランキングページをスキップします。")
        return
    if df_previous is None:
        df_previous = pd.DataFrame(columns=df_current.columns)

    player_stats_to_show = {'PTS': '得点', 'REB': 'リバウンド', 'AST': 'アシスト'}
    df_merged = pd.merge(df_current, df_previous, on='Player', how='left', suffixes=('_current', '_previous'))
    leaders_by_stat = {}
    
    for stat, name in player_stats_to_show.items():
        stat_key_current, stat_key_previous, stat_key_change = f'{stat}_current', f'{stat}_previous', f'{stat}_change'
        for col in [stat_key_current, stat_key_previous]: 
            df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce')
        df_merged[stat_key_change] = df_merged[stat_key_current] - df_merged[stat_key_previous].fillna(0)
        top_10_players = df_merged.sort_values(by=stat_key_current, ascending=False).head(10)
        
        player_data_list = []
        
        for _, row in top_10_players.iterrows():
            player_filename = create_player_filename(row['Player'])
            player_url = f"{base_path}/players/{player_filename}.html"
            player_data_list.append({
                'Player': row['Player'], 
                'url': player_url, 
                'value': row[stat_key_current], 
                'change': row[stat_key_change]
            })
        leaders_by_stat[name] = player_data_list

    stat_pages_footer = get_footer_data(base_path)
    render_data = {
        'base_path': base_path, 'season_str': season_str,
        'page_title': f"NBA {season_str}シーズン | 選手スタッツリーダー", 
        'meta_description': f"NBA {season_str}シーズンの主要スタッツ（得点、リバウンド、アシストなど）におけるトップ10選手ランキング。",
        'leaders_by_stat': leaders_by_stat, 'stat_pages': stat_pages_footer
    }
    output_path = f"output/{season_str}/index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template.render(render_data))
    print(f"--- {season_str}シーズン 選手ランキングページの生成完了 ---")

if __name__ == "__main__":
    print("--- HTML生成スクリプトを開始します ---")
    base_path = "/nba-stats-media"
    
    # サイトの全ディレクトリを確実に作成
    os.makedirs("output/teams", exist_ok=True)
    os.makedirs("output/images", exist_ok=True)
    os.makedirs("output/stats", exist_ok=True)
    os.makedirs("output/logos", exist_ok=True)
    os.makedirs("output/css", exist_ok=True)
    os.makedirs("output/js", exist_ok=True)
    os.makedirs("output/players", exist_ok=True)
    os.makedirs("output/images/players", exist_ok=True)
    os.makedirs("output/2023-24", exist_ok=True)
    os.makedirs("output/2024-25", exist_ok=True)
    os.makedirs("output/images/season_leaders", exist_ok=True)
    print("出力ディレクトリの準備が完了しました。")

    print("--- 静的ファイルのコピーを開始します ---")
    if os.path.exists('css'):
        shutil.copytree('css', 'output/css', dirs_exist_ok=True)
    if os.path.exists('js'):
        shutil.copytree('js', 'output/js', dirs_exist_ok=True)
    if os.path.exists('logos'):
        shutil.copytree('logos', 'output/logos', dirs_exist_ok=True)
    print("--- 静的ファイルのコピーが完了しました ---")

    try:
        df_23_24 = pd.read_csv("espn_team_stats_2023-24.csv")
        df_24_25 = pd.read_csv("espn_team_stats_2024-25.csv")
        df_23_24['Team'] = df_23_24['Team'].replace(TEAM_NAME_MAP)
        df_24_25['Team'] = df_24_25['Team'].replace(TEAM_NAME_MAP)
        df_23_24['NET EFF'] = df_23_24['OFF EFF'] - df_23_24['DEF EFF']
        df_24_25['NET EFF'] = df_24_25['OFF EFF'] - df_24_25['DEF EFF']
        df_24_25['PACE_rank'] = df_24_25['PACE'].rank(method='min', ascending=False)
        df_24_25['OFF EFF_rank'] = df_24_25['OFF EFF'].rank(method='min', ascending=False)
        df_24_25['DEF EFF_rank'] = df_24_25['DEF EFF'].rank(method='min', ascending=True)
    except FileNotFoundError as e:
        print(f"エラー: チーム統計ファイルが見つかりません: {e}")
        sys.exit(1)
    
    df_players_23_24, df_players_24_25, player_team_map = None, None, {}
    try:
        df_players_23_24 = pd.read_csv("player_stats_2023-24.csv")
        df_players_23_24['Player'] = df_players_23_24['Player'].apply(normalize_name)
    except FileNotFoundError: df_players_23_24 = None
    try:
        df_players_24_25 = pd.read_csv("player_stats_2024-25.csv")
        df_players_24_25['Player'] = df_players_24_25['Player'].apply(normalize_name)
    except FileNotFoundError: df_players_24_25 = None
    try:
        roster_df = pd.read_csv("player_team_map.csv")
        roster_df['Player'] = roster_df['Player'].apply(normalize_name)
        player_team_map = pd.Series(roster_df.Team.values, index=roster_df.Player).to_dict()
    except FileNotFoundError: player_team_map = {}
    try:
        with open('youtube_videos.json', 'r') as f: video_data = json.load(f)
    except FileNotFoundError: video_data = {}
    try:
        scoring_timeline_data = pd.read_csv('player_scoring_timeline.csv')
        scoring_timeline_data['Player'] = scoring_timeline_data['Player'].apply(normalize_name)
    except FileNotFoundError: scoring_timeline_data = pd.DataFrame()

    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    
    generate_main_index(env, base_path, df_23_24, df_24_25, df_players_23_24, df_players_24_25, video_data)
    generate_glossary_page(env, base_path)
    generate_team_pages(df_23_24, df_24_25, df_players_24_25, video_data, env, player_team_map, base_path)
    generate_stat_pages(df_23_24, df_24_25, env, base_path)
    generate_player_pages(env, scoring_timeline_data, df_players_23_24, df_players_24_25, player_team_map, base_path)
    generate_season_player_index(env, base_path, '2024-25', df_players_24_25, df_players_23_24)
    generate_season_player_index(env, base_path, '2023-24', df_players_23_24, df_players_24_25)

    print("\n--- すべての処理が完了しました ---")