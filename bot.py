from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

TOKEN = "8818895591:AAGH577sseS4urhHVhWHjz6ciDK3hS7DhMA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 Gelişmiş Profil Fotoğrafı Botu\n\n"
        "Kullanım:\n"
        "• /pp → Kendi fotoğrafın\n"
        "• Bir mesaja reply yapıp /pp → O kişinin fotoğrafı\n"
        "• /pp @username → Belirtilen kişinin fotoğrafı"
    )

async def pp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Reply varsa reply yapılan kişiyi al
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
    else:
        # Komut argümanı varsa (@username)
        if context.args:
            try:
                user = await context.bot.get_chat(context.args[0].replace("@", ""))
            except:
                await update.message.reply_text("❌ Kullanıcı bulunamadı!")
                return
        else:
            # Hiçbiri yoksa kendi profil
            user = update.message.from_user

    if not user:
        await update.message.reply_text("❌ Kullanıcı bulunamadı.")
        return

    try:
        photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        
        if photos.total_count > 0:
            photo = photos.photos[0][-1]  # En büyük boyut
            await update.message.reply_photo(
                photo.file_id,
                caption=f"👤 **{user.first_name}**'nin Profil Fotoğrafı\n"
                        f"ID: `{user.id}`\n"
                        f"Username: @{user.username if user.username else 'Yok'}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(f"❌ **{user.first_name}**'nin profil fotoğrafı yok.")
    except Exception as e:
        await update.message.reply_text("❌ Profil fotoğrafı alınamadı.")

# ====================== BOT ======================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler(["pp", "profil", "foto"], pp))

print("✅ Gelişmiş Profil Fotoğrafı Botu Çalışıyor...")
app.run_polling()
