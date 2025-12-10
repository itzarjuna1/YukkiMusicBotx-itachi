import os
import asyncio
from typing import Union
from dotenv import load_dotenv
from googleapiclient.discovery import build
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from YukkiMusic.utils.formatters import time_to_seconds  # Your own formatter module

load_dotenv()  # Load .env file

API_KEY = os.environ.get("YOUTUBE_API_KEY")
YOUTUBE = build("youtube", "v3", developerKey=API_KEY)


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.listbase = "https://youtube.com/playlist?list="

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        # Using youtubesearchpython for quick details
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = 0 if duration_min is None else int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def video(self, link: str, videoid: Union[bool, str] = None):
        """Returns the direct video URL (best quality up to 720p)"""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            f"{link}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def search(self, query: str, limit: int = 5):
        """Search using YouTube API key"""
        request = YOUTUBE.search().list(
            part="snippet",
            q=query,
            maxResults=limit,
            type="video"
        )
        response = request.execute()
        results = []
        for item in response.get("items", []):
            results.append({
                "title": item["snippet"]["title"],
                "link": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                "videoId": item["id"]["videoId"]
            })
        return results
