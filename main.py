import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

SELECTED_USER = {"username": "emilys", "password": "emilyspass"}
BASE_URL = "https://dummyjson.com"


def connectivity_test():
    try:
        login_res = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "username": SELECTED_USER["username"],
                "password": SELECTED_USER["password"],
            },
        )
        if login_res.ok:
            token = login_res.json()["accessToken"]
            return token
        else:
            print(f"❌ Login failed {login_res.status_code}: {login_res.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def get_user_info(headers):
    try:
        user_res = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if user_res.ok:
            return user_res.json()
        else:
            print(f"❌ Failed to get users data: {user_res.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def get_posts(headers, limit=60):
    try:
        posts_res = requests.get(f"{BASE_URL}/posts?limit={limit}", headers=headers)
        if posts_res.ok:
            return posts_res.json()["posts"]
        else:
            print(f"❌ Failed to get posts data: {posts_res.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def get_posts_with_comments(headers, posts):
    posts_with_comments = []

    for post in posts:
        post_id = post["id"]
        try:
            # get comments by post id
            comments_res = requests.get(
                f"{BASE_URL}/posts/{post_id}/comments", headers=headers
            )
            if comments_res.status_code == 200:
                comments = comments_res.json().get("comments", [])
            else:
                print(
                    f"❌ Failed to fetch comments for post {post_id}: {comments_res.status_code} - {comments_res.text}"
                )
                comments = []  # incase it failed put empty array
        except requests.RequestException as e:
            print(f"❌ Error fetching comments for post {post_id}: {e}")
            comments = []

        post["comments"] = comments
        posts_with_comments.append(post)

    return posts_with_comments


def fetch_comments(post, headers):
    post_id = post["id"]
    try:
        res = requests.get(
            f"{BASE_URL}/posts/{post_id}/comments", headers=headers, timeout=5
        )
        if res.status_code == 200:
            post["comments"] = res.json().get("comments", [])
        else:
            print(
                f"❌ Failed to fetch comments for post {post_id}: {res.status_code} - {res.text}"
            )
            post["comments"] = []
    except requests.RequestException as e:
        print(f"❌ Error fetching comments for post {post_id}: {e}")
        post["comments"] = []
    return post


def get_posts_with_comments_faster(headers, posts):
    posts_with_comments = []

    # using threads to fetch the comments faster (10 requests at a time)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_comments, post, headers) for post in posts]
        for future in as_completed(futures):
            post_with_comments = future.result()
            posts_with_comments.append(post_with_comments)

    return posts_with_comments


def main():
    token = connectivity_test()
    if not token:
        print("❌ Failed to get user token...")
        return
    headers = {"Authorization": f"Bearer {token}"}

    user_res = get_user_info(headers)
    if user_res:
        print("\n✅ E1: Authenticated User")
        print(user_res)
        print()

    posts = get_posts(headers)
    if not posts:
        print("❌ Failed to get posts...")
        return
    else:
        print("\n✅ E2: 60 Posts")
        print(posts)

    print("\n✅ E3: 60 Posts with Comments")
    posts_with_comments = []

    # posts_with_comments = get_posts_with_comments(headers, posts)
    # print(posts_with_comments)

    # Note: the original version it pretty slow, so i created 2 versions. one of them uses threads in order to speed
    # up the process
    posts_with_comments = get_posts_with_comments_faster(headers, posts)
    print(posts_with_comments)


if __name__ == "__main__":
    main()
