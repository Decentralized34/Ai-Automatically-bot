import os
import telebot
import yt_dlp
from gtts import gTTS
from pydub import AudioSegment
from telebot import types
import time

# --- Telegram Bot Token ---
API_TOKEN = '7996638463:AAGF7s3FJnOy_9MNspJfg_CSvtS2uQoO0ZA'

bot = telebot.TeleBot(API_TOKEN)
last_used_time = {}

def download_info_and_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'input_audio.%(ext)s',
        # TikTok Block ကျော်ရန် Header များ
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/',
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'TikTok Video')
    return 'input_audio.mp3', title

def main_menu_button():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("မူလသို့ပြန်သွားရန်", callback_data="reset")
    markup.add(btn)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "TikTok AI Recap Bot (Fixed Version) မှ ကြိုဆိုပါတယ်! ✨\nLink ပေးပို့နိုင်ပါပြီ။")

@bot.callback_query_handler(func=lambda call: call.data == "reset")
def reset_action(call):
    bot.send_message(call.message.chat.id, "TikTok Link အသစ်တစ်ခု ပေးပို့နိုင်ပါပြီ။")

@bot.message_handler(func=lambda message: "tiktok.com" in message.text)
def handle_tiktok(message):
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in last_used_time:
        time_diff = current_time - last_used_time[user_id]
        if time_diff < 600:
            remaining = int((600 - time_diff) / 60)
            bot.reply_to(message, f"နောက်ထပ် Video တစ်ခုအတွက် {remaining} မိနစ် ထပ်စောင့်ပေးပါဦး။")
            return

    try:
        msg = bot.send_message(message.chat.id, "ဆောင်ရွက်နေပါတယ် ⚡")
        
        audio_file, video_title = download_info_and_audio(message.text)
        
        tts = gTTS(text=f"ဒီဗီဒီယိုရဲ့ အကြောင်းအရာကတော့ {video_title} ဖြစ်ပါတယ်", lang='my')
        tts.save("temp.mp3")
        
        sound = AudioSegment.from_file("temp.mp3")
        faster_sound = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * 1.3)
        }).set_frame_rate(sound.frame_rate)
        
        final_filename = "recap_audio.mp3"
        faster_sound.export(final_filename, format="mp3")
        
        with open(final
