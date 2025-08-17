import os
import pandas as pd
import jinja2
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguedashteamstats

def get_team_season_stats_summary():
    """
    全チームの2024-25シーズンサマリーデータを取得する
    """
    try:
        # 2024-25シーズンのリーグ全体のチームスタッツを取得
        team_stats = leaguedashteamstats.LeagueDashTeamStats(season="2024-25").get_data_frames()[0]
        return team_stats
    except Exception as e:
        print(f"リーグデータ取得中にエラーが発生しました: {e}")
        return pd.DataFrame()

def generate_season_summary_text(team_id, team_stats_df):
    """
    データに基づいて、自然言語でのシーズン総括コメントを生成
    """
    team_data = team_stats_df[team_stats_df['TEAM_ID'] == team_id].iloc[0]
    
    wins = team_data['W_PCT'] * 100
    pts = team_data['PTS']
    ast = team_data['AST']
    reb = team_data['REB']
    
    summary = f"2024-25シーズン、このチームは勝率{wins:.1f}%を記録しました。オフェンス面では平均{pts:.1f}得点と{ast:.1f}アシストを記録し、チームの得点効率の高さが際立ちました。また、リバウンドでは平均{reb:.1f}リバウンドと、攻守両面で貢献度の高い選手が多かったことが特徴です。今後のシーズンでのさらなる飛躍が期待されます。"
    return summary

def generate_team_pages(team_stats_df):
    """
    全チーム分の総括ページを生成
    """
    nba_teams = teams.get_teams()
    
    # Jinja2テンプレート設定
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('season_summary_template.html')

    output_dir = "output/teams"
    os.makedirs(output_dir, exist_ok=True)

    for team in nba_teams:
        team_id = team['id']
        team_name = team['full_name']
        
        # 自然言語でのサマリーコメントを生成
        summary_text = generate_season_summary_text(team_id, team_stats_df)
        
        # テンプレートに渡すデータ
        report_data = {
            'team_name': team_name,
            'summary_text': summary_text,
            'team_stats_html': team_stats_df[team_stats_df['TEAM_ID'] == team_id].to_html(index=False),
            'main_page_url': '../index.html'
        }
        
        # ページ名にチーム名を使用
        file_name = f"{team_name.replace(' ', '_')}_2024-25_season.html"
        
        # HTMLを生成して保存
        html_content = template.render(report_data)
        with open(os.path.join(output_dir, file_name), "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"'{file_name}' を生成しました。")

def generate_index_page(team_stats_df):
    """
    トップページを生成
    """
    nba_teams = teams.get_teams()
    
    # Jinja2テンプレート設定
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('index_template.html')

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # テンプレートに渡すデータ
    teams_for_template = []
    for team in nba_teams:
        file_name = f"teams/{team['full_name'].replace(' ', '_')}_2024-25_season.html"
        teams_for_template.append({
            'name': team['full_name'],
            'url': file_name
        })
    
    html_content = template.render(teams=teams_for_template)
    
    # HTMLを生成して保存
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    team_stats_df = get_team_season_stats_summary()
    if team_stats_df.empty:
        print("データが取得できませんでした。")
        return
    
    generate_index_page(team_stats_df)
    generate_team_pages(team_stats_df)
    
if __name__ == "__main__":
    main()