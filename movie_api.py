import os
import random
import requests
from dotenv import load_dotenv

# .envからTMDBのAPIキーを環境変数へ読み込む。
load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

# ============================
# 映画検索（TMDB API）
# ============================

def search_movie(title):
    """TMDBでタイトルを検索し、公開日の古い順に映画情報を返す。"""
    if not API_KEY:
        print("⚠ TMDB_API_KEY が設定されていません。.env を確認してください。")
        return []

    url = "https://api.themoviedb.org/3/search/movie"

    params = {
        "api_key": API_KEY,
        "query": title,
        "language": "ja-JP"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # HTTPエラーを検出

        data = response.json()
        movies = data.get("results", [])

        # 公開日がない作品は末尾へ配置する。
        movies.sort(key=lambda movie: movie.get("release_date") or "9999-12-31")

        return movies

    except requests.exceptions.RequestException as e:
        print("APIリクエスト中にエラーが発生しました:", e)
        return []
    
def get_popular_movies():
    """背景表示用として、TMDBの人気映画をランダムなページから取得する。"""
    if not API_KEY:
        return []
    
    # 毎回異なる背景になるよう、人気映画の取得ページもランダムに選ぶ。
    page = random.randint(1, 50)

    url = "https://api.themoviedb.org/3/movie/popular"

    params = {
        "api_key": API_KEY,
        "language": "ja-JP",
        "page": page
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        movies = data.get("results", [])

        random.shuffle(movies)

        return movies

    except requests.exceptions.RequestException:
        return []
