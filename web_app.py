from flask import Flask, render_template, request, redirect, url_for
from movie_api import search_movie, get_popular_movies
from database import create_table, save_movie, get_movies, get_movie, delete_movie, update_movie, get_favorite_movies, get_review_movies
import random
app = Flask(__name__)

create_table()



@app.route("/save", methods=["POST"])
def save():

    movie = {
        "id": request.form["movie_id"],
        "title": request.form["title"],
        "release_date": request.form["release_date"],
        "poster_path": request.form["poster_path"]
        }
    
    save_movie(movie, 0, 0, "")

    keyword = request.form["keyword"]

    return redirect(url_for("search", keyword=keyword))


@app.route("/favorites/edit")
def favorites_edit():
    movies = get_movies()

    return render_template(
        "favorites.html",
        movies=movies,
        edit_mode=True
    )

@app.route("/favorites")
def favorites():
    movies = get_movies()

    return render_template(
        "favorites.html",
        movies=movies,
        edit_mode=False
    )

@app.route("/delete/<int:movie_id>", methods=["POST"])
def delete(movie_id):
    delete_movie(movie_id)
    return redirect("/favorites")

@app.route("/delete_selected", methods=["POST"])
def delete_selected():

    movie_ids = request.form.getlist("selected_movies")

    for movie_id in movie_ids:
        delete_movie(movie_id)

    return redirect("/favorites")

@app.route("/update/<int:movie_id>", methods=["POST"])
def update(movie_id):

    watched = 1 if request.form.get("watched") == "on" else 0
    rating = int(request.form["rating"])
    memo = request.form["memo"]

    update_movie(movie_id, watched, rating, memo)

    return redirect("/favorites")

@app.route("/movie/<int:movie_id>/edit")
def edit_movie(movie_id):

    movie = get_movie(movie_id)

    if movie is None:
        return "映画が見つかりません", 404

    return render_template(
        "edit_movie.html",
        movie=movie
    )

@app.route("/movie/<int:movie_id>/update", methods=["POST"])
def update_movie_route(movie_id):

    watched = 1 if request.form.get("watched") else 0

    rating = int(request.form["rating"])

    memo = request.form["memo"]

    update_movie(movie_id, watched, rating, memo)

    return redirect("/favorites")

@app.route("/")
def home():

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
    app.run(debug=True)