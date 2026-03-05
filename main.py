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
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'ဗီဒီယို ခေါင်းစဉ်မရှိပါ')
        # Caption (စာသား) အပြည့်အစုံကို ယူခြင်း
        description = info.get('description', 'စာသားမရှိပါ')
    return 'input_audio.mp3', title, description

def main_menu_button():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("မူလသို့ပြန်သွားရန်", callback_data="reset")
    markup.add(btn)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "TikTok အသံရှည် (၁ မိနစ်ကျော်) ပြောင်းပေးမည့် Bot မှ ကြိုဆိုပါတယ်! ✨")

@bot.callback_query_handler(func=lambda call: call.data == "reset")
def reset_action(call):
    bot.send_message(call.message.chat.id, "TikTok Link အသစ်တစ်ခု ပေးပို့နိုင်ပါပြီ။")

@bot.message_handler(func=lambda message: "tiktok.com" in message.text)
def handle_tiktok(message):
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in last_used_time and (current_time - last_used_time[user_id] < 600):
        remaining = int((600 - (current_time - last_used_time[user_id])) / 60)
        bot.reply_to(message, f"နောက်ထပ် Video အတွက် {remaining} မိနစ် စောင့်ပေးပါ။")
        return

    try:
        msg = bot.send_message(message.chat.id, "အသံဖိုင်အရှည် ထုတ်ယူနေပါတယ် ခဏစောင့်ပေးပါ... ⚡")
        
        # Audio, Title နဲ့ Description (Caption) တို့ကို ယူခြင်း
        audio_file, video_title, video_desc = download_info_and_audio(message.text)
        
        # Title ရော Caption ရော အကုန်ဖတ်ခိုင်းမှာမို့ အသံရှည်သွားပါလိမ့်မယ်
        myanmar_full_text = f"ဒီဗီဒီယိုရဲ့ ခေါင်းစဉ်ကတော့ {video_title} ဖြစ်ပါတယ်။ အသေးစိတ် အကြောင်းအရာကတော့ {video_desc} ဖြစ်ပါတယ် ခင်ဗျာ။"
        
        tts = gTTS(text=myanmar
