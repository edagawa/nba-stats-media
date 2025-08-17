# -*- coding: utf-8 -*-
import os
import sys
import pandas as pd
import jinja2

def get_team_season_stats_summary():
    """
    ローカルのCSVファイル(ESPN由来)からシーズンサマリーデータを読み込む
    """
    file_path = "espn_team_stats_23-24.csv"
    try:
        print("ローカルファイル '{0}' からデータを読み込んでいます...".format(file_path))
        team_stats_df = pd.read_csv(file_path)
        return team_stats_df
    except FileNotFoundError:
        print("エラー: データファイル '{0}' が見つかりません。".format(file_path))
        print("get_data.py を実行して、先にデータファイルを作成してください。")
        return pd.DataFrame()

def generate_season_summary_text(team_data):
    """
    ESPNのデータに基づいて、シーズン総括コメントを生成
    """
    team_name = team_data['Team']
    # 'W' と 'L' 列が存在するか確認し、なければ勝率計算をスキップ
    if 'W' in team_data.index and 'L' in team_data.index:
        wins = int(team_data['W'])
        losses = int(team_data['L'])
        win_pct = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0
        win_loss_text = "{0}勝{1}敗、勝率{2:.1f}%".format(wins, losses, win_pct)
    else:
        win_loss_text = "勝敗データなし"

    pts = float(team_data['PTS'])
    ast = float(team_data['AST'])
    reb = float(team_data['REB'])
    
    summary = "{0}は、2023-24シーズンを{1}で終えました。平均{2:.1f}得点、{3:.1f}アシスト、{4:.1f}リバウンドを記録し、安定したシーズンを送りました。".format(team_name, win_loss_text, pts, ast, reb)
    return summary

def generate_team_pages(team_stats_df):
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('season_summary_template.html')

    output_dir = "output/teams"
    os.makedirs(output_dir, exist_ok=True)

    for index, row in team_stats_df.iterrows():
        summary_text = generate_season_summary_text(row)
        
        # ★★★ このブロックの閉じ括弧が抜けていました ★★★
        report_data = {
            'team_name': row['Team'],
            'summary_text': summary_text,
            'team_stats_html': row.to_frame().T.to_html(index=False),
            'main_page_url': '../index.html'
        }
        
        file_name = "{0}_2023-24_season.html".format(row['Team'].replace(' ', '_'))
        html_content = template.render(report_data)
        with open(os.path.join(output_dir, file_name), "w", encoding="utf-8") as f:
            f.write(html_content)
        print("'{0}' を生成しました。".format(file_name))

def generate_index_page(team_stats_df):
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('index_template.html')

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    teams_for_template = []
    for index, row in team_stats_df.iterrows():
        file_name = "teams/{0}_2023-24_season.html".format(row['Team'].replace(' ', '_'))
        teams_for_template.append({
            'name': row['Team'],
            'url': file_name
        })
    
    html_content = template.render(teams=teams_for_template)
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print("index.html を生成しました。")

def main():
    team_stats_df = get_team_season_stats_summary()
    if team_stats_df.empty:
        print("データが取得できませんでした。スクリプトを異常終了します。")
        sys.exit(1)
    
    print("データ取得成功。HTMLファイルの生成を開始します。")
    generate_index_page(team_stats_df)
    generate_team_pages(team_stats_df)
    print("HTMLファイルの生成が完了しました。")

if __name__ == "__main__":
    main()