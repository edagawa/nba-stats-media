import os
import sys  # スクリプトを終了するためにインポート
import pandas as pd
import jinja2
import matplotlib.pyplot as plt
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguedashteamstats, boxscoretraditionalv2, playbyplayv2
from datetime import datetime, timedelta

# (generate_report_html などの関数は変更なしのため省略)
# ...
# ...

def get_team_season_stats_summary():
    """
    全チームのシーズンサマリーデータを取得する
    """
    try:
        team_stats = leaguedashteamstats.LeagueDashTeamStats(season="2023-24").get_data_frames()[0]
        # データが空かどうかの追加チェック
        if team_stats.empty:
            print("APIからデータが返されましたが、中身が空です。")
            return pd.DataFrame()
        return team_stats
    except Exception as e:
        print(f"リーグデータ取得中にエラーが発生しました: {e}")
        return pd.DataFrame()

# (generate_season_summary_text などの関数は変更なしのため省略)
# ...
# ...

def main():
    team_stats_df = get_team_season_stats_summary()
    if team_stats_df.empty:
        print("データが取得できませんでした。スクリプトを異常終了します。")
        # ★★★★★ ここを変更 ★★★★★
        # ワークフローに「失敗」を伝えるために、exit code 1 で終了する
        sys.exit(1)
    
    print("データ取得成功。HTMLファイルの生成を開始します。")
    generate_index_page(team_stats_df)
    generate_team_pages(team_stats_df)
    print("HTMLファイルの生成が完了しました。")
    
if __name__ == "__main__":
    main()

# --- 以下、省略した関数を記載 ---

def get_game_data(game_date_str):
    try:
        games = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=None).get_data_frames()[0]
        game_ids = games[games['GAME_DATE'] == game_date_str]['GAME_ID'].tolist()
        return game_ids
    except Exception as e:
        print(f"試合IDの取得中にエラーが発生しました: {e}")
        return []

def get_game_data_details(game_id):
    boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id).get_data_frames()[0]
    play_by_play = playbyplayv2.PlayByPlayV2(game_id=game_id).get_data_frames()[0]
    return boxscore, play_by_play

def create_svg_graph(df, filename, title):
    plt.figure(figsize=(12, 6))
    df = df[df['SCORE'].notna()]
    df['SCORE_DIFF'] = df['SCORE'].apply(lambda x: int(x.split(' - ')[0]) - int(x.split(' - ')[1]))
    df['EVENTNUM_INDEX'] = range(len(df))
    plt.plot(df['EVENTNUM_INDEX'], df['SCORE_DIFF'], label='得点差', color='blue')
    plt.xlabel('イベント数')
    plt.ylabel('ホームチームの得点差')
    plt.title(title)
    plt.grid(True)
    plt.gca().invert_xaxis()
    os.makedirs('output/images', exist_ok=True)
    plt.savefig(f"output/images/{filename}.svg", format="svg")
    plt.close()

def generate_highlight_text(boxscore):
    if boxscore.empty:
        return "データがありません。"
    top_scorers = boxscore.nlargest(3, 'PTS')
    top_scorer_name = top_scorers.iloc[0]['PLAYER_NAME']
    top_scorer_pts = int(top_scorers.iloc[0]['PTS'])
    highlight_text = f"今日の試合では、<span class='highlight'>{top_scorer_name}</span>がチームを牽引しました。彼は驚異的な<span class='highlight'>{top_scorer_pts}点</span>を記録し、チームの勝利に大きく貢献しました。"
    return highlight_text

def generate_report_html(game_id, boxscore_df, play_by_play_df):
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('report_template.html')
    create_svg_graph(play_by_play_df, f"game_flow_{game_id}", f"試合ID {game_id} スコア推移")
    highlight_text = generate_highlight_text(boxscore_df)
    report_data = {
        'title': f"NBA試合レポート - 試合ID: {game_id}",
        'game_id': game_id,
        'boxscore_html': boxscore_df.to_html(index=False),
        'highlight_text': highlight_text,
        'game_flow_svg': f"images/game_flow_{game_id}.svg"
    }
    html_content = template.render(report_data)
    output_dir = "output"
    with open(f"{output_dir}/{game_id}.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def generate_season_summary_text(team_id, team_stats_df):
    team_data = team_stats_df[team_stats_df['TEAM_ID'] == team_id].iloc[0]
    wins = team_data['W_PCT'] * 100
    pts = team_data['PTS']
    ast = team_data['AST']
    reb = team_data['REB']
    summary = f"2023-24シーズン、このチームは勝率{wins:.1f}%を記録しました。オフェンス面では平均{pts:.1f}得点と{ast:.1f}アシストを記録し、チームの得点効率の高さが際立ちました。また、リバウンドでは平均{reb:.1f}リバウンドと、攻守両面で貢献度の高い選手が多かったことが特徴です。今後のシーズンでのさらなる飛躍が期待されます。"
    return summary

def generate_team_pages(team_stats_df):
    nba_teams = teams.get_teams()
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('season_summary_template.html')
    output_dir = "output/teams"
    os.makedirs(output_dir, exist_ok=True)
    for team in nba_teams:
        team_id = team['id']
        team_name = team['full_name']
        summary_text = generate_season_summary_text(team_id, team_stats_df)
        report_data = {
            'team_name': team_name,
            'summary_text': summary_text,
            'team_stats_html': team_stats_df[team_stats_df['TEAM_ID'] == team_id].to_html(index=False),
            'main_page_url': '../index.html'
        }
        file_name = f"{team_name.replace(' ', '_')}_2023-24_season.html"
        html_content = template.render(report_data)
        with open(os.path.join(output_dir, file_name), "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"'{file_name}' を生成しました。")

def generate_index_page(team_stats_df):
    nba_teams = teams.get_teams()
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('index_template.html')
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    teams_for_template = []
    for team in nba_teams:
        file_name = f"teams/{team['full_name'].replace(' ', '_')}_2023-24_season.html"
        teams_for_template.append({
            'name': team['full_name'],
            'url': file_name
        })
    html_content = template.render(teams=teams_for_template)
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print("index.html を生成しました。")