from movie_api import search_movie
from database import (create_table, save_movie, get_movies, delete_movie,
                      update_movie, save_search_history, get_search_history,
                      export_movies_to_csv)

# ============================
# 入力系ユーティリティ関数
# ============================

def get_int_input(message, min_value, max_value):
    while True:
        try:
            value = int(input(message))
            if min_value <= value <= max_value:
                return value
            print(f"{min_value}~{max_value}の数字を入力してください。")
        except ValueError:
            print("数字を入力してください。")

def get_yes_no_input(message):
    while True:
        value = input(message).strip().lower()
        if value in ["y", "n"]:
            return value
        print("y または n を入力してください。")

def get_text_input(message):
    while True:
        value = input(message).strip()
        if value:
            return value
        print("空欄では登録できません。")


# ============================
# メニュー表示
# ============================

def show_menu():
    print("\n=== 映画管理アプリ ===")
    print("1. 映画を検索して保存")
    print("2. お気に入り一覧を表示")
    print("3. 映画を編集")
    print("4. 映画を削除")
    print("5. 検索履歴を表示")
    print("6. CSVに出力")
    print("7. 終了")


# ============================
# お気に入り一覧表示
# ============================

def show_favorites(sort_by="title", watched_filter=None):
    favorites = get_movies(sort_by, watched_filter)

    if not favorites:
        print("\nお気に入りが登録されていません。")
        return favorites

    print("\n=== お気に入り一覧 ===")

    for i, (movie_id, title, release_date, watched, rating, memo) in enumerate(favorites, start=1):
        status = "視聴済み" if watched else "未視聴"
        stars = "★" * rating if rating else "未評価"

        print(f"[{i}] {title}")
        print(f"公開日: {release_date}")
        print(f"視聴状況: {status}")
        print(f"評価: {stars}")
        print(f"感想: {memo}")
        print("-" * 30)

    return favorites


# ============================
# メイン処理
# ============================

def main():
    create_table()

    while True:
        show_menu()
        menu = get_int_input("メニューを選択してください: ", 1, 7)

        # -------------------------
        # 1. 映画検索 → 保存
        # -------------------------
        if menu == 1:
            title = get_text_input("映画タイトルを入力してください: ")
            save_search_history(title)

            movies = search_movie(title)

            if not movies:
                print("映画が見つかりませんでした。")
                continue

            for i, movie in enumerate(movies[:5], start=1):
                print(f"[{i}]: {movie['title']}")
                print(f"公開日: {movie.get('release_date', '不明')}")
                print(f"概要: {movie.get('overview', 'なし')}")
                print("-" * 30)

            choice = get_int_input(
                "保存したい映画の番号を入力してください(0でスキップ): ",
                0, len(movies[:5])
            )

            if 1 <= choice <= len(movies[:5]):
                selected_movie = movies[choice - 1]

                watched = get_yes_no_input("視聴済みですか？(y/n): ")
                watched_flag = 1 if watched == "y" else 0

                rating = get_int_input("評価を入力してください(1~5): ", 1, 5)
                memo = get_text_input("感想を入力してください: ")

                save_movie(selected_movie, watched_flag, rating, memo)
                print("保存しました。")
            else:
                print("保存をキャンセルしました。")

        # -------------------------
        # 2. 一覧表示
        # -------------------------
        elif menu == 2:
            print("\n=== 並び替え ===")
            print("1. タイトル順")
            print("2. 公開日順")
            print("3. 評価順")

            sort_choice = get_int_input(
                "並び順を選択してください: ",
                1,
                3
            )

            sort_map = {
                1: "title",
                2: "release_date",
                3: "rating"
            }

            print("\n=== 絞り込み ===")
            print("1. すべて表示")
            print("2. 視聴済みのみ")
            print("3. 未視聴のみ")

            filter_choice = get_int_input(
                "表示方法を選択してください:",
                1,
                3
            )

            filter_map = {
                1: None,
                2: 1,
                3: 0
            }

            show_favorites(sort_map[sort_choice], filter_map[filter_choice])

        # -------------------------
        # 3. 編集
        # -------------------------
        elif menu == 3:
            favorites = show_favorites()
            if not favorites:
                continue

            choice = get_int_input("編集したい番号を入力してください(0でスキップ): ",
                                   0, len(favorites))

            if choice != 0:
                movie_id = favorites[choice - 1][0]

                watched = get_yes_no_input("視聴済みですか？(y/n): ")
                watched_flag = 1 if watched == "y" else 0

                rating = get_int_input("新しい評価(1~5): ", 1, 5)
                memo = get_text_input("新しい感想: ")

                update_movie(movie_id, watched_flag, rating, memo)
                print("更新しました。")
            else:
                print("編集をキャンセルしました。")

        # -------------------------
        # 4. 削除
        # -------------------------
        elif menu == 4:
            favorites = show_favorites()
            if not favorites:
                continue

            choice = get_int_input(
                "削除したい番号を入力してください(0でスキップ): ",0, len(favorites))

            if choice != 0:
                movie_id = favorites[choice - 1][0]
                title = favorites[choice - 1][1]

                confirm = get_yes_no_input(
                    f"『{title}』を削除しますか？(y/n): "
                )

                if confirm == "y":
                    delete_movie(movie_id)
                    print("削除しました。")
                else:
                    print("削除をキャンセルしました。")

            else:
                print("削除をキャンセルしました。")


        #検索履歴表示機能
        elif menu == 5:
            history = get_search_history()

            if not history:
                print("検索履歴がありません。")
                continue
            print("\n=== 検索履歴 ===")

            for keyword, searched_at in history:
                print(f"{searched_at} : {keyword}")
        
        elif menu == 6:
            export_movies_to_csv()
            print("favorites.csv に出力しました。")

        # -------------------------
        # 5. 終了
        # -------------------------
        elif menu == 7:
            print("アプリを終了します。")
            break


# ============================
# 実行
# ============================

if __name__ == "__main__":
    main()
