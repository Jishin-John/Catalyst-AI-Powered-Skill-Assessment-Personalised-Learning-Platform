import os
import requests
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"


def search_youtube_videos(skill: str, max_results: int = 3) -> list:
    """
    Searches YouTube for the best beginner videos for a skill.
    Returns top videos sorted by view count.
    """
    try:
        # Search for videos
        search_params = {
            "part": "snippet",
            "q": f"{skill} tutorial for beginners",
            "type": "video",
            "order": "relevance",
            "maxResults": 10,
            "relevanceLanguage": "en",
            "videoDuration": "medium",
            "key": YOUTUBE_API_KEY
        }

        search_response = requests.get(
            YOUTUBE_SEARCH_URL,
            params=search_params
        )
        search_data = search_response.json()

        if "error" in search_data:
            return get_fallback_resources(skill)

        video_ids = [
            item["id"]["videoId"]
            for item in search_data.get("items", [])
            if item["id"].get("videoId")
        ]

        if not video_ids:
            return get_fallback_resources(skill)

        # Get video statistics
        stats_params = {
            "part": "statistics,snippet,contentDetails",
            "id": ",".join(video_ids),
            "key": YOUTUBE_API_KEY
        }

        stats_response = requests.get(
            YOUTUBE_VIDEO_URL,
            params=stats_params
        )
        stats_data = stats_response.json()

        videos = []
        for item in stats_data.get("items", []):
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})

            view_count = int(stats.get("viewCount", 0))
            like_count = int(stats.get("likeCount", 0))

            videos.append({
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "video_id": item["id"],
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                "view_count": view_count,
                "like_count": like_count,
                "view_count_display": format_count(view_count),
                "like_count_display": format_count(like_count)
            })

        # Sort by view count — most viewed first
        videos.sort(key=lambda x: x["view_count"], reverse=True)

        return videos[:max_results]

    except Exception as e:
        return get_fallback_resources(skill)


def format_count(count: int) -> str:
    """
    Formats large numbers — 1000000 becomes 1M
    """
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K"
    else:
        return str(count)


def get_fallback_resources(skill: str) -> list:
    """
    Fallback resources if YouTube API fails.
    """
    return [
        {
            "title": f"Learn {skill} — Search on YouTube",
            "channel": "YouTube",
            "url": f"https://www.youtube.com/results?search_query={skill}+tutorial+beginners",
            "thumbnail": "",
            "view_count_display": "N/A",
            "like_count_display": "N/A"
        }
    ]