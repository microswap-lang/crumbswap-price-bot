import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = 'YOUR_BOT_TOKEN_HERE'

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = 'https://api.dexscreener.com/latest/dex/pairs/bsc/0x68214c06d83a78274bb30598bf4aead0f8995657'
    response = requests.get(url)
    data = response.json()
    price = data['pair']['priceUsd']
    await update.message.reply_text(f"Current CRUMB price: ${price}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("price", price))
app.run_polling()
