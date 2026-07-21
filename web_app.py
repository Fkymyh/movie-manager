from flask import Flask, abort, render_template, request, redirect, url_for
from movie_api import search_movie, get_popular_movies
from database import (create_table, delete_movie, get_favorite_movies, get_movie,
                      get_movies, get_review_movies, get_reviews, save_movie,
                      update_movie)

app = Flask(__name__)

# Webサーバー起動時に、必要なテーブルが存在することを保証する。
create_table()


def get_rating_from_form():
    """フォームの評価を整数へ変換し、1〜5以外ならHTTP 400で拒否する。"""
    try:
        rating = int(request.form["rating"])
    except (KeyError, TypeError, ValueError):
        abort(400, description="評価は1〜5の整数で指定してください。")

    if not 1 <= rating <= 5:
        abort(400, description="評価は1〜5の整数で指定してください。")
    return rating



@app.route("/save", methods=["POST"])
def save():
    """検索結果のフォーム値から映画をマイリストへ保存する。"""
    try:
        movie_id = int(request.form["movie_id"])
        title = request.form["title"].strip()
    except (KeyError, TypeError, ValueError):
        abort(400, description="映画情報が不正です。")

    if movie_id <= 0 or not title:
        abort(400, description="映画情報が不正です。")

    movie = {
        "id": movie_id,
        "title": title,
        "release_date": request.form.get("release_date", ""),
        "poster_path": request.form.get("poster_path", "")
    }
    
    save_movie(movie, 0, 0, "")

    keyword = request.form.get("keyword", "")

    return redirect(url_for("search", keyword=keyword))


@app.route("/favorites/edit")
def favorites_edit():
    """複数選択による削除操作ができるマイリストを表示する。"""
    movies = get_movies()

    return render_template(
        "favorites.html",
        movies=movies,
        edit_mode=True
    )

@app.route("/favorites")
def favorites():
    """通常表示のマイリストを表示する。"""
    movies = get_movies()

    return render_template(
        "favorites.html",
        movies=movies,
        edit_mode=False
    )


@app.route("/reviews")
def reviews():
    """評価または感想を記録した映画の一覧を表示する。"""
    return render_template(
        "favorites.html",
        movies=get_reviews(),
        edit_mode=False,
        page_title="レビュー済み"
    )

@app.route("/delete/<int:movie_id>", methods=["POST"])
def delete(movie_id):
    """指定された映画を1件削除し、マイリストへ戻る。"""
    delete_movie(movie_id)
    return redirect("/favorites")

@app.route("/delete_selected", methods=["POST"])
def delete_selected():
    """フォームで選択された複数の映画を順番に削除する。"""

    movie_ids = request.form.getlist("selected_movies")

    for movie_id in movie_ids:
        delete_movie(movie_id)

    return redirect("/favorites")

@app.route("/update/<int:movie_id>", methods=["POST"])
def update(movie_id):
    """一覧画面から送信された視聴状態、評価、感想を更新する。"""

    watched = 1 if request.form.get("watched") == "on" else 0
    rating = get_rating_from_form()
    memo = request.form.get("memo", "")

    update_movie(movie_id, watched, rating, memo)

    return redirect("/favorites")

@app.route("/movie/<int:movie_id>/edit")
def edit_movie(movie_id):
    """指定された映画の編集画面を表示する。"""

    movie = get_movie(movie_id)

    if movie is None:
        return "映画が見つかりません", 404

    return render_template(
        "edit_movie.html",
        movie=movie
    )

@app.route("/movie/<int:movie_id>/update", methods=["POST"])
def update_movie_route(movie_id):
    """映画編集画面の入力を保存し、マイリストへ戻る。"""

    watched = 1 if request.form.get("watched") else 0

    if get_movie(movie_id) is None:
        abort(404, description="映画が見つかりません。")

    rating = get_rating_from_form()
    memo = request.form.get("memo", "")

    update_movie(movie_id, watched, rating, memo)

    return redirect("/favorites")

@app.route("/")
def home():
    """マイリストの抜粋と背景用の人気映画をホーム画面へ渡す。"""

    favorite_movies = get_favorite_movies()
    review_movies = get_review_movies()
    
    background_movies = get_popular_movies()

    return render_template(
        "home.html",
        favorite_movies=favorite_movies,
        review_movies=review_movies,
        background_movies=background_movies

    )

@app.route("/search")
def search():
    """クエリ文字列のキーワードでTMDBを検索し、結果を表示する。"""

    keyword = request.args.get("keyword", "")
    movies = []

    if keyword:
        movies = search_movie(keyword)

    return render_template(
        "search.html",
        movies=movies,
        keyword=keyword

    )

if __name__ == "__main__":
    # デバッグモードは必要な場合だけFLASK_DEBUG環境変数で有効にする。
    app.run()
