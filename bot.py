from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

TOKEN = "8818895591:AAGH577sseS4urhHVhWHjz6ciDK3hS7DhMA"

# Kullanıcı verilerini tutmak için
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎥 YouTube", callback_data="platform_yt")],
        [InlineKeyboardButton("📱 TikTok", callback_data="platform_tt")],
        [InlineKeyboardButton("📷 Instagram", callback_data="platform_ig")],
    ]
    await update.message.reply_text(
        "🚀 **Ultra İndirme Botu**\n\n"
        "Aşağıdan platform seç, sonra kalite ve link at.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data.startswith("platform_"):
        platform = query.data.split("_")[1]
        user_data[user_id] = {"platform": platform, "step": "quality"}
        
        keyboard = [
            [InlineKeyboardButton("🔝 Best Kalite", callback_data="quality_best")],
            [InlineKeyboardButton("📹 1080p", callback_data="quality_1080")],
            [InlineKeyboardButton("📺 720p", callback_data="quality_720")],
            [InlineKeyboardButton("🎵 Sadece Ses (MP3)", callback_data="quality_audio")],
        ]
        await query.edit_message_text("✅ Platform seçildi.\nŞimdi kalite seç:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("quality_"):
        quality = query.data.split("_")[1]
        user_data[user_id]["quality"] = quality
        user_data[user_id]["step"] = "link"
        await query.edit_message_text("✅ Kalite seçildi.\n\nŞimdi linki gönder:")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    data = user_data.get(user_id)

    if not data or data.get("step") != "link":
        await update.message.reply_text("Önce menüden platform ve kalite seç!")
        return

    url = update.message.text.strip()
    msg = await update.message.reply_text("🔄 İndiriliyor... Bu işlem biraz uzun sürebilir.")

    # Kalite ayarları
    quality = data["quality"]
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
    }

    if quality == "audio":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]
        })
    elif quality == "1080":
        ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'
    elif quality == "720":
        ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best'
    elif quality == "480":
        ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.exists(filename):
            if quality == "audio":
                await update.message.reply_audio(open(filename, 'rb'), caption=f"🎵 {info.get('title', 'Müzik')}")
            else:
                await update.message.reply_video(open(filename, 'rb'), caption=f"🎥 {info.get('title', 'Video')}")
            os.remove(filename)
            
            # Temizle
            if user_id in user_data:
                del user_data[user_id]
        else:
            await msg.edit_text("❌ Dosya indirilemedi.")
    except Exception as e:
        await msg.edit_text(f"❌ Hata: {str(e)[:250]}")

# Bot Başlatma
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

print("🚀 Ultra Bot Çalışıyor...")
app.run_polling()
