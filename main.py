import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp

# আপনার টোকেন
TOKEN = '8334541346:AAGFSRYnSrXheMfTb7dRw_HcYEXNFjNH9j4'

# ১. স্টার্ট হ্যান্ডলার
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

# ২. মেসেজ হ্যান্ডলার
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if url.startswith('http'):
        context.user_data['url'] = url
        keyboard = [
            [
                InlineKeyboardButton("🎬 Video (MP4)", callback_data='video'),
                InlineKeyboardButton("🎵 Audio (MP3)", callback_data='audio')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("কি ফরম্যাটে চান?", reply_markup=reply_markup)
    else:
        await update.message.reply_text("দয়া করে সঠিক লিংক দিন।")

# ৩. বাটন হ্যান্ডলার
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
            # সার্ভারে FFmpeg সমস্যা এড়াতে সাধারণ অডিও ফরম্যাট রাখা হলো
            ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'download.%(ext)s', 'quiet': True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Media')

        await query.edit_message_text("⬆️ <b>আপলোড হচ্ছে...</b>", parse_mode='HTML')
        
        chat_id = query.message.chat_id
        file_name = 'download.mp4' if choice == 'video' else 'download.webm' 
        # yt-dlp অডিও হিসেবে webm বা m4a নামাতে পারে যদি ffmpeg না থাকে
        
        # ফাইল খোঁজা (এক্সটেনশন যা-ই হোক)
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

# ৪. সার্ভার রানার (Colab থেকে আলাদা)
if __name__ == "__main__":
    print("Bot is starting on Server...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', handle_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    
    app.run_polling()
