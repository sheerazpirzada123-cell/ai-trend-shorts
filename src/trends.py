import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


def get_google_trends():
    url = "https://trends.google.com/trending/rss?geo=US"

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read()

        root = ET.fromstring(data)

        trends = []

        for item in root.findall(".//item"):
            title = item.findtext("title")

            if title:
                trends.append(title.strip())

        return trends[:20]

    except Exception as e:
        print("Google Trends error:", e)
        return []


def get_reddit_trends():
    subreddits = [
        "popular",
        "interestingasfuck",
        "Damnthatsinteresting",
        "AnimalsBeingDerps"
    ]

    trends = []

    for subreddit in subreddits:

        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"

        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "AI-Trend-Shorts/1.0"
                }
            )

            with urllib.request.urlopen(request, timeout=20) as response:
                data = json.loads(response.read())

            posts = data.get("data", {}).get("children", [])

            for post in posts:
                post_data = post.get("data", {})
                title = post_data.get("title")

                if title:
                    trends.append(title.strip())

        except Exception as e:
            print(f"Reddit error ({subreddit}):", e)

    return trends[:30]


def clean_trends(trends):

    cleaned = []

    for trend in trends:

        trend = " ".join(trend.split())

        if len(trend) < 5:
            continue

        if trend not in cleaned:
            cleaned.append(trend)

    return cleaned


def main():

    print("================================")
    print("AI TREND SHORTS - TREND RESEARCH")
    print("================================")

    google = get_google_trends()
    reddit = get_reddit_trends()

    all_trends = clean_trends(google + reddit)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "trends": all_trends
    }

    with open("trends.json", "w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(f"\nFound {len(all_trends)} trends.\n")

    for number, trend in enumerate(all_trends, 1):
        print(f"{number}. {trend}")


if __name__ == "__main__":
    main()
