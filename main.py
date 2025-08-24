# main.py (シーズン比較グラフ追加版)

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

# (is_file_up_to_date, normalize_name, 各種定数 は変更なし)
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

# (generate_team_summaryからgenerate_stat_pagesまでは変更なし)
def generate_team_summary(s1_stats, s2_stats):
    if s2_stats.empty: return ""
    STAT_INFO = { 'OFF EFF': {'jp': 'オフェンス'}, 'DEF EFF': {'jp': 'ディフェンス'}, 'PACE': {'jp': '試合のペース'} }
    ranks = { 'OFF EFF': s2_stats['OFF EFF_rank'], 'DEF EFF': s2_stats['DEF EFF_rank'], 'PACE': s2_stats['PACE_rank'] }
    best_strength_stat, best_rank = min(ranks.items(), key=lambda item: item[1])
    biggest_challenge_stat, worst_rank = max(ranks.items(), key=lambda item: item[1])
    positive_sentence, challenge_sentence = "", ""
    if best_rank <= 10:
        strength_desc = "リーグ屈指の" if best_rank <= 5 else "リーグ上位の"
        positive_sentence = f"今シーズンのチームの最大の武器は、{strength_desc}{STAT_INFO[best_strength_stat]['jp']}です。"
    else: positive_sentence = "今シーズンは攻守両面でバランスの取れた、安定感のあるパフォーマンスを見せています。"
    if worst_rank >= 21 and best_strength_stat != biggest_challenge_stat:
        challenge_desc = "リーグ下位に苦しむ" if worst_rank >= 26 else "改善が待たれる"
        challenge_sentence = f"一方で、今後の更なる飛躍のためには、{challenge_desc}{STAT_INFO[biggest_challenge_stat]['jp']}の立て直しが鍵となるでしょう。"
    else: challenge_sentence = "この安定感をシーズン通して維持し、さらに一段階レベルアップできれば、素晴らしい結果が期待できます。"
    return positive_sentence + " " + challenge_sentence
def get_footer_data(base_path):
    stat_pages = [{'name': en_full, 'url': f"{base_path}/stats/{en_short.replace('%', '_PCT').replace(' ', '_')}.html"} for en_short, en_full in STATS_TO_GENERATE.items()]
    all_teams_structured = {}
    for conf, divisions in CONFERENCE_STRUCTURE.items():
        all_teams_structured[conf] = {}
        for div, teams_in_div in divisions.items():
            all_teams_structured[conf][div] = [{'name': team, 'url': f"{base_path}/teams/comparison_{team.replace(' ', '_')}.html"} for team in teams_in_div]
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
            team_data_list = [{'Team': row['Team'], 'url': f"{base_path}/teams/comparison_{row['Team'].replace(' ', '_')}.html", 'value': row[stat_key_s2], 'change': row[stat_key_change]} for _, row in top_5_teams.iterrows()]
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
                player_filename = re.sub(r'[\\/*?:"<>|]', '', row['Player']).replace(' ', '_')
                player_url = f"{base_path}/players/{player_filename}.html"
                player_data_list.append({'Player': row['Player'], 'url': player_url, 'value': row[stat_key_s2], 'change': row[stat_key_change]})
            top_players_by_stat[name] = {'data': player_data_list, 'url': f"{base_path}/2024-25/index.html"}
    main_video_id = video_data.get("NBA_MAIN")
    main_video_embed_url = f"https://www.youtube.com/embed/{main_video_id}" if main_video_id else None
    stat_pages_footer, all_teams_structured_footer = get_footer_data(base_path)
    render_data = {'base_path': base_path, 'top_teams_by_stat': top_teams_by_stat, 'top_players_by_stat': top_players_by_stat, 'stat_pages': stat_pages_footer, 'all_teams_structured': all_teams_structured_footer, 'glossary_url': f'{base_path}/glossary.html', 'main_video_embed_url': main_video_embed_url}
    with open("output/index.html", "w", encoding="utf-8") as f: f.write(template.render(render_data))
    print("--- トップページの生成完了 ---")
def generate_glossary_page(env, base_path):
    print("--- 指標解説ページの生成開始 ---")
    template = env.get_template('glossary_template.html')
    glossary_items = [{'term': 'Pace', 'description': '1試合あたり48分間のポゼッション（攻撃回数）の推定値。'}, {'term': 'Offensive Efficiency (OFF EFF)', 'description': '100ポゼッションあたりの得点。'}, {'term': 'Defensive Efficiency (DEF EFF)', 'description': '100ポゼッションあたりの失点。'}, {'term': 'Net Rating (NET EFF)', 'description': 'Offensive EfficiencyとDefensive Efficiencyの差。'}, {'term': 'True Shooting % (TS%)', 'description': 'フィールドゴール、3ポイント、フリースローを総合的に評価したシュート効率。'}, {'term': 'Assist Ratio (AST)', 'description': 'チームのフィールドゴール成功のうち、アシストが占める割合。'}, {'term': 'Turnover Ratio (TO)', 'description': '100ポゼッションあたりのターンオーバー数。'}, {'term': 'Off Rebound Rate (ORR)', 'description': 'オフェンスリバウンド機会のうち、実際にリバウンドを獲得した割合。'}, {'term': 'Def Rebound Rate (DRR)', 'description': 'ディフェンスリバウンド機会のうち、実際にリバウンドを獲得した割合。'}]
    stat_pages, all_teams_structured = get_footer_data(base_path)
    render_data = {'base_path': base_path, 'glossary_items': glossary_items, 'stat_pages': stat_pages, 'all_teams_structured': all_teams_structured, 'glossary_url': f'{base_path}/glossary.html'}
    with open("output/glossary.html", "w", encoding="utf-8") as f: f.write(template.render(render_data))
    print("--- 指標解説ページの生成完了 ---")
def generate_comparison_pages(df_s1, df_s2, df_players, video_data, env, player_team_map, base_path):
    print("--- チーム別比較ページの生成開始 ---")
    df_s1_indexed = df_s1.set_index('Team')
    df_s2_indexed = df_s2.set_index('Team')
    all_teams = sorted(list(df_s1_indexed.index.union(df_s2_indexed.index)))
    template = env.get_template('comparison_template.html')
    stats_to_compare = ['PACE', 'OFF EFF', 'DEF EFF', 'NET EFF', 'TS%', 'AST', 'TO']
    stat_pages_footer, all_teams_structured_footer = get_footer_data(base_path)

    active_players_s2 = set()
    if df_players is not None:
        active_players_s2 = set(df_players['Player'])

    for team in all_teams:
        try:
            image_filename = team.replace(' ', '_')
            output_path = f"output/teams/comparison_{image_filename}.html"
            dependencies = [
                "espn_team_stats_2023-24.csv",
                "espn_team_stats_2024-25.csv",
                "player_team_map.csv",
                "player_stats_2024-25.csv",
                "templates/comparison_template.html"
            ]
            if is_file_up_to_date(output_path, dependencies):
                print(f"スキップ: {output_path} は最新です。")
                continue

            stats1 = df_s1_indexed.loc[team]
            stats2 = df_s2_indexed.loc[team]
            stats_for_graph1 = stats1[stats_to_compare]
            stats_for_graph2 = stats2[stats_to_compare]
            x = np.arange(len(stats_to_compare)); width = 0.35
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(x - width/2, stats_for_graph1, width, label='2023-24')
            ax.bar(x + width/2, stats_for_graph2, width, label='2024-25')
            ax.set_ylabel('Value'); ax.set_title(f'Key Stats Comparison: {team}'); ax.set_xticks(x); ax.set_xticklabels(stats_to_compare, rotation=45, ha="right"); ax.legend(); fig.tight_layout()
            
            plt.savefig(f"output/images/comparison_{image_filename}.svg", format="svg"); plt.close(fig)
            summary = generate_team_summary(stats1, stats2)
            
            player_list = []
            if player_team_map:
                for player_name, player_team in player_team_map.items():
                    if player_team == team and player_name in active_players_s2:
                        player_filename_p = re.sub(r'[\\/*?:"<>|]', "", player_name).replace(' ', '_')
                        player_list.append({'name': player_name, 'url': f"{base_path}/players/{player_filename_p}.html"})

            video_id = video_data.get(team)
            video_embed_url = f"https://www.youtube.com/embed/{video_id}" if video_id else None
            render_data = { 'base_path': base_path, 'team_name': team, 'image_filename': image_filename, 'stats_s1': stats1.to_frame(name='Value').to_html(), 'stats_s2': stats2.to_frame(name='Value').to_html(), 'details': TEAM_DETAILS.get(team, {}), 'all_teams_structured': all_teams_structured_footer, 'stat_pages': stat_pages_footer, 'summary_text': summary, 'player_list': player_list, 'video_embed_url': video_embed_url, 'glossary_url': f'{base_path}/glossary.html' }
            
            with open(output_path, "w", encoding="utf-8") as f: f.write(template.render(render_data))
            print(f"生成完了: {output_path}")
        except Exception as e: print(f"警告: {team} の比較ページ生成中にエラーが発生しました。詳細: {e}")
    print("--- チーム別比較ページの生成完了 ---")
def generate_stat_pages(df_s1, df_s2, env, base_path):
    print("--- 指標別ランキングページの生成開始 ---")
    template = env.get_template('stat_comparison_template.html')
    for stat_short, stat_full in STATS_TO_GENERATE.items():
        try:
            sort_ascending = True if stat_short in ('DEF EFF', 'TO') else False
            df_merged = pd.merge(df_s1[['Team', stat_short]], df_s2[['Team', stat_short]], on='Team', suffixes=('_s1', '_s2')).set_index('Team').sort_values(by=f"{stat_short}_s2", ascending=sort_ascending)
            y = np.arange(len(df_merged.index)); height = 0.4
            fig, ax = plt.subplots(figsize=(10, 14))
            ax.barh(y + height/2, df_merged[f'{stat_short}_s1'], height, label='2023-24'); ax.barh(y - height/2, df_merged[f'{stat_short}_s2'], height, label='2024-25')
            ax.set_xlabel('Value'); ax.set_title(f'All Teams Comparison: {stat_full}'); ax.set_yticks(y); ax.set_yticklabels(df_merged.index); ax.invert_yaxis(); ax.legend(); fig.tight_layout()
            stat_filename = stat_short.replace('%', '_PCT').replace(' ', '_')
            plt.savefig(f"output/images/stat_{stat_filename}.svg", format="svg"); plt.close(fig)
            stat_pages, all_teams_structured = get_footer_data(base_path)
            render_data = { 'base_path': base_path, 'stat_name_jp': stat_full, 'stat_name_en': stat_filename, 'data_table_html': df_merged.rename(columns={f'{stat_short}_s1': '2023-24', f'{stat_short}_s2': '2024-25'}).to_html(), 'stat_pages': stat_pages, 'all_teams_structured': all_teams_structured, 'glossary_url': f'{base_path}/glossary.html' }
            output_path = f"output/stats/{stat_filename}.html"
            with open(output_path, "w", encoding="utf-8") as f: f.write(template.render(render_data))
        except Exception as e: print(f"エラー: {stat_full} のページ生成中に問題が発生しました: {e}")
    print("--- 指標別ランキングページの生成完了 ---")


def generate_player_pages(env, scoring_timeline_data, df_s1_raw, df_s2_raw, player_team_map, base_path):
    print("--- 選手ページの生成開始 ---")
    if df_s1_raw is None or df_s2_raw is None:
        print("警告: 選手データファイルが見つからないため、選手ページをスキップします。")
        return

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
    
    # ★★★ 追加 ★★★ 
    # 1分毎の得点データを集計するヘルパー関数
    def get_scoring_by_minute(timeline_df):
        made_shots = timeline_df[timeline_df['MADE_FLAG'] == 1].copy()
        if made_shots.empty:
            return pd.DataFrame()
        point_map = {'3PT': 3, '2PT': 2, 'FT': 1}
        made_shots['POINTS'] = made_shots['SHOT_TYPE'].map(point_map)
        made_shots['minute_bin'] = np.floor(made_shots['absolute_minute'])
        scoring_df = pd.pivot_table(
            made_shots, values='POINTS', index='minute_bin', columns='SHOT_TYPE', aggfunc='sum'
        ).fillna(0)
        for col in ['FT', '2PT', '3PT']:
            if col not in scoring_df.columns:
                scoring_df[col] = 0
        return scoring_df

    df_merged = pd.merge(df_s2_raw, df_s1_raw, on='Player', how='left', suffixes=('_s2', '_s1'))
    template = env.get_template('player_comparison_template.html')
    stats_to_compare = ['PTS', 'REB', 'AST', 'STL', 'BLK']
    stat_pages_footer, all_teams_structured_footer = get_footer_data(base_path)

    for index, player_data in df_merged.iterrows():
        player_name = player_data.get('Player', 'Unknown')
        try:
            player_filename = re.sub(r'[\\/*?:"<>|]', "", player_name).replace(' ', '_')
            output_path = f"output/players/{player_filename}.html"
            dependencies = [
                "player_stats_2023-24.csv", "player_stats_2024-25.csv",
                "player_scoring_timeline.csv", "templates/player_comparison_template.html"
            ]
            if is_file_up_to_date(output_path, dependencies):
                print(f"スキップ: {output_path} は最新です。")
                continue

            has_s1_data = pd.notna(player_data.get('PTS_s1'))
            stats_s2_table = pd.DataFrame(player_data.filter(like='_s2')).rename(index=lambda x: x.replace('_s2', ''))
            stats_s1_table = pd.DataFrame(player_data.filter(like='_s1')).rename(index=lambda x: x.replace('_s1', ''))
            team_name = player_team_map.get(player_name, ''); team_url = ""
            if team_name: team_url = f"{base_path}/teams/comparison_{team_name.replace(' ', '_')}.html"
            
            render_data = { 
                'base_path': base_path, 'player_name': player_name, 'player_filename': player_filename, 
                'player_info': stats_s2_table.T.to_dict('records')[0], 
                'stats_s1': stats_s1_table.to_html(header=False, na_rep='-'), 
                'stats_s2': stats_s2_table.to_html(header=False, na_rep='-'), 
                'stat_pages': stat_pages_footer, 'all_teams_structured': all_teams_structured_footer, 
                'team_name': team_name, 'team_url': team_url, 
                'glossary_url': f'{base_path}/glossary.html',
                'has_s1_data': has_s1_data, 
                'has_timeline_23_24': False, 
                'has_timeline_24_25': False,
                'has_timeline_comparison': False # ★★★ 追加 ★★★
            }

            if has_s1_data:
                # (シーズンスタッツ比較グラフの生成は変更なし)
                graph_stats_s2_series = pd.to_numeric(stats_s2_table.loc[stats_to_compare].squeeze(), errors='coerce')
                graph_stats_s1_series = pd.to_numeric(stats_s1_table.loc[stats_to_compare].squeeze(), errors='coerce')
                graph_stats_s2 = graph_stats_s2_series.fillna(0).values
                graph_stats_s1 = graph_stats_s1_series.fillna(0).values
                x = np.arange(len(stats_to_compare)); width = 0.35
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.bar(x - width/2, graph_stats_s1, width, label='2023-24')
                ax.bar(x + width/2, graph_stats_s2, width, label='2024-25')
                ax.set_ylabel('Value'); ax.set_title(f'Key Stats Comparison: {player_name}')
                ax.set_xticks(x); ax.set_xticklabels(stats_to_compare); ax.legend(); fig.tight_layout()
                plt.savefig(f"output/images/players/comparison_{player_filename}.svg", format="svg")
                plt.close(fig)

            timeline_data_23_24 = scoring_timeline_data[(scoring_timeline_data['Player'] == player_name) & (scoring_timeline_data['Season'] == '2023-24')]
            timeline_data_24_25 = scoring_timeline_data[(scoring_timeline_data['Player'] == player_name) & (scoring_timeline_data['Season'] == '2024-25')]
            
            if not timeline_data_24_25.empty:
                render_data['has_timeline_24_25'] = True
                render_data['comment_24_25'] = generate_player_comment(player_name, '2024-25', timeline_data_24_25)
                scoring_24_25 = get_scoring_by_minute(timeline_data_24_25)
                if not scoring_24_25.empty:
                    fig, ax = plt.subplots(figsize=(12, 7))
                    scoring_24_25[['FT', '2PT', '3PT']].plot(kind='bar', stacked=True, ax=ax, width=0.8, color={'FT': '#FFC107', '2PT': '#2196F3', '3PT': '#4CAF50'})
                    ax.set_title(f'{player_name} Scoring Timeline (2024-25)'); ax.set_xlabel('Game Minute'); ax.set_ylabel('Points Scored'); ax.legend(title='Shot Type'); ax.grid(True, axis='y', linestyle='--', alpha=0.6)
                    tick_labels = [item.get_text() for item in ax.get_xticklabels()]
                    new_tick_labels = [label if int(float(label)) % 5 == 0 or int(float(label)) in [11, 23, 35, 47] else '' for label in tick_labels]
                    ax.set_xticklabels(new_tick_labels, rotation=45)
                    fig.tight_layout()
                    plt.savefig(f"output/images/players/timeline_stacked_24-25_{player_filename}.svg", format="svg"); plt.close(fig)
            
            if not timeline_data_23_24.empty:
                render_data['has_timeline_23_24'] = True
                render_data['comment_23_24'] = generate_player_comment(player_name, '2023-24', timeline_data_23_24)
                scoring_23_24 = get_scoring_by_minute(timeline_data_23_24)
                if not scoring_23_24.empty:
                    fig, ax = plt.subplots(figsize=(12, 7))
                    scoring_23_24[['FT', '2PT', '3PT']].plot(kind='bar', stacked=True, ax=ax, width=0.8, color={'FT': '#FFC107', '2PT': '#2196F3', '3PT': '#4CAF50'})
                    ax.set_title(f'{player_name} Scoring Timeline (2023-24)'); ax.set_xlabel('Game Minute'); ax.set_ylabel('Points Scored'); ax.legend(title='Shot Type'); ax.grid(True, axis='y', linestyle='--', alpha=0.6)
                    tick_labels = [item.get_text() for item in ax.get_xticklabels()]
                    new_tick_labels = [label if int(float(label)) % 5 == 0 or int(float(label)) in [11, 23, 35, 47] else '' for label in tick_labels]
                    ax.set_xticklabels(new_tick_labels, rotation=45)
                    fig.tight_layout()
                    plt.savefig(f"output/images/players/timeline_stacked_23-24_{player_filename}.svg", format="svg"); plt.close(fig)

            # ★★★ ここから新しいグラフ生成ブロック ★★★
            if render_data['has_timeline_23_24'] and render_data['has_timeline_24_25']:
                scoring_23_24 = get_scoring_by_minute(timeline_data_23_24)
                scoring_24_25 = get_scoring_by_minute(timeline_data_24_25)

                if not scoring_23_24.empty and not scoring_24_25.empty:
                    render_data['has_timeline_comparison'] = True
                    # 両方のDFを0-47分のindexで揃える
                    full_index = pd.Index(range(48), name='minute_bin')
                    scoring_23_24 = scoring_23_24.reindex(full_index, fill_value=0)
                    scoring_24_25 = scoring_24_25.reindex(full_index, fill_value=0)
                    
                    # グラフ1: 得点差（実数）
                    diff_abs = (scoring_24_25 - scoring_23_24)[['FT', '2PT', '3PT']]
                    fig, ax = plt.subplots(figsize=(12, 7))
                    diff_abs.plot(kind='bar', ax=ax, width=0.8, color={'FT': '#FFC107', '2PT': '#2196F3', '3PT': '#4CAF50'})
                    ax.set_title(f'{player_name} 得点差 (24-25 vs 23-24)'); ax.set_xlabel('Game Minute'); ax.set_ylabel('Point Difference')
                    ax.axhline(0, color='grey', linewidth=0.8)
                    ax.legend(title='Shot Type')
                    tick_labels = [item.get_text() for item in ax.get_xticklabels()]
                    new_tick_labels = [label if int(float(label)) % 5 == 0 or int(float(label)) in [11, 23, 35, 47] else '' for label in tick_labels]
                    ax.set_xticklabels(new_tick_labels, rotation=45)
                    fig.tight_layout()
                    plt.savefig(f"output/images/players/timeline_diff_abs_{player_filename}.svg", format="svg"); plt.close(fig)

                    # グラフ2: 増減率
                    # 0除算を避けるため、分母が0の場合は変化率を0とする
                    diff_pct = (scoring_24_25 - scoring_23_24).divide(scoring_23_24.replace(0, np.nan)).fillna(0) * 100
                    diff_pct = diff_pct[['FT', '2PT', '3PT']]
                    fig, ax = plt.subplots(figsize=(12, 7))
                    diff_pct.plot(kind='bar', ax=ax, width=0.8, color={'FT': '#FFC107', '2PT': '#2196F3', '3PT': '#4CAF50'})
                    ax.set_title(f'{player_name} 得点増減率 (24-25 vs 23-24)'); ax.set_xlabel('Game Minute'); ax.set_ylabel('Percentage Change (%)')
                    ax.axhline(0, color='grey', linewidth=0.8)
                    ax.legend(title='Shot Type')
                    tick_labels = [item.get_text() for item in ax.get_xticklabels()]
                    new_tick_labels = [label if int(float(label)) % 5 == 0 or int(float(label)) in [11, 23, 35, 47] else '' for label in tick_labels]
                    ax.set_xticklabels(new_tick_labels, rotation=45)
                    fig.tight_layout()
                    plt.savefig(f"output/images/players/timeline_diff_pct_{player_filename}.svg", format="svg"); plt.close(fig)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(template.render(render_data))
            print(f"生成完了: {output_path}")

        except Exception as e:
            print(f"警告: {player_name} のページ生成中にエラー: {e}")
            traceback.print_exc()
    print("--- 選手ページの生成完了 ---")


# (generate_season_player_index と if __name__ == "__main__": は変更なし)
def generate_season_player_index(env, base_path, season_str, df_current, df_previous):
    print(f"--- {season_str}シーズン 選手ランキングページの生成開始 ---")
    if df_current is None:
        print(f"警告: {season_str}の選手データがないため、ランキングページをスキップします。")
        return
    if df_previous is None:
        print(f"警告: 前シーズンの選手データが見つかりません。比較なしで {season_str} のランキングを生成します。")
        df_previous = pd.DataFrame(columns=df_current.columns)

    template = env.get_template('season_player_index_template.html')
    player_stats_to_show = {'PTS': {'jp': '得点', 'en': 'Points'}, 'REB': {'jp': 'リバウンド', 'en': 'Rebounds'}, 'AST': {'jp': 'アシスト', 'en': 'Assists'}, 'STL': {'jp': 'スティール', 'en': 'Steals'}, 'BLK': {'jp': 'ブロック', 'en': 'Blocks'}}
    current_year_short = season_str.split('-')[0]; previous_year_short = str(int(current_year_short) - 1); previous_season_str = f"{previous_year_short}-{current_year_short[2:]}"
    df_merged = pd.merge(df_current, df_previous, on='Player', how='left', suffixes=('_current', '_previous'))
    leaders_with_graphs = []
    for stat, names in player_stats_to_show.items():
        name_jp = names['jp']; name_en = names['en']
        stat_key_current, stat_key_previous, stat_key_change = f'{stat}_current', f'{stat}_previous', f'{stat}_change'
        for col in [stat_key_current, stat_key_previous]: df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce')
        df_merged[stat_key_change] = df_merged[stat_key_current] - df_merged[stat_key_previous].fillna(0)
        top_10_players = df_merged.sort_values(by=stat_key_current, ascending=False).head(10)
        
        fig, ax = plt.subplots(figsize=(10, 8)); y = np.arange(len(top_10_players)); height = 0.4
        
        players_reversed = top_10_players.iloc[::-1]
        ax.barh(y - height/2, players_reversed[stat_key_previous], height, label=previous_season_str); ax.barh(y + height/2, players_reversed[stat_key_current], height, label=season_str)
        ax.set_xlabel(name_en); ax.set_ylabel('Player'); ax.set_title(f'Top 10 {name_en} Leaders ({season_str} Season)'); ax.set_yticks(y); ax.set_yticklabels(players_reversed['Player']); ax.legend(); fig.tight_layout()
        graph_filename = f"{season_str}_{stat}.svg"; graph_path = f"output/images/season_leaders/{graph_filename}"
        plt.savefig(graph_path, format="svg"); plt.close(fig)
        player_data_list = []
        for _, row in top_10_players.iterrows():
            player_filename = re.sub(r'[\\/*?:"<>|]', '', row['Player']).replace(' ', '_')
            player_url = f"{base_path}/players/{player_filename}.html"
            player_data_list.append({'Player': row['Player'], 'url': player_url, 'value': row[stat_key_current], 'change': row[stat_key_change]})
        leaders_with_graphs.append({'stat_en': stat, 'stat_jp': name_jp, 'data': player_data_list, 'graph_url': f"{base_path}/images/season_leaders/{graph_filename}"})
    stat_pages_footer, all_teams_structured_footer = get_footer_data(base_path)
    render_data = {'base_path': base_path, 'season_str': season_str, 'leaders_with_graphs': leaders_with_graphs, 'stat_pages': stat_pages_footer, 'all_teams_structured': all_teams_structured_footer, 'glossary_url': f'{base_path}/glossary.html'}
    output_path = f"output/{season_str}/index.html"
    with open(output_path, "w", encoding="utf-8") as f: f.write(template.render(render_data))
    print(f"--- {season_str}シーズン 選手ランキングページの生成完了 ---")
if __name__ == "__main__":
    print("--- HTML生成スクリプトを開始します ---")
    base_path = "/nba-stats-media"
    
    os.makedirs("output/teams", exist_ok=True); os.makedirs("output/images", exist_ok=True); os.makedirs("output/stats", exist_ok=True); os.makedirs("output/logos", exist_ok=True); os.makedirs("output/css", exist_ok=True); os.makedirs("output/players", exist_ok=True); os.makedirs("output/images/players", exist_ok=True); os.makedirs("output/2023-24", exist_ok=True); os.makedirs("output/2024-25", exist_ok=True); os.makedirs("output/images/season_leaders", exist_ok=True)
    print("出力ディレクトリの準備が完了しました。")

    df_23_24, df_24_25 = None, None
    try:
        df_23_24 = pd.read_csv("espn_team_stats_2023-24.csv"); df_24_25 = pd.read_csv("espn_team_stats_2024-25.csv")
        df_23_24['Team'] = df_23_24['Team'].replace(TEAM_NAME_MAP); df_24_25['Team'] = df_24_25['Team'].replace(TEAM_NAME_MAP)
        df_23_24['NET EFF'] = df_23_24['OFF EFF'] - df_23_24['DEF EFF']; df_24_25['NET EFF'] = df_24_25['OFF EFF'] - df_24_25['DEF EFF']
        df_24_25['PACE_rank'] = df_24_25['PACE'].rank(method='min', ascending=False); df_24_25['OFF EFF_rank'] = df_24_25['OFF EFF'].rank(method='min', ascending=False); df_24_25['DEF EFF_rank'] = df_24_25['DEF EFF'].rank(method='min', ascending=True)
    except FileNotFoundError as e:
        print(f"エラー: チーム統計ファイルが見つかりません: {e}")
        sys.exit(1)
    
    df_players_23_24, df_players_24_25, player_team_map = None, None, {}
    try:
        df_players_23_24 = pd.read_csv("player_stats_2023-24.csv"); df_players_23_24['Player'] = df_players_23_24['Player'].apply(normalize_name)
    except FileNotFoundError:
        print("警告: 2023-24シーズンの選手データファイルが見つかりません。")
    try:
        df_players_24_25 = pd.read_csv("player_stats_2024-25.csv"); df_players_24_25['Player'] = df_players_24_25['Player'].apply(normalize_name)
    except FileNotFoundError:
        print("警告: 2024-25シーズンの選手データファイルが見つかりません。")
    try:
        roster_df = pd.read_csv("player_team_map.csv"); roster_df['Player'] = roster_df['Player'].apply(normalize_name)
        player_team_map = pd.Series(roster_df.Team.values, index=roster_df.Player).to_dict()
    except FileNotFoundError:
        print("警告: 選手チーム対応ファイル(player_team_map.csv)が見つかりません。")

    try:
        with open('youtube_videos.json', 'r') as f: video_data = json.load(f)
    except FileNotFoundError: video_data = {}

    try:
        scoring_timeline_data = pd.read_csv('player_scoring_timeline.csv')
        scoring_timeline_data['Player'] = scoring_timeline_data['Player'].apply(normalize_name)
    except FileNotFoundError:
        print("警告: スコアリングタイムラインデータが見つかりません。")
        scoring_timeline_data = pd.DataFrame()

    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    
    generate_main_index(env, base_path, df_23_24, df_24_25, df_players_23_24, df_players_24_25, video_data)
    generate_glossary_page(env, base_path)
    generate_stat_pages(df_23_24, df_24_25, env, base_path)
    generate_comparison_pages(df_23_24, df_24_25, df_players_24_25, video_data, env, player_team_map, base_path)
    generate_player_pages(env, scoring_timeline_data, df_players_23_24, df_players_24_25, player_team_map, base_path)
    generate_season_player_index(env, base_path, '2024-25', df_players_24_25, df_players_23_24)
    generate_season_player_index(env, base_path, '2023-24', df_players_23_24, df_players_24_25)

    print("\n--- すべての処理が完了しました ---")