import os
import re
import json
import asyncio
import aiohttp
import base64
import urllib.parse
from urllib.parse import parse_qs, urlparse
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Flask Web Server
app = Flask(__name__)

@app.route('/')
def home():
    return "Ultra Speed Firebase Monitor is Active!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Parallel Limits
SEMAPHORE = asyncio.Semaphore(100)

# Advance Deep Decoder (URL Decode + Multi-round Base64 + JSON Extraction)
def smart_base64_decode(text: str) -> str:
    current = text.strip()
    
    # 1. URL Parameter extraction
    if "http" in current and "?" in current:
        parsed_url = urlparse(current)
        query_params = parse_qs(parsed_url.query)
        for k, v in query_params.items():
            if v and len(v[0]) > 10:
                current = v[0]
                break

    # 2. URL Unquote (%2F, %2B, %3D conversion)
    current = urllib.parse.unquote(current)

    # 3. Recursive Base64 Decoding
    for _ in range(4):
        try:
            # Fix Base64 Padding
            missing_padding = len(current) % 4
            if missing_padding:
                current += '=' * (4 - missing_padding)
            
            # Replace spaces with + (URL encoding fix)
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

# Ultra-Fast Online Device Checking Function
async def check_online_fast(session, firebase_url: str) -> dict:
    clean_url = firebase_url.strip()
    if not clean_url.startswith("http"):
        clean_url = "https://" + clean_url
    if not clean_url.endswith(".json"):
        clean_url = clean_url.rstrip("/") + "/.json"

    timeout = aiohttp.ClientTimeout(total=1.5, connect=0.8)

    async with SEMAPHORE:
        try:
            async with session.get(clean_url, timeout=timeout) as response:
                if response.status != 200:
                    return None
                
                text_data = await response.text()
                if not text_data or text_data == "null" or len(text_data) < 10:
                    return None

                # Fast regex scan for status
                if not re.search(r'(?i)"(status|state|presence|isonline|online)"', text_data):
                    return None

                data = json.loads(text_data)
                online_count = 0

                nodes = [data]
                while nodes:
                    curr = nodes.pop()
                    if isinstance(curr, dict):
                        for k, v in curr.items():
                            if k.lower() in ["status", "state", "presence", "isonline", "online"]:
                                val_str = str(v).lower()
                                if val_str in ["online", "true", "1", "active"]:
                                    online_count += 1
                                break
                        nodes.extend(curr.values())
                    elif isinstance(curr, list):
                        nodes.extend(curr)

                if online_count > 0:
                    return {"url": firebase_url, "online": online_count}
                return None

        except Exception:
            return None

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ **Advanced Firebase Link Extractor**\n\n"
        "Kisi bhi panel ka heavy encoded link bhejien, bot auto-decode karke sirf **ONLINE** Firebase links dega!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Advanced Decoding
    decoded_content = smart_base64_decode(text)
    
    # Extract Firebase URLs with Regular Expressions
    firebase_pattern = r'https://[a-zA-Z0-9\.-]+?\.(?:firebaseio\.com|firebasedatabase\.app)'
    found_urls = re.findall(firebase_pattern, decoded_content) + re.findall(firebase_pattern, text)
    unique_urls = list(dict.fromkeys(found_urls))

    if not unique_urls:
        await update.message.reply_text("❌ Koi valid Firebase URL nahi mila.")
        return

    status_msg = await update.message.reply_text(f"⚡ **Found {len(unique_urls)} Firebase link(s)! Checking Online Status...**")

    connector = aiohttp.TCPConnector(limit=200, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [check_online_fast(session, url) for url in unique_urls]
        results = await asyncio.gather(*tasks)

    online_results = [res for res in results if res is not None]

    if not online_results:
        await status_msg.edit_text("❌ **Kisi bhi Firebase me Online Device nahi mila.**")
        return

    response_lines = [f"🟢 **ONLINE FIREBASE LINKS FOUND ({len(online_results)}/{len(unique_urls)}):**\n"]
    
    for item in online_results:
        response_lines.append(f"`{item['url']}` (Online: {item['online']})")

    final_report = "\n".join(response_lines)

    if len(final_report) > 4000:
        await status_msg.edit_text("✅ **Online Firebase Links Found:**")
        chunks = [final_report[i:i+3900] for i in range(0, len(final_report), 3900)]
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        await status_msg.edit_text(final_report, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN Environment Variable nahi mila!")
        return

    Thread(target=run_flask, daemon=True).start()

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Turbo Fast Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()

