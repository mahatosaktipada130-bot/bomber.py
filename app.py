import os
import base64
import asyncio
from urllib.parse import parse_qs, urlparse
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Flask Web Server (Render Port Binding ke liye)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Link Decoder Function
def decode_custom_url(url_text: str) -> str:
    parsed_url = urlparse(url_text)
    query_params = parse_qs(parsed_url.query)
    
    if 's' in query_params:
        encoded_str = query_params['s'][0]
    else:
        encoded_str = url_text.strip()

    try:
        missing_padding = len(encoded_str) % 4
        if missing_padding:
            encoded_str += '=' * (4 - missing_padding)
        
        decoded_bytes = base64.b64decode(encoded_str)
        decoded_str = decoded_bytes.decode('utf-8')
        
        urls = decoded_str.split('|||')
        return "\n".join([f"• {u}" for u in set(urls)])
    except Exception:
        return None

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hii! Mujhe link bhejie, main decode kar doonga.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    decoded_result = decode_custom_url(text)
    
    if decoded_result:
        reply_text = f"✅ **Decoded Result:**\n\n{decoded_result}"
    else:
        reply_text = "❌ Yeh valid Base64 link nahi hai."
        
    await update.message.reply_text(reply_text, parse_mode="Markdown")

def main():
    # Render Environment Variables se Token uthayega
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN Environment Variable nahi mila!")
        return

    # Background me Flask server start karna
    Thread(target=run_flask, daemon=True).start()

    # Telegram Bot Start karna
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot started successfully...")
    application.run_polling()

if __name__ == '__main__':
    main()
