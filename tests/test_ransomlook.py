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

    def fake_get(url, timeout):
        calls.append(url)
        assert timeout == 15
        return FakeResponse([
            {"post_title": "Example victim", "discovered": "2026-09-01T12:00:00Z"}
        ])

    monkeypatch.setattr("core.ransomlook.requests.get", fake_get)

    client = RansomLookClient()
    posts = client.recent_posts()

    assert calls == ["https://www.ransomlook.io/api/recent"]
    assert posts[0]["post_title"] == "Example victim"


def test_search_works_on_real_post_schema(monkeypatch):
    monkeypatch.setattr(
        "core.ransomlook.requests.get",
        lambda url, timeout: FakeResponse([
            {"post_title": "Acme Corp", "description": "Ransomware publication"},
            {"post_title": "Other Corp", "description": "No match"},
        ]),
    )

    client = RansomLookClient()
    posts = client.search("acme")

    assert [post["post_title"] for post in posts] == ["Acme Corp"]
