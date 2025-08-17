import os
import pandas as pd
import jinja2
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamelog

def get_team_season_stats(team_id):
    """
    指定されたチームIDの2024-25シーズンの全試合データを取得
    """
    try:
        # 2024-25シーズンのチームの全試合データを取得
        team_log = leaguegamelog.LeagueGameLog(team_id_nullable=team_id, season="2024-25").get_data_frames()[0]
        return team_log
    except Exception as e:
        print(f"チームID {team_id} のデータ取得中にエラーが発生しました: {e}")
        return pd.DataFrame()

def generate_team_season_page(team_data, team_name):
    """
    チームごとのシーズンサマリーページを生成
    """
    # データの集計
    if team_data.empty:
        summary_text = "2024-25シーズンのデータはありません。"
        summary_stats_html = ""
    else:
        # 勝利数と敗戦数を計算
        wins = team_data[team_data['WL'] == 'W'].shape[0]
        losses = team_data[team_data['WL'] == 'L'].shape[0]
        
        # 主要スタッツの平均値を計算
        summary_stats = team_data[['PTS', 'AST', 'REB', 'STL', 'BLK']].mean().round(1)
        
        summary_text = f"2024-25シーズンの{team_name}は、{wins}勝 {losses}敗という成績でした。以下にシーズン全体の平均スタッツを示します。"
        summary_stats_html = summary_stats.to_frame(name='シーズン平均').to_html()

    # Jinja2テンプレート設定
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('season_summary_template.html')

    # レポート生成
    html_content = template.render(
        team_name=team_name,
        summary_text=summary_text,
        summary_stats_html=summary_stats_html
    )
    
    # ページ名にチーム名を使用
    file_name = f"{team_name.replace(' ', '_')}_2024-25_season.html"
    output_dir = "output/teams"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, file_name), "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"'{file_name}' を生成しました。")

def main():
    nba_teams = teams.get_teams()
    for team in nba_teams:
        team_id = team['id']
        team_name = team['full_name']
        
        # チームごとのシーズンスタッツを取得
        team_season_data = get_team_season_stats(team_id)
        
        # ページを生成
        generate_team_season_page(team_season_data, team_name)

if __name__ == "__main__":
    main()