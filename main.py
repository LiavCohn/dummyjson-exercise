from APIClient import DummyJsonClient

SELECTED_USER = {"username": "emilys", "password": "emilyspass"}
BASE_URL = "https://dummyjson.com"


def main():
    dummyjson_client = DummyJsonClient(
        SELECTED_USER["username"], SELECTED_USER["password"]
    )
    # if connectivity test succeeded
    if dummyjson_client.login():
        user = dummyjson_client.get_user()
        print("\n E1: Authenticated User")
        print(user)
        print()

        posts = dummyjson_client.get_posts()
        print("\n E2: 60 Posts")
        print(posts)
        print()

        posts_with_comments = dummyjson_client.get_post_comments()
        print("\n E3: 60 Posts with Comments")
        print(posts_with_comments)
        print()


if __name__ == "__main__":
    main()
