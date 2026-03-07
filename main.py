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
            'preferredquality': '192', # High Quality ဖြစ်အောင် 192 ထားထားပါတယ်
        }],
        'quiet': True,
        'max_filesize': 20 * 1024 * 1024, # 20MB အထိ ခွင့်ပြုပေးထားပါတယ်
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'ဗီဒီယို ခေါင်းစဉ်မရှိပါ')
        description = info.get('description', 'အသေးစိတ်စာသား မရှိပါ')
    return 'input_audio.mp3', title, description

def main_menu_button():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("မူလသို့ပြန်သွားရန်", callback_data="reset")
    markup.add(btn)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "TikTok အသံရှည် မြန်မာလိုပြောင်းပေးမည့် Bot မှ ကြိုဆိုပါတယ်! ✨\nKey မလိုဘဲ စိတ်ချလက်ချ သုံးနိုင်ပါပြီ။")

@bot.callback_query_handler(func=lambda call: call.data == "reset")
def reset_action(call):
    bot.send_message(call.message.chat.id, "TikTok Link အသစ်တစ်ခု ပေးပို့နိုင်ပါပြီ။")

@bot.message_handler(func=lambda message: "tiktok.com" in message.text)
def handle_tiktok(message):
    user_id = message.from_user.id
    current_time = time.time()

    # ၁၀ မိနစ် Cooldown
    if user_id in last_used_time and (current_time - last_used_time[user_id] < 600):
        remaining = int((600 - (current_time - last_used_time[user_id])) / 60)
        bot.reply_to(message, f"နောက်ထပ် Video အတွက် {remaining} မိနစ် စောင့်ပေးပါဦး။")
        return

    try:
        msg = bot.send_message(message.chat.id, "အသံဖိုင်အရှည် ထုတ်ယူနေပါတယ် ခဏစောင့်ပေးပါ... ⚡")
        audio_file, video_title, video_desc = download_info_and_audio(message.text)
        
        # အသံဖိုင် ရှည်ရှည်ရအောင် စာသားများကို စုစည်းခြင်း
        full_text = f"မင်္ဂလာပါ ခင်ဗျာ။ အခု ဗီဒီယိုရဲ့ ခေါင်းစဉ်ကတော့ {video_title} ဖြစ်ပါတယ်။ "
        full_text += f"ဒီဗီဒီယိုမှာ ရေးသားထားတဲ့ အကြောင်းအရာတွေကတော့ {video_desc} တို့ပဲ ဖြစ်ပါတယ်။ "
        full_text += "ဗီဒီယိုကို အဆုံးထိ နားဆင်ပေးတဲ့အတွက် ကျေးဇူးတင်ပါတယ်။ နောက်ထပ် ဗီဒီယိုတွေမှာ ပြန်လည် ဆုံတွေ့ကြပါမယ် ခင်ဗျာ။"
        
        # မြန်မာလို အသံထွက်ပေးခြင်း
        tts = gTTS(text=full_text, lang='my')
        tts.save("temp.mp3")
        
        # အသံကို ပုံမှန်အရှိန် (1.0) နဲ့ပဲ ထားထားလို့ အသံဖိုင် ပိုရှည်ရှည်ထွက်လာမှာပါ
        sound = AudioSegment.from_file("temp.mp3")
        final_filename = "recap_audio.mp3"
        sound.export(final_filename, format="mp3")
        
        with open(final_filename, 'rb') as audio:
            bot.send_audio(
                message.chat.id, 
                audio, 
                caption=f"📝 ခေါင်းစဉ် - {video_title}\n\n(မြန်မာအသံဖြင့် ၁ မိနစ်ကျော် ၂ မိနစ်စာ ဖတ်ပြထားပါသည်။)", 
                reply_markup=main_menu_button()
            )
        
        last_used_time[user_id] = current_time
        if os.path.exists(audio_file): os.remove(audio_file)
        if os.path.exists("temp.mp3"): os.remove("temp.mp3")
        if os.path.exists(final_filename): os.remove(final_filename)
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}\nခဏနေမှ ပြန်စမ်းကြည့်ပါဦး။", reply_markup=main_menu_button())

bot.polling()
