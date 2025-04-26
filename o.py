import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = '8003231767:AAGewSQTTDGH64C1ADdW14OGWu4yqxmquY8'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_data():
    try:
        with open('saldo.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open('saldo.json', 'w') as file:
        json.dump(data, file, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Selamat datang di Mayugoro Store\n\n"
        "Untuk melanjutkan, ketik /menu"
    )

async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_data = get_user_data()

    saldo = user_data.get(user_id, {}).get("saldo", 0)
    await update.message.reply_text(f"Saldo Anda: Rp {saldo}")

async def topup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_data = get_user_data()

    try:
        amount = int(context.args[0])
        if amount <= 0:
            await update.message.reply_text("Jumlah top-up tidak valid. Harap masukkan jumlah yang positif.")
            return

        if user_id not in user_data:
            user_data[user_id] = {"saldo": 0}

        user_data[user_id]["saldo"] += amount
        save_user_data(user_data)

        await update.message.reply_text(f"Top-up berhasil! Saldo Anda sekarang: Rp {user_data[user_id]['saldo']}")
    except (IndexError, ValueError):
        await update.message.reply_text("Harap masukkan jumlah top-up yang valid. Contoh: /topup 10000")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("GMAIL", callback_data='gmail')],
        [InlineKeyboardButton("YT Prem", callback_data='ytprem')],
        [InlineKeyboardButton("CapCut", callback_data='capcut')],
        [InlineKeyboardButton("Viu", callback_data='viu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Silahkan order:\n\n"
        "┏━━━━━━━━━༻❁༺━━━━━━━━┓\n"
        "    📱 Gmail\n" 
        "    🎬 YT Prem\n" 
        "    🎥 CapCut\n" 
        "    📺 Viu\n" 
        "┗━━━━━━━━━༻❁༺━━━━━━━━┛\n"
        "Pilih salah satu opsi di bawah ini:",
        reply_markup=reply_markup
    )

async def submenu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'gmail':
        message = "Anda akan melakukan order untuk **GMAIL**. Apakah Anda ingin melanjutkan?"
    elif query.data == 'ytprem':
        message = "Anda akan melakukan order untuk **YT Premium**. Apakah Anda ingin melanjutkan?"
    elif query.data == 'capcut':
        message = "Anda akan melakukan order untuk **CapCut**. Apakah Anda ingin melanjutkan?"
    elif query.data == 'viu':
        message = "Anda akan melakukan order untuk **Viu**. Apakah Anda ingin melanjutkan?"

    keyboard = [
        [InlineKeyboardButton("LANJUT BELI", callback_data=f'continue_{query.data}')],
        [InlineKeyboardButton("KEMBALI", callback_data=f'back_{query.data}')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        f"{message}\n\n"
        "----------------------------------\n"
        "Pilih salah satu opsi di bawah ini:",
        reply_markup=reply_markup
    )

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.edit_text(
        "Silahkan order:\n\n"
        "┏━━━━━━━━━༻❁༺━━━━━━━━━┓\n"
        "    📱 Gmail\n" 
        "    🎬 YT Prem\n" 
        "    🎥 CapCut\n" 
        "    📺 Viu\n" 
        "┗━━━━━━━━━༻❁༺━━━━━━━━━┛\n"
        "Pilih salah satu opsi di bawah ini:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("GMAIL", callback_data='gmail')],
            [InlineKeyboardButton("YT Prem", callback_data='ytprem')],
            [InlineKeyboardButton("CapCut", callback_data='capcut')],
            [InlineKeyboardButton("Viu", callback_data='viu')]
        ])
    )

async def continue_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_type = query.data.split('_')[1]

    try:
        with open('akun.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        await query.message.edit_text("Data akun premium tidak ditemukan.")
        return

    user_id = str(query.from_user.id)
    user_data = get_user_data()

    saldo = user_data.get(user_id, {}).get("saldo", 0)
    account = data.get(order_type, [])

    if not account:
        await query.message.edit_text("Maaf, akun premium yang Anda pilih tidak tersedia.")
        return

    harga_akun = 5000  # Harga akun set menjadi 5000

    if saldo >= harga_akun:
        # Menampilkan pilihan metode pembayaran
        keyboard = [
            [InlineKeyboardButton("SALDO BOT", callback_data=f"saldo_{order_type}")],
            [InlineKeyboardButton("QRIS", callback_data=f"qris_{order_type}")],
            [InlineKeyboardButton("BATAL", callback_data=f"back_{order_type}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(
            f"Akun {order_type.capitalize()} siap dipesan. Silahkan pilih metode pembayaran:",
            reply_markup=reply_markup
        )
    else:
        await query.message.edit_text(f"Saldo Anda tidak cukup untuk melakukan pemesanan. Harga akun: Rp {harga_akun}")

async def saldo_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    user_data = get_user_data()

    saldo = user_data.get(user_id, {}).get("saldo", 0)
    account_type = query.data.split('_')[1]

    # Pastikan saldo cukup untuk mengirimkan akun
    if saldo >= 5000:  # Sesuai harga akun 5000
        # Ambil data akun
        try:
            with open('akun.json', 'r') as f:
                data = json.load(f)
            account = data.get(account_type, [])

            if account:
                account_info = account.pop(0)
                with open('akun.json', 'w') as f:
                    json.dump(data, f, indent=4)

                user_data[user_id]["saldo"] -= 5000
                save_user_data(user_data)

                file_content = f"Username: {account_info['username']}\nPassword: {account_info['password']}"
                file_name = f"{account_type}_account.txt"

                with open(file_name, 'w') as file:
                    file.write(file_content)

                with open(file_name, 'rb') as file:
                    await query.message.reply_document(file, caption=f"Akun {account_type.capitalize()} berhasil dipesan!")

                os.remove(file_name)
                await query.message.edit_text(f"Pembayaran dengan SALDO BOT berhasil! Pesanan {account_type.capitalize()} telah dikirim.")
            else:
                await query.message.edit_text(f"Maaf, akun {account_type} tidak tersedia.")
        except Exception as e:
            await query.message.edit_text(f"Terjadi kesalahan: {e}")
    else:
        await query.message.edit_text("Saldo bot tidak cukup untuk melakukan transaksi.")

async def qris(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    qris_link = "awokwokao 🗿"
    await query.message.edit_text(f"Dalam proses pengembangan: {qris_link}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("saldo", saldo))
    app.add_handler(CommandHandler("topup", topup))
    app.add_handler(CallbackQueryHandler(submenu, pattern='^(gmail|ytprem|capcut|viu)$'))
    app.add_handler(CallbackQueryHandler(back, pattern='^back_'))
    app.add_handler(CallbackQueryHandler(continue_order, pattern='^continue_'))
    app.add_handler(CallbackQueryHandler(saldo_bot, pattern='^saldo_'))
    app.add_handler(CallbackQueryHandler(qris, pattern='^qris_'))

    print("Bot jalan... 🚀")
    app.run_polling()

if __name__ == '__main__':
    main()
