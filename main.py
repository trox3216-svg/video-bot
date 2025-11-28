import os
import threading
from flask import Flask
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp

# --- ১. সার্ভারকে খুশি রাখার জন্য নকল ওয়েবসাইট (Flask) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running successfully! (24/7)"

def run_flask():
    # সার্ভারের পোর্ট ডিটেক্ট করা
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- ২. বটের কনফিগারেশন ---
# আপনার টোকেন
TOKEN = '8334541346:AAGFSRYnSrXheMfTb7dRw_HcYEXNFjNH9j4'

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/IftekharRahman")], 
        [InlineKeyboardButton("📢 Channel", url="https://t.me/YourChannelLink")]   
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    img_url = "https://cdn-icons-png.flaticon.com/512/3075/3075977.png"
    
    await update.message.reply_photo(
        photo=img_url,
        caption="<b>স্বাগতম! 🎥</b>\n\nযেকোনো ভিডিওর লিংক দিন, আমি ডাউনলোড করে দেব।",
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if url.startswith('http'):
        context.user_data['url'] = url
        keyboard = [
            [InlineKeyboardButton("🎬 Video (MP4)", callback_data='video'),
             InlineKeyboardButton("🎵 Audio (MP3)", callback_data='audio')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("কি ফরম্যাটে চান?", reply_markup=reply_markup)
    else:
        await update.message.reply_text("দয়া করে সঠিক লিংক দিন।")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    url = context.user_data.get('url')
    
    await query.edit_message_text(f"⏳ <b>{choice.upper()} ডাউনলোড হচ্ছে...</b>", parse_mode='HTML')

    try:
        ydl_opts = {}
        if choice == 'video':
            ydl_opts = {'format': 'best[ext=mp4]', 'outtmpl': 'download.%(ext)s', 'quiet': True}
        else:
            ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'download.%(ext)s', 'quiet': True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Media')

        await query.edit_message_text("⬆️ <b>আপলোড হচ্ছে...</b>", parse_mode='HTML')
        
        chat_id = query.message.chat_id
        file_name = 'download.mp4' if choice == 'video' else 'download.webm'
        
        # ফাইল নাম যাই হোক, খুঁজে বের করা
        for file in os.listdir('.'):
            if file.startswith('download'):
                file_name = file
                break

        if choice == 'video':
            await context.bot.send_video(chat_id=chat_id, video=open(file_name, 'rb'), caption=f"🎬 {title}")
        else:
            await context.bot.send_audio(chat_id=chat_id, audio=open(file_name, 'rb'), caption=f"🎵 {title}")
            
        if os.path.exists(file_name):
            os.remove(file_name)
        await query.delete_message()

    except Exception as e:
        await query.edit_message_text(f"❌ এরর: {e}")

# --- ৩. মেইন রানার (Thread ব্যবহার করে) ---
if __name__ == "__main__":
    # আগে ফ্লাস্ক সার্ভার চালু করা (Background Thread)
    threading.Thread(target=run_flask).start()
    
    # এরপর বট চালু করা
    print("Bot is starting on Server...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', handle_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    
    app.run_polling()
