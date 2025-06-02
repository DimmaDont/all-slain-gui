import requests


def get_webhook(url: str):
    if not url.startswith("https://discord.com/api/webhooks/"):
        return {}

    try:
        return requests.get(url, timeout=5).json()
    except requests.RequestException:
        return {}


def post_webhook(url: str, text: str):
    return requests.post(
        url,
        json={
            "content": f"```ansi\n{text}\n```",
        },
        timeout=5,
    )
