import os
import requests
import yt_dlp
from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID

# --- Keep Alive ---
from keep_alive import keep_alive
keep_alive()

# --- Media Folder ---
if not os.path.exists("media"):
    os.makedirs("media")

# --- Pyrogram Client ---
bot = Client(
    "downloader_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ------------ URL Auto Expand ---------------
def expand_url(url):
    try:
        r = requests.head(url, allow_redirects=True, timeout=10)
        return r.url
    except:
        return url

# ------------ Normal 4K Downloader ------------
def download_data(url, mp3=False):
    ydl_opts = {
        "outtmpl": "media/%(title)s.%(ext)s",
        "writethumbnail": True,
        "quiet": True,
        "merge_output_format": "mp4",
    }

    if mp3:
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320"
            }]
        })
    else:
        ydl_opts["format"] = "bestvideo+bestaudio/best"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info

# ------------ TikTok No Watermark Downloader ------------
def download_tiktok_nowm(url):
    ydl_opts = {
        "format": "bv*+ba/b",
        "outtmpl": "media/%(title)s_nowm.%(ext)s",
        "writethumbnail": True,
        "quiet": True,
        "merge_output_format": "mp4",
        "extractor_args": {
            "tiktok": {
                "no_watermark": True
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info

# ------------ Smart Downloader -------------
@bot.on_message(filters.regex(r'https?://'))
async def smart_downloader(client, message):
    url = message.text.strip()
    real_url = expand_url(url)
    wait = await message.reply("🔍 লিংক পরীক্ষা করা হচ্ছে…")

    # TikTok
    if "tiktok.com" in real_url or "vm.tiktok.com" in real_url:
        await wait.edit("🎵 TikTok ভিডিও (No Watermark) ডাউনলোড হচ্ছে…")
        info = download_tiktok_nowm(real_url)
        title = info.get("title", "tiktok")
        filename = f"media/{title}_nowm.mp4"

        # Thumbnail
        thumb = None
        for f in os.listdir("media"):
            if f.endswith((".jpg",".png",".webp")):
                thumb = f"media/{f}"

        await wait.edit("⬆️ আপলোড হচ্ছে…")
        await message.reply_video(filename, caption=f"🎬 {title}\n(No Watermark)", thumb=thumb)
        await client.send_video(CHANNEL_ID, filename, caption=f"🎬 {title}")

        os.remove(filename)
        if thumb: os.remove(thumb)
        await wait.delete()
        return

    # Normal 4K Downloader
    await wait.edit("📥 ভিডিও ডাউনলোড হচ্ছে (4K চেষ্টা করা হচ্ছে)…")
    info = download_data(real_url)
    title = info.get("title", "video")
    filename = f"media/{title}.mp4"

    thumb = None
    for f in os.listdir("media"):
        if f.endswith((".jpg",".png",".webp")):
            thumb = f"media/{f}"

    await wait.edit("⬆️ আপলোড হচ্ছে…")
    await message.reply_video(filename, caption=title, thumb=thumb)
    await client.send_video(CHANNEL_ID, filename, caption=title)

    os.remove(filename)
    if thumb: os.remove(thumb)
    await wait.delete()

# ------------ MP3 Downloader -------------
@bot.on_message(filters.command("mp3"))
async def mp3_down(client, message):
    try:
        url = message.text.split(maxsplit=1)[1]
    except:
        return await message.reply("❗ ব্যবহার: /mp3 <url>")

    wait = await message.reply("🎧 MP3 এক্সট্র্যাক্ট করা হচ্ছে…")
    info = download_data(url, mp3=True)
    title = info.get("title", "audio")
    filename = f"media/{title}.mp3"

    await message.reply_audio(filename, caption=f"🎵 {title}")
    await client.send_audio(CHANNEL_ID, filename, caption=f"🎵 {title}")

    os.remove(filename)
    await wait.delete()

# ------------ Run Bot -------------
bot.run()
