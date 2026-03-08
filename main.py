import os
import telebot
import yt_dlp
from gtts import gTTS
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
        title = info.get('title', 'ဗီဒီယို ခေါင်းစဉ်')
        description = info.get('description', 'အသေးစိတ်စာသား မရှိပါ')
    return title, description

@bot.message_handler(func=lambda message: "tiktok.com" in message.text)
def handle_tiktok(message):
    try:
        msg = bot.send_message(message.chat.id, "အသံဖိုင်ကို စနစ်တကျ ပြင်ဆင်နေပါပြီ... ခဏစောင့်ပေးပါ ⚡")
        
        # Audio ဖိုင်အစား စာသားကို အရင်ယူမယ်
        video_title, video_desc = download_info_and_audio(message.text)
        
        # အသံဖိုင် ရှည်ရှည်ရအောင် စာသားကို သေချာစီစဉ်ခြင်း
        full_text = f"မင်္ဂလာပါ ခင်ဗျာ။ အခု ဗီဒီယိုရဲ့ ခေါင်းစဉ်ကတော့ {video_title} ဖြစ်ပါတယ်။ "
        full_text += f"ဒီဗီဒီယိုမှာ ရေးသားထားတဲ့ အကြောင်းအရာတွေကတော့ {video_desc} တို့ပဲ ဖြစ်ပါတယ်။ "
        full_text += "ဗီဒီယိုကို အဆုံးထိ နားဆင်ပေးတဲ့အတွက် ကျေးဇူးတင်ပါတယ်။"
        
        # Google TTS ဖြင့် အသံဖိုင်ထုတ်ခြင်း (အသံအရည်အသွေး ကောင်းအောင်)
        tts = gTTS(text=full_text, lang='my', slow=False)
        tts.save("recap_audio.mp3")
        
        with open("recap_audio.mp3", 'rb') as audio:
            bot.send_audio(
                message.chat.id, 
                audio, 
                caption=f"📝 ခေါင်းစဉ် - {video_title}\n(အသံ အရည်အသွေးကောင်းဖြင့် တင်ပေးလိုက်ပါပြီ။)"
            )
        
        if os.path.exists("recap_audio.mp3"): os.remove("recap_audio.mp3")
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

bot.polling()
