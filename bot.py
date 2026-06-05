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
        [InlineKeyboardButton("🎵 Sadece Müzik", callback_data="audio")],
    ]
    await update.message.reply_text(
        "🚀 **İndirme Botu**\n\nPlatform seç ve link gönder.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data[user_id] = {"mode": query.data}
    await query.edit_message_text("✅ Seçildi!\n\nŞimdi linki gönder:")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    data = user_data.get(user_id)
    
    if not data:
        await update.message.reply_text("Önce butonlardan platform seç!")
        return

    url = update.message.text.strip()
    mode = data["mode"]
    msg = await update.message.reply_text("🔄 İndiriliyor...")

    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
    }

    if mode == "audio":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.exists(filename):
            if mode == "audio":
                await update.message.reply_audio(open(filename, 'rb'), caption=info.get('title', 'Müzik'))
            else:
                await update.message.reply_video(open(filename, 'rb'), caption=info.get('title', 'Video'))
            os.remove(filename)
            if user_id in user_data:
                del user_data[user_id]
        else:
            await msg.edit_text("❌ Dosya indirilemedi.")
    except Exception as e:
        await msg.edit_text(f"❌ Hata: {str(e)[:300]}")

# Bot
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

print("🚀 Bot Çalışıyor...")
app.run_polling()
