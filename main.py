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

def generate_season_pages(season_string, team_stats_df, stat_pages_info_main):
    # (This function is correct and needs no changes)
    print("--- {0} シーズンのページ生成開始 ---".format(season_string))
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'); env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    team_template = env.get_template('season_summary_template.html')
    output_dir_teams = "output/{0}/teams".format(season_string); os.makedirs(output_dir_teams, exist_ok=True)
    for index, row in team_stats_df.iterrows():
        team_name = row['Team']
        summary_text = "{0}は、{1}シーズンをOFF EFF {2:.2f}, DEF EFF {3:.2f}, NET RTG {4:.2f}で終えました。".format(team_name, season_string, row['OFF EFF'], row['DEF EFF'], row['NET EFF'])
        report_data = { 'team_name': team_name, 'season_string': season_string, 'summary_text': summary_text, 'team_stats_html': row.to_frame().T.to_html(index=False), 'main_page_url': '../../index.html' }
        file_name = "{0}_{1}_season.html".format(team_name.replace(' ', '_'), season_string)
        html_content = team_template.render(report_data)
        with open(os.path.join(output_dir_teams, file_name), "w", encoding="utf-8") as f: f.write(html_content)
    index_template = env.get_template('index_template.html')
    output_dir_season = "output/{0}".format(season_string); os.makedirs(output_dir_season, exist_ok=True)
    season_teams_structured = {}
    stat_pages_info_seasonal = [{'name': stat['name'], 'url': f"../{stat['url']}"} for stat in stat_pages_info_main]
    html_content = index_template.render(all_teams_structured=season_teams_structured, season_string=season_string, stat_pages=stat_pages_info_seasonal)
    with open(os.path.join(output_dir_season, "index.html"), "w", encoding="utf-8") as f: f.write(html_content)
    print("--- {0} シーズンのページ生成完了 ---".format(season_string))

def generate_comparison_pages(df_s1, df_s2):
    # (This function is correct and needs no changes)
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
            render_data = { 'team_name': team, 'image_filename': image_filename, 'stats_s1': df_s1.loc[team].to_frame().to_html(), 'stats_s2': df_s2.loc[team].to_frame().to_html(), 'all_teams_structured': all_teams_structured_footer, 'stat_pages': stat_pages_info_footer }
            html_content = comparison_template.render(render_data)
            with open(os.path.join(output_dir_teams, "{0}.html".format(image_filename)), "w", encoding="utf-8") as f: f.write(html_content)
        except KeyError: print("'{0}' のデータが片方のシーズンにしか存在しないため、比較ページは生成されません。".format(team))
    print("--- チーム別比較ページの生成完了 ---")

def generate_main_index(all_teams_structured_main, stat_pages_info_main):
    # (This function is correct and needs no changes)
    print("--- メインインデックスページの生成開始 ---")
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'); env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    index_template = env.get_template('index_template.html')
    html_content = index_template.render(season_string="チーム比較", all_teams_structured=all_teams_structured_main, stat_pages=stat_pages_info_main)
    with open(os.path.join("output", "index.html"), "w", encoding="utf-8") as f: f.write(html_content)
    print("--- メインインデックスページの生成完了 ---")

def generate_stat_comparison_pages(df_s1, df_s2):
    # (This function is correct and needs no changes)
    print("--- 指標別比較ページの生成開始 ---")
    merged_df = pd.merge(df_s1, df_s2, on='Team', suffixes=('_s1', '_s2'), how='inner')
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'); env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    stat_template = env.get_template('stat_comparison_template.html')
    output_dir_stats = "output/stats"; output_dir_images = "output/images"
    os.makedirs(output_dir_stats, exist_ok=True); os.makedirs(output_dir_images, exist_ok=True)
    stats_to_generate = { 'PACE': 'Pace', 'AST': 'Assist Ratio', 'TO': 'Turnover Ratio', 'ORR': 'Off Rebound Rate', 'DRR': 'Def Rebound Rate', 'TS%': 'True Shooting %', 'OFF EFF': 'Offensive Efficiency', 'DEF EFF': 'Defensive Efficiency', 'NET EFF': 'Net Rating' }
    all_teams = sorted(list(df_s1['Team'].unique()))
    all_teams_structured_footer = {}
    for conf, divisions in CONFERENCE_STRUCTURE.items():
        all_teams_structured_footer[conf] = {}
        for div, teams_in_div in divisions.items():
            all_teams_structured_footer[conf][div] = [{'name': team, 'url': '../teams/{0}.html'.format(team.replace(' ', '_'))} for team in teams_in_div]
    stat_pages_info_footer = [{'name': en_full, 'url': './{0}.html'.format(en_short.replace('%', '_PCT').replace(' ', '_'))} for en_short, en_full in stats_to_generate.items()]
    for stat_en, stat_full_en in stats_to_generate.items():
        safe_stat_en = stat_en.replace('%', '_PCT').replace(' ', '_')
        ascending_order = True if stat_en == 'DEF EFF' or stat_en == 'TO' else False
        sorted_df = merged_df.sort_values(by=f'{stat_en}_s2', ascending=ascending_order)
        teams = sorted_df['Team']; stats1 = sorted_df[f'{stat_en}_s1']; stats2 = sorted_df[f'{stat_en}_s2']
        x = np.arange(len(teams)); width = 0.4
        fig, ax = plt.subplots(figsize=(15, 8)); rects1 = ax.bar(x - width/2, stats1, width, label='2023-24'); rects2 = ax.bar(x + width/2, stats2, width, label='2024-25')
        ax.set_ylabel('Value'); ax.set_title('All Teams Comparison: {0}'.format(stat_en)); ax.set_xticks(x); ax.set_xticklabels(teams, rotation=90); ax.legend(); ax.grid(axis='y', linestyle='--', alpha=0.7); fig.tight_layout()
        plt.savefig(os.path.join(output_dir_images, "stat_{0}.svg".format(safe_stat_en)), format="svg"); plt.close()
        render_data = { 'stat_name_jp': stat_full_en, 'stat_name_en': safe_stat_en, 'graph_url': '../images/stat_{0}.svg'.format(safe_stat_en), 'data_table_html': sorted_df[['Team', f'{stat_en}_s1', f'{stat_en}_s2']].to_html(index=False), 'all_teams_structured': all_teams_structured_footer, 'stat_pages': stat_pages_info_footer }
        html_content = stat_template.render(render_data)
        with open(os.path.join(output_dir_stats, "{0}.html".format(safe_stat_en)), "w", encoding="utf-8") as f: f.write(html_content)
        print("'{0}.html' を生成しました。".format(safe_stat_en))
    print("--- 指標別比較ページの生成完了 ---")

def main():
    try:
        # ★★★ ファイル名を4桁の年に修正 ★★★
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

    generate_season_pages("2023-24", df_s1, stat_pages_info_main)
    generate_season_pages("2024-25", df_s2, stat_pages_info_main)
    generate_comparison_pages(df_s1, df_s2)
    generate_stat_comparison_pages(df_s1, df_s2)
    generate_main_index(all_teams_structured_main, stat_pages_info_main)

    print("\nすべてのHTMLファイルの生成が完了しました。")

if __name__ == "__main__":
    main()