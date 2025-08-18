# -*- coding: utf-8 -*-
import os
import json
from googleapiclient.discovery import build

# 検索対象となるチーム名のリスト
NBA_TEAMS = [
    'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets', 'Chicago Bulls',
    'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons', 'Golden State Warriors',
    'Houston Rockets', 'Indiana Pacers', 'LA Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies',
    'Miami Heat', 'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks',
    'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns', 'Portland Trail Blazers',
    'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors', 'Utah Jazz', 'Washington Wizards'
]

def fetch_latest_videos():
    """YouTube APIを使い、各チームの最新動画IDを取得してJSONファイルに保存する"""
    
    # ★★★ ここから修正 ★★★
    # 環境変数からAPIキーを読み込む
    API_KEY = os.environ.get("YOUTUBE_API_KEY")
    
    # APIキーが設定されていない場合はエラーメッセージを出して終了
    if not API_KEY:
        print("エラー: 環境変数 'YOUTUBE_API_KEY' が設定されていません。")
        print("実行前にターミナルで export YOUTUBE_API_KEY='あなたのキー' を実行してください。")
        return
    # ★★★ ここまで修正 ★★★

    youtube = build('youtube', 'v3', developerKey=API_KEY)
    video_links = {}

    print("--- 各チームの最新動画を取得しています ---")
    for team_name in NBA_TEAMS:
        try:
            # チーム名でYouTubeチャンネルを検索して、チャンネルIDを取得する
            search_request = youtube.search().list(
                q=f"{team_name} official channel",
                part='snippet',
                type='channel',
                maxResults=1
            )
            search_response = search_request.execute()

            if 'items' not in search_response or not search_response['items']:
                print(f"失敗: {team_name} のチャンネルが見つかりませんでした。")
                video_links[team_name] = None
                continue
            
            channel_id = search_response['items'][0]['id']['channelId']

            # チャンネルIDからアップロード動画のリストIDを取得する
            channel_request = youtube.channels().list(
                part='contentDetails',
                id=channel_id
            )
            channel_response = channel_request.execute()
            playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # 動画リストから最新の動画を1件取得する
            playlist_request = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=1
            )
            playlist_response = playlist_request.execute()

            if 'items' not in playlist_response or not playlist_response['items']:
                print(f"情報: {team_name} のチャンネルに動画がありませんでした。")
                video_links[team_name] = None
                continue

            video_id = playlist_response['items'][0]['snippet']['resourceId']['videoId']
            video_links[team_name] = video_id
            print(f"成功: {team_name} -> Video ID: {video_id}")
            
        except Exception as e:
            print(f"失敗: {team_name} の処理中に予期せぬエラーが発生しました: {e}")
            video_links[team_name] = None
    
    with open('youtube_videos.json', 'w') as f:
        json.dump(video_links, f, indent=4)
        
    print("\n--- 動画IDを 'youtube_videos.json' に保存しました ---")

if __name__ == "__main__":
    fetch_latest_videos()