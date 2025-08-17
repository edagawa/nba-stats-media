# -*- coding: utf-8 -*-
import os
import sys
import pandas as pd
import jinja2
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'

def generate_season_pages(season_string, team_stats_df):
    # (この関数は変更なし)
    print("--- {0} シーズンのページ生成開始 ---".format(season_string))
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    team_template = env.get_template('season_summary_template.html')
    output_dir_teams = "output/{0}/teams".format(season_string)
    os.makedirs(output_dir_teams, exist_ok=True)
    for index, row in team_stats_df.iterrows():
        team_name = row['Team']
        summary_text = "{0}は、{1}シーズンを平均{2:.1f}得点、{3:.1f}アシスト、{4:.1f}リバウンドで終えました。".format(team_name, season_string, row['PTS'], row['AST'], row['REB'])
        report_data = { 'team_name': team_name, 'season_string': season_string, 'summary_text': summary_text, 'team_stats_html': row.to_frame().T.to_html(index=False), 'main_page_url': '../../index.html' }
        file_name = "{0}_{1}_season.html".format(team_name.replace(' ', '_'), season_string)
        html_content = team_template.render(report_data)
        with open(os.path.join(output_dir_teams, file_name), "w", encoding="utf-8") as f: f.write(html_content)
    index_template = env.get_template('index_template.html')
    output_dir_season = "output/{0}".format(season_string)
    os.makedirs(output_dir_season, exist_ok=True)
    teams_for_template = []
    for index, row in team_stats_df.iterrows():
        file_name = "teams/{0}_{1}_season.html".format(row['Team'].replace(' ', '_'), season_string)
        teams_for_template.append({ 'name': row['Team'], 'url': file_name })
    html_content = index_template.render(teams=teams_for_template, season_string=season_string)
    with open(os.path.join(output_dir_season, "index.html"), "w", encoding="utf-8") as f: f.write(html_content)
    print("--- {0} シーズンのページ生成完了 ---".format(season_string))

def generate_comparison_pages(df_s1, df_s2, all_teams, stat_pages_info):
    print("--- 比較ページの生成開始 ---")
    df_s1 = df_s1.set_index('Team')
    df_s2 = df_s2.set_index('Team')
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    comparison_template = env.get_template('comparison_template.html')
    output_dir_teams = "output/teams"; output_dir_images = "output/images"
    os.makedirs(output_dir_teams, exist_ok=True); os.makedirs(output_dir_images, exist_ok=True)
    stats_to_compare = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'FG%']
    
    # ★★★ フッター用の全チームリンクリストを作成 ★★★
    all_teams_info = [{'name': team, 'url': '../teams/{0}.html'.format(team.replace(' ', '_'))} for team in all_teams]

    for team in all_teams:
        try:
            stats1 = df_s1.loc[team, stats_to_compare]; stats2 = df_s2.loc[team, stats_to_compare]
            x = np.arange(len(stats_to_compare)); width = 0.35
            fig, ax = plt.subplots(figsize=(10, 6))
            rects1 = ax.bar(x - width/2, stats1, width, label='2023-24')
            rects2 = ax.bar(x + width/2, stats2, width, label='2024-25')
            ax.set_ylabel('Value'); ax.set_title('Key Stats Comparison: {0}'.format(team)); ax.set_xticks(x); ax.set_xticklabels(stats_to_compare); ax.legend(); fig.tight_layout()
            image_filename = team.replace(' ', '_')
            plt.savefig(os.path.join(output_dir_images, "comparison_{0}.svg".format(image_filename)), format="svg"); plt.close()
            
            # ★★★ フッター用データをテンプレートに渡す ★★★
            render_data = { 
                'team_name': team, 'image_filename': image_filename, 
                'stats_s1': df_s1.loc[team].to_frame().to_html(), 
                'stats_s2': df_s2.loc[team].to_frame().to_html(),
                'all_teams': all_teams_info,
                'stat_pages': stat_pages_info
            }
            html_content = comparison_template.render(render_data)
            with open(os.path.join(output_dir_teams, "{0}.html".format(image_filename)), "w", encoding="utf-8") as f: f.write(html_content)
        except KeyError: print("'{0}' のデータが片方のシーズンにしか存在しないため、比較ページは生成されません。".format(team))
    print("--- 比較ページの生成完了 ---")

def generate_main_index(teams_list, stat_pages_info):
    print("--- メインインデックスページの生成開始 ---")
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    index_template = env.get_template('index_template.html')
    teams_for_template = []
    for team in teams_list:
        file_name = "teams/{0}.html".format(team.replace(' ', '_'))
        teams_for_template.append({ 'name': team, 'url': file_name })
    html_content = index_template.render(teams=teams_for_template, season_string="チーム比較", stat_pages=stat_pages_info)
    with open(os.path.join("output", "index.html"), "w", encoding="utf-8") as f: f.write(html_content)
    print("--- メインインデックスページの生成完了 ---")

def generate_stat_comparison_pages(df_s1, df_s2, all_teams, stat_pages_info):
    print("--- 指標別比較ページの生成開始 ---")
    merged_df = pd.merge(df_s1, df_s2, on='Team', suffixes=('_s1', '_s2'), how='inner')
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    stat_template = env.get_template('stat_comparison_template.html')
    output_dir_stats = "output/stats"; output_dir_images = "output/images"
    os.makedirs(output_dir_stats, exist_ok=True); os.makedirs(output_dir_images, exist_ok=True)
    
    stats_to_generate = {
        'PTS': 'Points Per Game', 'REB': 'Rebounds Per Game', 'AST': 'Assists Per Game',
        'STL': 'Steals Per Game', 'BLK': 'Blocks Per Game', 'FG%': 'Field Goal %'
    }

    for stat_en, stat_full_en in stats_to_generate.items():
        sorted_df = merged_df.sort_values(by=f'{stat_en}_s2', ascending=False)
        teams = sorted_df['Team']; stats1 = sorted_df[f'{stat_en}_s1']; stats2 = sorted_df[f'{stat_en}_s2']
        x = np.arange(len(teams)); width = 0.4
        
        fig, ax = plt.subplots(figsize=(15, 8))
        rects1 = ax.bar(x - width/2, stats1, width, label='2023-24')
        rects2 = ax.bar(x + width/2, stats2, width, label='2024-25')

        # ★★★ グラフタイトルをさらにシンプルな英語に修正 ★★★
        ax.set_ylabel('Value')
        ax.set_title('All Teams Comparison: {0}'.format(stat_en))
        ax.set_xticks(x)
        ax.set_xticklabels(teams, rotation=90)
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        fig.tight_layout()

        plt.savefig(os.path.join(output_dir_images, "stat_{0}.svg".format(stat_en)), format="svg"); plt.close()

        # ★★★ フッター用データをテンプレートに渡す ★★★
        render_data = {
            'stat_name_jp': stat_full_en,
            'stat_name_en': stat_en,
            'graph_url': '../images/stat_{0}.svg'.format(stat_en),
            'data_table_html': sorted_df[['Team', f'{stat_en}_s1', f'{stat_en}_s2']].to_html(index=False),
            'all_teams': [{'name': team, 'url': '../teams/{0}.html'.format(team.replace(' ', '_'))} for team in all_teams],
            'stat_pages': stat_pages_info
        }
        html_content = stat_template.render(render_data)
        with open(os.path.join(output_dir_stats, "{0}.html".format(stat_en)), "w", encoding="utf-8") as f: f.write(html_content)
        print("'{0}.html' を生成しました。".format(stat_en))
        
    print("--- 指標別比較ページの生成完了 ---")

def main():
    try:
        df_s1 = pd.read_csv("espn_team_stats_23-24.csv")
        df_s2 = pd.read_csv("espn_team_stats_24-25.csv")
    except FileNotFoundError as e:
        print("エラー: CSVファイルが見つかりません。 {0}".format(e))
        sys.exit(1)
    
    stats_to_generate = {
        'PTS': 'Points Per Game', 'REB': 'Rebounds Per Game', 'AST': 'Assists Per Game',
        'STL': 'Steals Per Game', 'BLK': 'Blocks Per Game', 'FG%': 'Field Goal %'
    }
    stat_pages_info = [{'name': en_full, 'url': './stats/{0}.html'.format(en_short)} for en_short, en_full in stats_to_generate.items()]
    all_teams = sorted(list(set(df_s1['Team']) | set(df_s2['Team'])))

    generate_season_pages("2023-24", df_s1)
    generate_season_pages("2024-25", df_s2)
    # ★★★ フッター用のデータを渡すように変更 ★★★
    generate_comparison_pages(df_s1, df_s2, all_teams, stat_pages_info)
    generate_stat_comparison_pages(df_s1, df_s2, all_teams, stat_pages_info)
    generate_main_index(all_teams, stat_pages_info)

    print("\nすべてのHTMLファイルの生成が完了しました。")

if __name__ == "__main__":
    main()