import os
import uuid
import time
from threading import Thread

import telebot
from telebot import types
from flask import Flask, abort, render_template_string
import psycopg2
from psycopg2 import sql
import psycopg2.extras

# ------------------ الإعدادات الأساسية ------------------
TOKEN = "7923040242:AAHH55scaoC1Z9MkRmAV3nph7m8SN8mJCUU"
ADMIN_ID = "5087712149"
BOT_URL_BASE = "https://kingo999.onrender.com"  # تأكد من صحة الرابط

# رابط PostgreSQL المباشر (يمكنك وضعه مباشرة أو عبر متغير بيئة)
# الأفضل استخدام متغير بيئة: DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASE_URL = "postgresql://king_6bx4_user:RhAgl1RanixDRSOtsp9VxiKlRaJrugYh@dpg-d67hvp7gi27c739t43b0-a/king_6bx4"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ------------------ دوال قاعدة البيانات ------------------
def get_db():
    """إنشاء اتصال بقاعدة البيانات مع إعادة المحاولة"""
    retries = 3
    for i in range(retries):
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            return conn
        except Exception as e:
            print(f"⚠️ محاولة اتصال {i+1} فشلت: {e}")
            time.sleep(2)
    raise Exception("❌ فشل الاتصال بقاعدة البيانات بعد 3 محاولات")

def init_db():
    """إنشاء الجدول إذا لم يكن موجوداً"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS uploaded_files (
            file_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            created_at REAL,
            original_name TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()
    print("✅ تم التأكد من وجود جدول uploaded_files")

def save_file_to_db(file_id, name, content, original_name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO uploaded_files (file_id, name, content, active, created_at, original_name) VALUES (%s, %s, %s, %s, %s, %s)",
        (file_id, name, content, 1, time.time(), original_name)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_all_files():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT file_id, name, active, created_at, original_name FROM uploaded_files ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_file_by_id(file_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, content, active FROM uploaded_files WHERE file_id = %s", (file_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def update_file_active(file_id, active):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE uploaded_files SET active = %s WHERE file_id = %s", (1 if active else 0, file_id))
    conn.commit()
    cur.close()
    conn.close()

def delete_file_from_db(file_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM uploaded_files WHERE file_id = %s", (file_id,))
    conn.commit()
    cur.close()
    conn.close()

# تهيئة قاعدة البيانات عند بدء التشغيل
init_db()

# ------------------ دوال المساعدة ------------------
def is_admin(user_id):
    return str(user_id) == ADMIN_ID

# ------------------ البوت (polling) ------------------
@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id
    if not is_admin(uid):
        bot.send_message(uid, "⛔ أنت غير مصرح باستخدام هذا البوت.")
        return

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    upload_btn = types.InlineKeyboardButton("📤 رفع ملف HTML جديد", callback_data="upload_file")
    list_btn = types.InlineKeyboardButton("📋 قائمة الملفات المرفوعة", callback_data="list_files")
    keyboard.add(upload_btn, list_btn)

    bot.send_message(
        uid,
        "🛠️ **لوحة تحكم الأدمن**\n\nاختر الإجراء المناسب:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.from_user.id
    if not is_admin(uid):
        bot.answer_callback_query(call.id, "⛔ غير مصرح!")
        return

    if call.data == "upload_file":
        request_upload(call)
    elif call.data == "list_files":
        list_files(call)
    elif call.data.startswith("file_"):
        file_control(call, call.data[5:])
    elif call.data.startswith("run_"):
        set_file_active(call, call.data[4:], True)
    elif call.data.startswith("stop_"):
        set_file_active(call, call.data[5:], False)
    elif call.data.startswith("delete_"):
        delete_file(call, call.data[7:])
    elif call.data == "back_to_panel":
        start(call.message)

def request_upload(call):
    msg = bot.send_message(
        call.message.chat.id,
        "📎 **أرسل ملف HTML الآن**\n(يجب أن يكون بامتداد .html)"
    )
    bot.register_next_step_handler(msg, receive_file)

def receive_file(msg):
    uid = msg.from_user.id
    if not is_admin(uid):
        return

    if msg.content_type != 'document':
        bot.send_message(uid, "⚠️ يرجى إرسال ملف وليس نصاً.")
        return

    file_name = msg.document.file_name
    if not file_name.lower().endswith('.html'):
        bot.send_message(uid, "⚠️ الملف يجب أن يكون بامتداد .html فقط.")
        return

    try:
        file_info = bot.get_file(msg.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        html_content = downloaded.decode('utf-8')
    except Exception as e:
        bot.send_message(uid, f"❌ فشل تحميل الملف: {e}")
        return

    bot.send_message(uid, "✅ تم الاستلام. أرسل **اسم** للملف (مثلاً: صفحتي الشخصية):")
    bot.register_next_step_handler(msg, save_file_with_name, html_content, file_name)

def save_file_with_name(msg, html_content, original_name):
    uid = msg.from_user.id
    if not is_admin(uid):
        return

    custom_name = msg.text.strip()
    if not custom_name:
        custom_name = original_name

    file_id = str(uuid.uuid4())[:1]
    save_file_to_db(file_id, custom_name, html_content, original_name)

    file_url = f"{BOT_URL_BASE}/{file_id}/"
    bot.send_message(
        uid,
        f"✅ **تم رفع الملف بنجاح!**\n\n"
        f"📌 الاسم: {custom_name}\n"
        f"🔗 الرابط: {file_url}\n"
        f"🆔 المعرف: `{file_id}`\n"
        f"📊 الحالة: ✅ مفعل\n\n"
        "يمكنك إدارة هذا الملف من قائمة الملفات."
    )

def list_files(call):
    files = get_all_files()
    if not files:
        keyboard = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_panel")
        keyboard.add(back_btn)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="📭 لا توجد أي ملفات مرفوعة.",
            reply_markup=keyboard
        )
        return

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for file_id, name, active, created_at, orig_name in files:
        status = "✅" if active else "❌"
        btn_text = f"{status} {name[:30]}"
        keyboard.add(types.InlineKeyboardButton(btn_text, callback_data=f"file_{file_id}"))

    back_btn = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_panel")
    keyboard.add(back_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="📋 **الملفات المرفوعة:**\n✅ مفعل | ❌ متوقف",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

def file_control(call, file_id):
    file_data = get_file_by_id(file_id)
    if not file_data:
        bot.answer_callback_query(call.id, "⚠️ الملف غير موجود!")
        return

    name, content, active = file_data
    file_url = f"{BOT_URL_BASE}/{file_id}/"
    status_text = "✅ **نشط**" if active else "❌ **متوقف**"

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    run_btn = types.InlineKeyboardButton("▶️ تشغيل", callback_data=f"run_{file_id}")
    stop_btn = types.InlineKeyboardButton("⏹️ إيقاف", callback_data=f"stop_{file_id}")
    delete_btn = types.InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_{file_id}")
    preview_btn = types.InlineKeyboardButton("👁️ معاينة", url=file_url)
    back_btn = types.InlineKeyboardButton("🔙 رجوع", callback_data="list_files")

    keyboard.add(run_btn, stop_btn)
    keyboard.add(delete_btn, preview_btn)
    keyboard.add(back_btn)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"📁 **الملف:** {name}\n🆔 المعرف: `{file_id}`\n🔗 الرابط: {file_url}\n📊 الحالة: {status_text}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

def set_file_active(call, file_id, active):
    if get_file_by_id(file_id):
        update_file_active(file_id, active)
        bot.answer_callback_query(call.id, "✅ تم التفعيل" if active else "⏹️ تم الإيقاف")
        file_control(call, file_id)
    else:
        bot.answer_callback_query(call.id, "⚠️ الملف غير موجود")

def delete_file(call, file_id):
    if get_file_by_id(file_id):
        delete_file_from_db(file_id)
        bot.answer_callback_query(call.id, "🗑️ تم حذف الملف")
        list_files(call)
    else:
        bot.answer_callback_query(call.id, "⚠️ الملف غير موجود")

# ------------------ مسارات Flask ------------------
@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html dir="rtl">
    <head><meta charset="UTF-8"><title>بوت رفع الملفات</title>
    <style>
        body{background:#0a0a1a;color:white;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;}
        .card{background:#1e1e3f;padding:40px;border-radius:20px;text-align:center;}
    </style>
    </head>
    <body>
        <div class="card">
            <h1>📁 بوت رفع ملفات HTML</h1>
            <p>الملفات مخزنة بشكل دائم في قاعدة بيانات PostgreSQL.</p>
        </div>
    </body>
    </html>
    """)

@app.route("/f/<file_id>")
def serve_file(file_id):
    file_data = get_file_by_id(file_id)
    if not file_data:
        abort(404, description="الملف غير موجود")

    name, content, active = file_data
    if not active:
        return render_template_string("""
        <!DOCTYPE html>
        <html dir="rtl">
        <head><meta charset="UTF-8"><title>الملف متوقف</title>
        <style>body{background:#1e1e2f;color:#ccc;display:flex;justify-content:center;align-items:center;height:100vh;}</style>
        </head>
        <body>
            <div style="text-align:center;">
                <h1>⏹️ هذا الملف متوقف حالياً</h1>
                <p>تم إيقاف الملف من قبل الإدارة.</p>
            </div>
        </body>
        </html>
        """)
    return content

# ------------------ تشغيل البوت (polling) والخادم ------------------
def run_bot():
    while True:
        try:
            print("✅ بدء تشغيل polling...")
            bot.infinity_polling()
        except Exception as e:
            print(f"⚠️ خطأ في polling: {e}")
            time.sleep(5)

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_bot).start()
    print("✅ البوت والخادم يعملان مع PostgreSQL مباشرة")
    run_flask()
