import os
from dotenv import load_dotenv
import telebot
import yt_dlp

# config.env লोड করা
load_dotenv("config.env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN config.env ফাইলে পাওয়া যায়নি!")

if not OWNER_ID:
    raise ValueError("❌ OWNER_ID config.env ফাইলে পাওয়া যায়নি!")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🎬 লিংক পাঠাও, আমি ভিডিও ডাউনলোড করে দেব!")

@bot.message_handler(content_types=['text'])
def download_video(message):
    url = message.text

    bot.send_message(message.chat.id, "⬇️ ভিডিও ডাউনলোড হচ্ছে... অপেক্ষা করো")

    try:
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': 'downloaded_video.%(ext)s'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        video_path = "downloaded_video.mp4"

        # ইউজারকে ভিডিও পাঠানো
        bot.send_video(message.chat.id, open(video_path, 'rb'), caption="🎉 ভিডিও রেডি!")

        # একই ভিডিও Owner-কেও পাঠানো
        bot.send_video(OWNER_ID, open(video_path, 'rb'),
                       caption=f"📥 নতুন ভিডিও ডাউনলোড করেছে: @{message.from_user.username}\n\n🔗 লিংক:\n{url}"
        )

        os.remove(video_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ সমস্যা: {e}")
        bot.send_message(OWNER_ID, f"⚠️ ইউজারের ভিডিও ডাউনলোডে সমস্যা:\n{e}")

bot.polling(none_stop=True)
