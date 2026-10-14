import os
import json
import random
import string
import telebot
from flask import Flask, send_file
from threading import Thread

# ================== الإعدادات الثابتة ==================
BOT_TOKEN = "7923040242:AAHH55scaoC1Z9MkRmAV3nph7m8SN8mJCUU"

# ⚠️ بعد الحصول على الدومين من Render، استبدل هذا الرابط
BASE_URL = "https://kingo999.onrender.com"

SERVER_HOST = "0.0.0.0"
# Render يفرض منفذاً معيناً عبر PORT، والباقي يُستخدم محلياً فقط
SERVER_PORT = int(os.environ.get("PORT", 12706))

UPLOAD_FOLDER = "html_files"
LINKS_FILE = "links.json"

# الرموز المسموحة: حرف أو رقم واحد (a-z و 0-9)
CODE_CHARS = string.ascii_lowercase + string.digits
CODE_SET = set(CODE_CHARS)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================== البوت ==================
bot = telebot.TeleBot(BOT_TOKEN)

# ================== تخزين الروابط ==================
def load_links():
    if os.path.exists(LINKS_FILE):
        try:
            with open(LINKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_links():
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=2)

links = load_links()  # مثال: { "a": "a_index.html", "7": "7_page.html" }

def generate_code():
    """يرجع حرفاً أو رقماً واحداً غير مستخدم"""
    free = [c for c in CODE_CHARS if c not in links]
    if free:
        return random.choice(free)
    # في حال انتهت كل الرموز المفردة ننتقل إلى رمزين
    while True:
        code = "".join(random.choice(CODE_CHARS) for _ in range(2))
        if code not in links:
            return code

# ================== سيرفر Flask ==================
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot is running", 200

@app.route("/<code>/")
@app.route("/<code>")
def serve_by_code(code):
    """الرابط المختصر: /a/"""
    filename = links.get(code)
    if not filename:
        return "❌ الرابط غير موجود", 404
    path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(path):
        return "❌ الملف غير موجود", 404
    return send_file(path)

@app.route("/<code>/<path:filename>")
def serve_by_code_name(code, filename):
    """الرابط بالاسم: /a/index.html"""
    stored = links.get(code)
    if not stored:
        return "❌ الرابط غير موجود", 404
    path = os.path.join(UPLOAD_FOLDER, stored)
    if not os.path.exists(path):
        return "❌ الملف غير موجود", 404
    return send_file(path)

# ================== معالجات البوت ==================
@bot.message_handler(commands=["start"])
def cmd_start(message):
    bot.reply_to(
        message,
        "👋 أرسل ملف HTML:\n"
        "• مع كابشن حرف/رقم واحد (مثال: a أو 5) لاختيار رابطك.\n"
        "• أو بدون كابشن ليختار البوت الرمز تلقائياً."
    )

@bot.message_handler(content_types=["document"])
def handle_html_file(message):
    try:
        doc = message.document
        name = doc.file_name or ""

        if not name.lower().endswith(".html"):
            bot.reply_to(message, "❌ يرجى إرسال ملف HTML فقط")
            return

        # ---- تحديد الرمز ----
        code = None
        if message.caption:
            c = message.caption.strip()
            if len(c) == 1 and c in CODE_SET:
                if c in links:
                    bot.reply_to(message, f"⚠️ الرمز /{c}/ مستخدم مسبقاً، اختر رمزاً آخر.")
                    return
                code = c
            else:
                bot.reply_to(message, "⚠️ الكابشن يجب أن يكون حرفاً واحداً أو رقماً واحداً فقط (a-z أو 0-9).")
                return

        if code is None:
            code = generate_code()

        # ---- تنزيل الملف ----
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)

        stored_name = f"{code}_{name}"
        with open(os.path.join(UPLOAD_FOLDER, stored_name), "wb") as f:
            f.write(downloaded)

        links[code] = stored_name
        save_links()

        short_url = f"{BASE_URL}/{code}/"
        full_url = f"{BASE_URL}/{code}/{name}"

        bot.reply_to(
            message,
            f"✅ تم رفع الملف بنجاح\n"
            f"🔗 الرابط المختصر:\n{short_url}\n\n"
            f"🔗 الرابط بالاسم:\n{full_url}"
        )

    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {e}")

# ================== تشغيل البوت في خيط منفصل ==================
def run_bot():
    print("Bot is running...")
    bot.polling(none_stop=True)

# مهم: نُشغّل البوت عند استيراد الملف لأن gunicorn لا يستدعي __main__
bot_thread = Thread(target=run_bot)
bot_thread.daemon = True
bot_thread.start()

# ================== تشغيل محلي ==================
if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True)
