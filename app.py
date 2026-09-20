import os
import base64
import re
import json
from urllib.parse import parse_qs, urlparse
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Flask Web Server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Only Firebase URLs Extract karne wala function
def decode_custom_url(url_text: str) -> str:
    parsed_url = urlparse(url_text)
    query_params = parse_qs(parsed_url.query)
    
    if 's' in query_params:
        encoded_str = query_params['s'][0]
    else:
        encoded_str = url_text.strip()

    try:
        # Base64 padding fix
        missing_padding = len(encoded_str) % 4
        if missing_padding:
            encoded_str += '=' * (4 - missing_padding)
        
        # Decode base64
        decoded_bytes = base64.b64decode(encoded_str)
        decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
        
        # Regex se sirf Firebase URLs extract karna (.firebaseio.com aur .firebasedatabase.app dono)
        firebase_pattern = r'https://[a-zA-Z0-9\.-]+?\.(?:firebaseio\.com|firebasedatabase\.app)'
        firebase_links = re.findall(firebase_pattern, decoded_str)
        
        # Unique links preserve karna
        unique_links = list(dict.fromkeys(firebase_links))
        
        if not unique_links:
            return None
            
        return "\n".join([f"• {link}" for link in unique_links])
        
    except Exception:
        return None

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hii! Mujhe link ya Base64 text bhejo, main usme se sirf Firebase URLs nikal ke de doonga.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    decoded_result = decode_custom_url(text)
    
    if decoded_result:
        reply_text = f"✅ **Decoded Firebase Links:**\n\n{decoded_result}"
    else:
        reply_text = "❌ Koi valid Firebase URL nahi mila."
        
    await update.message.reply_text(reply_text, disable_web_page_preview=True)

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN Environment Variable nahi mila!")
        return

    Thread(target=run_flask, daemon=True).start()

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot started successfully...")
    application.run_polling()

if __name__ == '__main__':
    main()
