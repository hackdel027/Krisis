from core.ransomlook import RansomLookClient


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_recent_posts_uses_documented_base_url(monkeypatch):
    calls = []

    def fake_get(url, timeout, params=None):
        calls.append((url, params))
        assert timeout == 15
        return FakeResponse({
            "posts": [{"post_title": "Example victim", "discovered": "2026-09-01T12:00:00Z"}]
        })

    monkeypatch.setattr("core.ransomlook.requests.get", fake_get)

    client = RansomLookClient()
    posts = client.recent_posts()

    assert calls[0][0] == "https://www.ransomlook.io/api/posts"
    assert calls[0][1] == {"days": 7}
    assert posts[0]["post_title"] == "Example victim"


def test_search_uses_documented_search_endpoint(monkeypatch):
    calls = []

    def fake_get(url, timeout, params=None):
        calls.append((url, params))
        return FakeResponse([
            {"post_title": "Acme Corp", "description": "Ransomware publication"},
            {"post_title": "Other Corp", "description": "No match"},
        ])

    monkeypatch.setattr("core.ransomlook.requests.get", fake_get)

    client = RansomLookClient()
    posts = client.search("acme")

    assert calls[0][0] == "https://www.ransomlook.io/api/search"
    assert calls[0][1] == {"query": "acme"}
    assert [post["post_title"] for post in posts] == ["Acme Corp"]


def test_groups_handles_documented_array_of_names(monkeypatch):
    monkeypatch.setattr(
        "core.ransomlook.requests.get",
        lambda url, timeout, params=None: FakeResponse(["lockbit", "blackcat"]),
    )

    client = RansomLookClient()
    groups = client.groups()

    assert groups == ["lockbit", "blackcat"]
