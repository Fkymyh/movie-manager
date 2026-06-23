import os
import random
import requests
from dotenv import load_dotenv

# .env の読み込み
load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

# ============================
# 映画検索（TMDB API）
# ============================

def search_movie(title):
    if not API_KEY:
        print("⚠ TMDB_API_KEY が設定されていません。.env を確認してください。")
        

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

        movies.sort(
            key=lambda movie: movie.get("release_date", "9999-12-31")
        )

        return movies

    except requests.exceptions.RequestException as e:
        print("APIリクエスト中にエラーが発生しました:", e)
        return []
    
def get_popular_movies():
    if not API_KEY:
        return []
    
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
