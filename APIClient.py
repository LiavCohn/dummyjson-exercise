from concurrent.futures import ThreadPoolExecutor, as_completed
import requests


class BaseAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {}

    def make_request(self, method, endpoint, payload=None, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                json=payload,
                params=params,
                timeout=5,
            )
            response.raise_for_status()  # raise an exception if got an invalid http code
            return response.json()
        except requests.RequestException as e:
            print(f"Error during request: {e}")
            return None


class DummyJsonClient(BaseAPIClient):
    def __init__(self, username, password):
        super().__init__("https://dummyjson.com")
        self.username = username
        self.password = password
        self.token = None
        self.posts = []

    # connectivity test
    def login(self):
        res = self.make_request(
            "POST",
            "/auth/login",
            payload={"username": self.username, "password": self.password},
        )
        if res and "accessToken" in res:
            self.token = res["accessToken"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            return True
        return False

    def get_user(self):
        return self.make_request("GET", "/auth/me")

    def get_posts(self, limit=60):
        res = self.make_request("GET", f"/posts", params={"limit": limit})
        if res:
            self.posts = res["posts"]
        return self.posts

    def fetch_comments(self, post):
        post_id = post["id"]
        comments = self.make_request("GET", f"/posts/{post_id}/comments")
        post["comments"] = comments if comments else []
        return post

    def get_post_comments(self):
        posts_with_comments = []

        # using threads to fetch the comments faster (10 requests at a time)
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(self.fetch_comments, post) for post in self.posts
            ]
            for future in as_completed(futures):
                post_with_comments = future.result()
                posts_with_comments.append(post_with_comments)

        return posts_with_comments
