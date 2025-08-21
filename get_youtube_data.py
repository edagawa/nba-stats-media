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

# NBA公式チャンネルのID
NBA_MAIN_CHANNEL_ID = "UCWJ2lWNubArHWmf3FIHbfcQ"

def fetch_latest_videos():
    """YouTube APIを使い、各チャンネルの最新動画IDを取得してJSONファイルに保存する"""
    
    API_KEY = os.environ.get("YOUTUBE_API_KEY")
    if not API_KEY:
        print("エラー: 環境変数 'YOUTUBE_API_KEY' が設定されていません。")
        print("実行前にターミナルで export YOUTUBE_API_KEY='あなたのキー' を実行してください。")
        return

    youtube = build('youtube', 'v3', developerKey=API_KEY)
    video_links = {}

    # ★★★ ここから修正箇所 ★★★
    # --- NBAメインチャンネルの最新動画を取得 ---
    print("--- NBAメインチャンネルの動画ID取得開始 ---")
    try:
        # チャンネルIDからアップロード動画のリストIDを取得する
        channel_request = youtube.channels().list(
            part='contentDetails',
            id=NBA_MAIN_CHANNEL_ID
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

        if 'items' in playlist_response and playlist_response['items']:
            video_id = playlist_response['items'][0]['snippet']['resourceId']['videoId']
            video_links['NBA_MAIN'] = video_id
            print(f"成功: NBAメインチャンネル -> Video ID: {video_id}")
        else:
            print(f"情報: NBAメインチャンネルに動画がありませんでした。")
            video_links['NBA_MAIN'] = None

    except Exception as e:
        print(f"失敗: NBAメインチャンネルの動画取得中にエラーが発生しました: {e}")
        video_links['NBA_MAIN'] = None
    print("--- NBAメインチャンネルの動画ID取得完了 ---\n")
    # ★★★ ここまで修正箇所 ★★★

    # 各チームのチャンネルを検索し、最新の動画IDを取得する
    print("--- 各チームの動画ID取得開始 ---")
    for team_name in NBA_TEAMS:
        try:
            # チャンネルを検索
            search_request = youtube.search().list(
                q=f"{team_name} official",
                part='id',
                type='channel',
                maxResults=1
            )
            search_response = search_request.execute()
            
            if 'items' not in search_response or not search_response['items']:
                print(f"情報: {team_name} のチャンネルが見つかりませんでした。")
                video_links[team_name] = None
                continue
            
            channel_id = search_response['items'][0]['id']['channelId']

            # チャンネルIDからアップロード動画のリストIDを取得
            channel_request = youtube.channels().list(part='contentDetails', id=channel_id)
            channel_response = channel_request.execute()
            playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # 動画リストから最新の動画を1件取得
            playlist_request = youtube.playlistItems().list(part='snippet', playlistId=playlist_id, maxResults=1)
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
        
    print("\n--- 全ての動画IDを 'youtube_videos.json' に保存しました ---")

if __name__ == '__main__':
    fetch_latest_videos()