from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

TOKEN = "8818895591:AAGH577sseS4urhHVhWHjz6ciDK3hS7DhMA"

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎥 YouTube", callback_data="yt")],
        [InlineKeyboardButton("📱 TikTok", callback_data="tt")],
        [InlineKeyboardButton("📷 Instagram", callback_data="ig")],
    ]
    await update.message.reply_text(
        "🚀 **Ultra Downloader Bot v2**\n\n"
        "Platform seç → Kalite seç → Link at",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    platform = query.data
    user_data[user_id] = {"platform": platform, "step": "quality"}

    keyboard = [
        [InlineKeyboardButton("Best Kalite", callback_data="q_best")],
        [InlineKeyboardButton("1080p", callback_data="q_1080")],
        [InlineKeyboardButton("720p", callback_data="q_720")],
        [InlineKeyboardButton("🎵 Sadece MP3", callback_data="q_audio")],
    ]
    await query.edit_message_text("Kalite seç:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    data = user_data.get(user_id)
    if not data or data.get("step") != "quality":
        await update.message.reply_text("Önce menüden seçim yap!")
        return

    url = update.message.text.strip()
    msg = await update.message.reply_text("🔄 İndiriliyor...")

    opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
    }

    if data["platform"] == "yt":
        opts['cookiesfrombrowser'] = 'chrome'   # Bu satır çok önemli

    if data.get("quality") == "q_audio":
        opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]})
    elif data.get("quality") == "q_1080":
        opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'
    elif data.get("quality") == "q_720":
        opts['format'] = 'bestvideo[height<=720]+bestaudio/best'

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.exists(filename):
            if "audio" in data.get("quality", ""):
                await update.message.reply_audio(open(filename, 'rb'), caption=info.get('title', 'Müzik'))
            else:
                await update.message.reply_video(open(filename, 'rb'), caption=info.get('title', 'Video'))
            os.remove(filename)
            del user_data[user_id]
        else:
            await msg.edit_text("❌ Dosya bulunamadı.")
    except Exception as e:
        await msg.edit_text(f"❌ Hata: {str(e)[:200]}")

# Bot
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

app.run_polling()
