import os
import re
import base64
import urllib.parse
from urllib.parse import parse_qs, urlparse
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Flask Web Server (Render/Keep-Alive)
app = Flask(__name__)

@app.route('/')
def home():
    return "Auto-Decoder Bot Active!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Automatic Multi-Round Deep Decoder
def auto_decode_text(text: str) -> str:
    current = text.strip()
    
    # 1. Extract query parameter if it's a URL
    if "http" in current and "?" in current:
        parsed_url = urlparse(current)
        query_params = parse_qs(parsed_url.query)
        for k, v in query_params.items():
            if v and len(v[0]) > 10:
                current = v[0]
                break

    # 2. URL Unquote
    current = urllib.parse.unquote(current)

    # 3. Multi-round Base64 Decoding
    for _ in range(5):
        try:
            missing_padding = len(current) % 4
            if missing_padding:
                current += '=' * (4 - missing_padding)
            
            clean_b64 = current.replace(' ', '+')
            decoded_bytes = base64.b64decode(clean_b64)
            decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
            
            if decoded_str and decoded_str != current:
                current = urllib.parse.unquote(decoded_str)
            else:
                break
        except Exception:
            break

    return current

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send link to decode.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Automatic Deep Decode
    decoded_content = auto_decode_text(text)

    # Extract all HTTP/HTTPS links from decoded content & original text
    link_pattern = r'https?://[^\s<>"]+'
    found_links = re.findall(link_pattern, decoded_content) + re.findall(link_pattern, text)
    unique_links = list(dict.fromkeys(found_links))

    if not unique_links:
        await update.message.reply_text("❌ No links found.")
        return

    final_report = "\n".join(unique_links)

    if len(final_report) > 4000:
        chunks = [final_report[i:i+3900] for i in range(0, len(final_report), 3900)]
        for chunk in chunks:
            await update.message.reply_text(chunk, disable_web_page_preview=True)
    else:
        await update.message.reply_text(final_report, disable_web_page_preview=True)

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN Environment Variable missing!")
        return

    Thread(target=run_flask, daemon=True).start()

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot running...")
    application.run_polling()

if __name__ == '__main__':
    main()
