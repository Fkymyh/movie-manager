import sqlite3
import csv

DB_NAME = "movies.db"

# ============================
# DB接続のヘルパー
# ============================

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn



# ============================
# テーブル作成
# ============================

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            movie_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            release_date TEXT,
            poster_path TEXT,
            is_favorite INTEGER DEFAULT 1,
            watched INTEGER DEFAULT 0,
            rating INTEGER,
            memo TEXT
        )
    """)
    #検索履歴テーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   keyword TEXT NOT NULL,
                   searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ============================
# 映画の保存
# ============================

def save_movie(movie, watched, rating, memo):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO favorites
        (movie_id, title, release_date, poster_path, watched, rating, memo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        movie["id"],
        movie["title"],
        movie.get("release_date", ""),
        movie.get("poster_path", ""),
        watched,
        rating,
        memo
    ))

    conn.commit()
    conn.close()


# ============================
# 映画一覧の取得
# ============================

def get_movies(sort_by="title", watched_filter=None):
    conn = get_connection()
    cursor = conn.cursor()

    order_by = {
        "title": "title ASC",
        "release_date": "release_date DESC",
        "rating": "rating DESC, title ASC"
    }

    sort_column = order_by.get(sort_by, "title ASC")

    sql = """
        SELECT movie_id, title, release_date, poster_path, watched, rating, memo
        FROM favorites
    """

    params = []

    if watched_filter is not None:
        sql += " WHERE watched = ?"
        params.append(watched_filter)
    
    sql += f" ORDER BY {sort_column}"

    cursor.execute(sql, params)

    movies = cursor.fetchall()
    conn.close()

    return movies


# ============================
# 映画の削除
# ============================

def delete_movie(movie_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM favorites
        WHERE movie_id = ?
    """, (movie_id,))

    conn.commit()
    conn.close()


# ============================
# 映画の更新
# ============================

def update_movie(movie_id, watched, rating, memo):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE favorites
        SET watched = ?, rating = ?, memo = ?
        WHERE movie_id = ?
    """, (watched, rating, memo, movie_id))

    conn.commit()
    conn.close()

    #検索履歴を保存する関数
def save_search_history(keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO search_history (keyword)
                   VALUES (?)
        """, (keyword,))
    
    conn.commit()
    conn.close()

    #検索履歴を取得する関数
def get_search_history(limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT keyword, searched_at
        FROM search_history
        ORDER BY searched_at DESC
        LIMIT ?
    """, (limit,))

    history = cursor.fetchall()

    conn.close()

    return history

def export_movies_to_csv(filename="favorites.csv"):
    movies = get_movies()

    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)

        writer.writerow([
            "タイトル",
            "公開日",
            "視聴状況",
            "評価",
            "感想"
        ])

        for _, title, release_date, _, watched, rating, memo in movies:
            writer.writerow([
                title,
                release_date,
                "視聴済み" if watched else "未視聴",
                rating,
                memo
            ])

def get_movie(movie_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT movie_id, title, release_date, poster_path,
               watched, rating, memo
        FROM favorites
        WHERE movie_id = ?
    """, (movie_id,))

    movie = cursor.fetchone()

    conn.close()

    return movie

def get_favorite_movies(limit=6):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT movie_id, title, poster_path
        FROM favorites
        WHERE is_favorite = 1
        ORDER BY movie_id DESC
        LIMIT ?
    """, (limit,))

    movies = cursor.fetchall()

    conn.close()

    return movies


def get_review_movies(limit=6):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT movie_id, title, poster_path
        FROM favorites
        WHERE memo != '' OR rating > 0
        ORDER BY movie_id DESC
        LIMIT ?
    """, (limit,))

    movies = cursor.fetchall()

    conn.close()

    return movies