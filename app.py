#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
آوا (AVA) — شبکه اجتماعی
توسعه‌دهنده: امیرعباس شهریاری
رفع BrokenPipe + کانال خصوصی/عمومی + قوانین + کپچا + بات کامل
"""

import os, re, html, time, uuid, random, hashlib, sqlite3, mimetypes, threading, traceback, secrets, string
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, parse_qs, unquote
from http.server import HTTPServer, BaseHTTPRequestHandler

APP_NAME, APP_NAME_EN = "آوا", "AVA"
APP_TAGLINE = "جایی که صداها به هم می‌رسن"
HOST, PORT = "0.0.0.0", 8080
DB_PATH, UPLOAD_DIR = "ava.db", "uploads"
SECRET = "ava-secret-amirabbas-shahriari-2024"
MAX_UPLOAD_MB = 12
DEVELOPER = "امیرعباس شهریاری"
MAX_ACCOUNTS_PER_DEVICE = 3

LOGO_SVG = '''<svg width="34" height="34" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#ff6b35"/><stop offset="50%" stop-color="#f7c948"/><stop offset="100%" stop-color="#00d4aa"/>
  </linearGradient></defs>
  <rect width="64" height="64" rx="16" fill="url(#g)"/>
  <path d="M18 44 L32 16 L46 44" stroke="#0a0a0a" stroke-width="5.5" stroke-linecap="round" fill="none"/>
  <path d="M24 36 H40" stroke="#0a0a0a" stroke-width="5.5" stroke-linecap="round"/>
  <circle cx="48" cy="16" r="4.5" fill="#0a0a0a"/>
</svg>'''

# تیک آبی شیک‌تر
VERIFIED_SVG = '''<svg width="16" height="16" viewBox="0 0 22 22" style="vertical-align:-3px;margin-right:2px"><circle cx="11" cy="11" r="11" fill="#1d9bf0"/><path d="M6.5 11.2l2.8 2.8 6.2-6.5" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'''

ICONS = {
    "home": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "search": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "plus": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
    "chat": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "user": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "bell": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
    "settings": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "heart": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
    "heart_fill": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="#ed4956" stroke="#ed4956" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
    "comment": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "bookmark": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>',
    "bookmark_fill": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>',
    "explore": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>',
    "eye": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
    "sun": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/></svg>',
    "moon": '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
    "admin": '<svg width="14" height="14" viewBox="0 0 24 24" fill="#f59e0b"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>',
    "bot": '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#00a884" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/></svg>',
}

WELCOME_MSGS = ["سلام! به آوا خوش اومدی 🔥", "آوا یعنی صدا. صدای تو هم اینجاست.", "خوش اومدی. پست بذار و گپ بزن."]

TERMS_HTML = """
<div class="terms-box">
<h2>قوانین و شرایط استفاده از آوا</h2>
<p>با ساخت حساب یا ورود به <strong>آوا (AVA)</strong> شما موافقت خود را با قوانین زیر اعلام می‌کنید. لطفاً با دقت بخوانید.</p>
<h3>۱. تعریف سرویس</h3>
<p>آوا یک بستر ارتباط اجتماعی است که امکان انتشار پست، استوری، گفتگو، کانال و گروه را فراهم می‌کند. سرویس توسط تیم توسعه به مدیریت امیرعباس شهریاری ارائه می‌شود.</p>
<h3>۲. ثبت‌نام و حساب کاربری</h3>
<ul>
<li>هر فرد حداکثر می‌تواند <strong>۳ حساب</strong> بسازد.</li>
<li>نام کاربری باید حداقل ۵ حرف انگلیسی (حروف، عدد و _) باشد.</li>
<li>مسئولیت حفظ رمز عبور با خود کاربر است.</li>
<li>حساب‌های جعلی، ربات‌های غیرمجاز و هویت جعلی ممنوع است.</li>
</ul>
<h3>۳. محتوای ممنوع</h3>
<ul>
<li>محتوای خشونت‌آمیز، پورنوگرافی غیرقانونی، نفرت‌پراکنی و تهدید</li>
<li>اسپم، کلاهبرداری، فیشینگ و تبلیغات گمراه‌کننده</li>
<li>نقض حق نشر و مالکیت معنوی دیگران</li>
<li>اطلاعات شخصی دیگران بدون رضایت</li>
</ul>
<h3>۴. کانال و گروه</h3>
<ul>
<li>کانال/گروه <strong>عمومی</strong> در جستجو و پیشنهادها نمایش داده می‌شود.</li>
<li>کانال/گروه <strong>خصوصی</strong> فقط با لینک دعوت قابل دسترسی است و در جستجو نمی‌آید.</li>
<li>مالک مسئول محتوای منتشرشده در کانال/گروه خود است.</li>
</ul>
<h3>۵. ربات‌ها</h3>
<ul>
<li>ربات‌ها فقط از طریق بات‌پدر و با رعایت مستندات ساخته می‌شوند.</li>
<li>سوءاستفاده از توکن ربات یا ارسال اسپم منجر به مسدودسازی می‌شود.</li>
</ul>
<h3>۶. حریم خصوصی</h3>
<p>ما اطلاعات ضروری حساب را ذخیره می‌کنیم. پیام‌های خصوصی رمزنگاری سرتاسری کامل در این نسخه ندارند؛ از ارسال اطلاعات فوق‌حساس خودداری کنید.</p>
<h3>۷. مسدودسازی و تعلیق</h3>
<p>مدیریت حق دارد در صورت نقض قوانین، حساب را بدون اطلاع قبلی مسدود یا حذف کند.</p>
<h3>۸. تغییرات قوانین</h3>
<p>قوانین ممکن است به‌روزرسانی شوند. ادامه استفاده به معنای پذیرش نسخه جدید است.</p>
<p style="margin-top:16px;color:var(--muted);font-size:12px">آخرین به‌روزرسانی: ۱۴۰۴ · آوا (AVA) · {dev}</p>
</div>
""".replace("{dev}", DEVELOPER)

def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def hpw(pw):
    return hashlib.sha256((str(pw) + SECRET).encode()).hexdigest()

def make_token(uid):
    return hashlib.sha256(f"{uid}:{int(time.time())}:{SECRET}".encode()).hexdigest()[:48] + f".{uid}"

def read_token(tok):
    try:
        if "." not in tok: return None
        return int(tok.rsplit(".", 1)[1])
    except: return None

def esc(s):
    return html.escape(str(s or ""))

def clean_username(u, min_len=5):
    u = re.sub(r"[^a-zA-Z0-9_]", "", (u or "").lower().strip())
    return u[:24] if len(u) >= min_len else ""

def ic(name, size=24):
    return ICONS.get(name, "").format(s=size)

def g(row, key, default=None):
    if row is None: return default
    try:
        if hasattr(row, "keys"):
            return row[key] if key in row.keys() else default
        return row.get(key, default) if hasattr(row, "get") else default
    except Exception:
        return default

def format_text(text):
    if not text: return ""
    t = html.escape(str(text))
    t = re.sub(r'@([a-zA-Z0-9_]+)', r'<a href="/u/\1" style="color:var(--accent);font-weight:500">@\1</a>', t)
    t = re.sub(r'#([^\s#]+)', r'<a href="/search?q=%23\1" style="color:var(--accent)">#\1</a>', t)
    return t.replace("\n", "<br>")

def time_ago(ts):
    try:
        dt = datetime.strptime(str(ts), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        diff = (datetime.now(timezone.utc) - dt).total_seconds()
        if diff < 60: return "همین الان"
        if diff < 3600: return f"{int(diff//60)} دقیقه"
        if diff < 86400: return f"{int(diff//3600)} ساعت"
        if diff < 604800: return f"{int(diff//86400)} روز"
        return str(ts)[:10]
    except: return str(ts or "")[:10]

def avatar_html(user, size=40):
    if not user:
        return f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:#dbdbdb"></div>'
    av = g(user, "avatar")
    if av and str(av).strip():
        return f'<img src="/uploads/{esc(av)}" alt="" style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;display:block">'
    name = g(user, "display_name") or g(user, "username") or "?"
    initial = str(name)[0].upper()
    colors = ["#e1306c", "#f77737", "#fcaf45", "#405de6", "#5851db", "#833ab4", "#c13584"]
    color = colors[abs(hash(str(g(user, "username", "")))) % len(colors)]
    return f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:{color};display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:{max(11,size//2.5)}px">{initial}</div>'

def verified_badge(user):
    return f' {VERIFIED_SVG}' if g(user, "is_verified") else ""

def admin_badge(user):
    return f' {ic("admin")}' if g(user, "is_admin") else ""

def bot_badge(user):
    if g(user, "is_bot"):
        return f' <span class="badge-bot">{ic("bot")} بات</span>'
    return ""

def gen_captcha():
    a, b = random.randint(2, 12), random.randint(2, 9)
    return f"{a}+{b}", str(a + b)

def gen_user_public_id():
    """آیدی غیررتبه‌ای برای کاربران عادی"""
    return str(random.randint(200000, 999999999))

def gen_invite():
    return secrets.token_urlsafe(10)[:14]

def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        display_name TEXT,
        password TEXT NOT NULL,
        public_id TEXT UNIQUE,
        email TEXT DEFAULT '',
        bio TEXT DEFAULT '',
        avatar TEXT DEFAULT '',
        is_admin INTEGER DEFAULT 0,
        is_verified INTEGER DEFAULT 0,
        is_blocked INTEGER DEFAULT 0,
        is_bot INTEGER DEFAULT 0,
        bot_token TEXT DEFAULT '',
        theme TEXT DEFAULT 'dark',
        device_id TEXT DEFAULT '',
        created TEXT
    );
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER, content TEXT DEFAULT '', image TEXT DEFAULT '',
        is_explore INTEGER DEFAULT 1, views INTEGER DEFAULT 0, created TEXT
    );
    CREATE TABLE IF NOT EXISTS likes (uid INTEGER, pid INTEGER, PRIMARY KEY(uid,pid));
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pid INTEGER, uid INTEGER, body TEXT, created TEXT
    );
    CREATE TABLE IF NOT EXISTS saves (uid INTEGER, pid INTEGER, PRIMARY KEY(uid,pid));
    CREATE TABLE IF NOT EXISTS follows (a INTEGER, b INTEGER, PRIMARY KEY(a,b));
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER, actor INTEGER, type TEXT, ref_id INTEGER,
        body TEXT, is_read INTEGER DEFAULT 0, created TEXT
    );
    CREATE TABLE IF NOT EXISTS stories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER, image TEXT, caption TEXT DEFAULT '',
        created TEXT, expires TEXT
    );
    CREATE TABLE IF NOT EXISTS story_views (sid INTEGER, uid INTEGER, PRIMARY KEY(sid,uid));
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE, title TEXT DEFAULT '',
        is_group INTEGER DEFAULT 0, is_channel INTEGER DEFAULT 0,
        is_private INTEGER DEFAULT 0, invite_code TEXT DEFAULT '',
        owner_id INTEGER, description TEXT DEFAULT '',
        avatar TEXT DEFAULT '', created TEXT
    );
    CREATE TABLE IF NOT EXISTS conv_members (
        cid INTEGER, uid INTEGER, role TEXT DEFAULT 'member', PRIMARY KEY(cid,uid)
    );
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cid INTEGER, sender INTEGER, body TEXT, image TEXT DEFAULT '', created TEXT
    );
    CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
    CREATE TABLE IF NOT EXISTS ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, body TEXT, link TEXT DEFAULT '',
        image TEXT DEFAULT '', is_active INTEGER DEFAULT 1, created TEXT
    );
    CREATE TABLE IF NOT EXISTS broadcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        body TEXT, image TEXT DEFAULT '', sent_by INTEGER, created TEXT
    );
    CREATE TABLE IF NOT EXISTS bots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER, bot_uid INTEGER, token TEXT UNIQUE,
        name TEXT, username TEXT, created TEXT
    );
    CREATE TABLE IF NOT EXISTS post_views (pid INTEGER, uid INTEGER, PRIMARY KEY(pid,uid));
    CREATE TABLE IF NOT EXISTS captcha_store (sid TEXT PRIMARY KEY, answer TEXT, created REAL);
    """)
    for k, v in [("explore_mode", "all"), ("welcome_enabled", "1")]:
        c.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", (k, v))

    if not c.execute("SELECT id FROM users WHERE username='HAMAVA'").fetchone():
        c.execute(
            "INSERT INTO users(username,display_name,password,public_id,is_admin,is_verified,bio,theme,created) VALUES(?,?,?,?,1,1,?,?,?)",
            ("HAMAVA", "مدیر آوا", hpw("13866831"), "10001",
             f"توسعه‌دهنده و مدیر اصلی آوا · {DEVELOPER}", "dark", now())
        )
        print(">>> ادمین: HAMAVA / 13866831")

    for uname, dname, pid, bio in [
        ("AvaBot", "بات آوا", "10002", "بات رسمی خوشامدگویی و اطلاع‌رسانی آوا"),
        ("BotFather", "بات پدر", "10003", "ساخت و مدیریت ربات‌های آوا"),
    ]:
        if not c.execute("SELECT id FROM users WHERE username=?", (uname,)).fetchone():
            c.execute(
                "INSERT INTO users(username,display_name,password,public_id,is_bot,is_verified,bio,theme,created) VALUES(?,?,?,?,1,1,?,?,?)",
                (uname, dname, hpw("bot-internal"), pid, bio, "dark", now())
            )
    c.commit()
    c.close()

def get_setting(key, default=""):
    c = db(); r = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone(); c.close()
    return r["value"] if r else default

def set_setting(key, value):
    c = db(); c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, str(value))); c.commit(); c.close()

def save_media(field):
    if not field or not isinstance(field, dict) or not field.get("filename"):
        return None
    data = field.get("data") or b""
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024: return None
    ext = os.path.splitext(field["filename"])[1].lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".webm"): return None
    name = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(UPLOAD_DIR, name), "wb") as f:
        f.write(data)
    return name

def parse_multipart(body, boundary):
    fields = {}
    for part in body.split(b"--" + boundary):
        if b"Content-Disposition" not in part: continue
        header, _, content = part.partition(b"\r\n\r\n")
        content = content.rstrip(b"\r\n--")
        m = re.search(rb'name="([^"]+)"', header)
        if not m: continue
        name = m.group(1).decode()
        fn = re.search(rb'filename="([^"]*)"', header)
        if fn and fn.group(1):
            fields[name] = {"filename": fn.group(1).decode(), "data": content}
        else:
            try: fields[name] = content.decode("utf-8", "replace")
            except: fields[name] = ""
    return fields

def ensure_saved_messages(uid):
    c = db()
    uname = f"saved_{uid}"
    conv = c.execute("SELECT id FROM conversations WHERE username=?", (uname,)).fetchone()
    if not conv:
        c.execute("INSERT INTO conversations(username,title,is_group,is_channel,owner_id,created) VALUES(?,?,0,0,?,?)",
                  (uname, "پیام‌های ذخیره شده", uid, now()))
        cid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
        c.execute("INSERT INTO conv_members(cid,uid,role) VALUES(?,?,?)", (cid, uid, "owner"))
        c.commit(); c.close(); return cid
    c.close(); return conv["id"]

def notify(uid, actor, typ, ref_id, body):
    if uid == actor: return
    c = db()
    c.execute("INSERT INTO notifications(uid,actor,type,ref_id,body,created) VALUES(?,?,?,?,?,?)",
              (uid, actor, typ, ref_id, body, now()))
    c.commit(); c.close()

def record_view(pid, uid):
    c = db()
    try:
        c.execute("INSERT OR IGNORE INTO post_views(pid,uid) VALUES(?,?)", (pid, uid))
        if c.total_changes:
            c.execute("UPDATE posts SET views = views + 1 WHERE id=?", (pid,))
        c.commit()
    except: pass
    c.close()

def store_captcha():
    q, a = gen_captcha()
    sid = secrets.token_hex(8)
    c = db()
    c.execute("INSERT OR REPLACE INTO captcha_store(sid,answer,created) VALUES(?,?,?)", (sid, a, time.time()))
    c.execute("DELETE FROM captcha_store WHERE created < ?", (time.time() - 600,))
    c.commit(); c.close()
    return sid, q

def check_captcha(sid, answer):
    c = db()
    r = c.execute("SELECT answer FROM captcha_store WHERE sid=?", (sid,)).fetchone()
    c.execute("DELETE FROM captcha_store WHERE sid=?", (sid,))
    c.commit(); c.close()
    return r and str(r["answer"]).strip() == str(answer).strip()

def start_background():
    def loop():
        time.sleep(5)
        while True:
            try:
                c = db()
                c.execute("DELETE FROM stories WHERE expires < ?", (now(),))
                c.execute("DELETE FROM captcha_store WHERE created < ?", (time.time() - 600,))
                c.commit(); c.close()
            except: pass
            time.sleep(120)
    threading.Thread(target=loop, daemon=True).start()

# ==================== Handler ====================
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def get_theme(self, me):
        if me and g(me, "theme"): return g(me, "theme")
        cookie = self.headers.get("Cookie", "")
        m = re.search(r"theme=([^;]+)", cookie)
        return m.group(1) if m and m.group(1) in ("light", "dark") else "dark"

    def get_device_id(self):
        cookie = self.headers.get("Cookie", "")
        m = re.search(r"did=([^;]+)", cookie)
        if m: return m.group(1)
        return secrets.token_hex(12)

    def get_user(self):
        cookie = self.headers.get("Cookie", "")
        m = re.search(r"token=([^;]+)", cookie)
        if not m: return None
        uid = read_token(unquote(m.group(1)))
        if not uid: return None
        c = db(); u = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone(); c.close()
        if u and g(u, "is_blocked"): return None
        return u

    def send_html(self, html_str, status=200, extra=None):
        try:
            data = html_str.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            if extra:
                for k, v in extra.items():
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass  # کلاینت قطع شده — نادیده بگیر

    def redirect(self, path, extra=None):
        try:
            self.send_response(302)
            self.send_header("Location", path)
            if extra:
                for k, v in extra.items():
                    self.send_header(k, v)
            self.end_headers()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def parse_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0: return {}, {}
        ctype = self.headers.get("Content-Type", "")
        body = self.rfile.read(length)
        if "multipart/form-data" in ctype:
            boundary = re.search(r"boundary=([^\s;]+)", ctype)
            if boundary: return parse_multipart(body, boundary.group(1).encode()), {}
            return {}, {}
        try:
            qs = parse_qs(body.decode("utf-8", "replace"))
            return {}, {k: v[0] for k, v in qs.items()}
        except: return {}, {}

    def do_GET(self):
        try:
            self.route_get()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        except Exception:
            traceback.print_exc()
            try:
                self.send_html("<div style='text-align:center;padding:60px;font-family:sans-serif'>خطا. صفحه را رفرش کنید.</div>", 500)
            except Exception:
                pass

    def do_POST(self):
        try:
            self.route_post()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        except Exception:
            traceback.print_exc()
            try:
                self.send_html("<div style='text-align:center;padding:60px;font-family:sans-serif'>خطا</div>", 500)
            except Exception:
                pass

    def serve_upload(self, filename):
        path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(path) or ".." in filename:
            try: self.send_html("Not found", 404)
            except Exception: pass
            return
        try:
            ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(os.path.getsize(path)))
            self.send_header("Cache-Control", "public, max-age=86400")
            self.end_headers()
            with open(path, "rb") as f:
                self.wfile.write(f.read())
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def route_get(self):
        u = urlparse(self.path)
        path, qs = u.path, parse_qs(u.query)
        me = self.get_user()
        theme = self.get_theme(me)

        if path.startswith("/uploads/"):
            self.serve_upload(path[9:]); return

        if path in ("/", "/home"):
            if not me: return self.redirect("/login")
            return self.send_html(page_home(me, theme))
        if path == "/explore":
            if not me: return self.redirect("/login")
            return self.send_html(page_explore(me, theme))
        if path == "/login": return self.send_html(page_login(theme=theme))
        if path == "/register": return self.send_html(page_register(theme=theme))
        if path == "/terms": return self.send_html(page_terms(theme))
        if path == "/logout":
            return self.redirect("/login", {"Set-Cookie": "token=; Max-Age=0; Path=/"})
        if path == "/theme":
            new_t = "light" if theme == "dark" else "dark"
            extra = {"Set-Cookie": f"theme={new_t}; Path=/; Max-Age=31536000"}
            if me:
                c = db(); c.execute("UPDATE users SET theme=? WHERE id=?", (new_t, me["id"])); c.commit(); c.close()
            return self.redirect(self.headers.get("Referer", "/home"), extra)

        if not me: return self.redirect("/login")

        if path == "/search": return self.send_html(page_search(me, qs.get("q", [""])[0], theme))
        if path == "/notifications": return self.send_html(page_notifications(me, theme))
        if path == "/chat": return self.send_html(page_chat_list(me, theme))
        if path == "/saved": return self.send_html(page_saved(me, theme))
        if path == "/settings": return self.send_html(page_settings(me, theme))
        if path == "/create": return self.send_html(page_create(me, qs.get("tab", ["post"])[0], theme))
        if path == "/channels": return self.send_html(page_channels(me, theme))
        if path == "/groups": return self.send_html(page_groups(me, theme))
        if path == "/bots": return self.send_html(page_bots(me, theme))
        if path == "/fun": return self.send_html(page_fun(me, theme))
        if path == "/docs": return self.send_html(page_docs(me, theme))
        if path == "/invite":
            code = qs.get("c", [""])[0]
            return self.send_html(page_invite(me, code, theme))

        if path == "/admin":
            if not g(me, "is_admin"): return self.redirect("/home")
            return self.send_html(page_admin(me, qs.get("tab", ["dashboard"])[0], theme))

        if path.startswith("/u/") and path.endswith("/followers"):
            return self.send_html(page_follow_list(me, unquote(path[3:-10]), "followers", theme))
        if path.startswith("/u/") and path.endswith("/following"):
            return self.send_html(page_follow_list(me, unquote(path[3:-10]), "following", theme))

        if path.startswith("/u/"):
            uname = unquote(path[3:].split("/")[0])
            c = db(); target = c.execute("SELECT * FROM users WHERE username=?", (uname,)).fetchone(); c.close()
            if not target: return self.send_html(layout("یافت نشد", "<div class='empty'>کاربر یافت نشد</div>", me, theme=theme), 404)
            return self.send_html(page_profile(me, target, theme))

        if path.startswith("/p/"):
            try: pid = int(path[3:].split("/")[0])
            except: return self.send_html("404", 404)
            record_view(pid, me["id"])
            return self.send_html(page_single_post(me, pid, theme))

        if path.startswith("/c/") or path.startswith("/g/") or path.startswith("/ch/"):
            if path.startswith("/ch/"): uname = unquote(path[4:].split("/")[0])
            elif path.startswith("/g/"): uname = unquote(path[3:].split("/")[0])
            else: uname = unquote(path[3:].split("/")[0])
            if path.endswith("/edit"):
                c = db(); conv = c.execute("SELECT * FROM conversations WHERE username=?", (uname,)).fetchone(); c.close()
                if not conv: return self.send_html("404", 404)
                return self.send_html(page_conv_edit(me, conv, theme))
            c = db(); conv = c.execute("SELECT * FROM conversations WHERE username=?", (uname,)).fetchone(); c.close()
            if not conv: return self.send_html(layout("یافت نشد", "<div class='empty'>یافت نشد</div>", me, theme=theme), 404)
            # private check
            if g(conv, "is_private"):
                mem = db().execute("SELECT 1 FROM conv_members WHERE cid=? AND uid=?", (conv["id"], me["id"])).fetchone()
                if not mem and conv["owner_id"] != me["id"]:
                    return self.send_html(layout("خصوصی", "<div class='empty'>این کانال/گروه خصوصی است. فقط با لینک دعوت وارد شوید.</div>", me, theme=theme))
            return self.send_html(page_conversation(me, conv, theme))

        if path.startswith("/s/") and path[3:].isdigit():
            return self.send_html(page_view_story(me, int(path[3:]), theme))

        self.send_html(layout("۴۰۴", "<div class='empty'><h2>صفحه پیدا نشد</h2></div>", me, theme=theme), 404)

    def route_post(self):
        path = urlparse(self.path).path
        fields, form = self.parse_body()
        me = self.get_user()

        if path == "/login":
            ident = form.get("ident", "").strip()
            pw = form.get("password", "")
            cap_sid = form.get("cap_sid", "")
            cap_ans = form.get("cap_ans", "")
            if not check_captcha(cap_sid, cap_ans):
                return self.send_html(page_login("پاسخ آزمون عددی اشتباه است."))
            if form.get("accept_terms") != "1":
                return self.send_html(page_login("پذیرش قوانین الزامی است."))
            c = db()
            user = c.execute("SELECT * FROM users WHERE username=? OR email=? OR public_id=?", (ident, ident, ident)).fetchone()
            c.close()
            if user and user["password"] == hpw(pw):
                if g(user, "is_blocked"): return self.send_html(page_login("حساب مسدود است."))
                tok = make_token(user["id"])
                ensure_saved_messages(user["id"])
                did = self.get_device_id()
                return self.redirect("/home", {
                    "Set-Cookie": f"token={tok}; Path=/; HttpOnly; SameSite=Lax",
                })
            return self.send_html(page_login("نام کاربری یا رمز اشتباه است."))

        if path == "/register":
            uname = clean_username(form.get("username", ""), 5)
            display = form.get("display_name", "").strip()[:40]
            pw = form.get("password", "")
            cap_sid = form.get("cap_sid", "")
            cap_ans = form.get("cap_ans", "")
            if not check_captcha(cap_sid, cap_ans):
                return self.send_html(page_register("پاسخ آزمون عددی اشتباه است."))
            if form.get("accept_terms") != "1":
                return self.send_html(page_register("برای ثبت‌نام باید قوانین را بپذیرید."))
            if not uname or len(pw) < 6:
                return self.send_html(page_register("نام کاربری حداقل ۵ حرف انگلیسی و رمز حداقل ۶ کاراکتر."))
            did = self.get_device_id()
            c = db()
            cnt = c.execute("SELECT COUNT(*) as c FROM users WHERE device_id=? AND is_bot=0", (did,)).fetchone()["c"]
            if cnt >= MAX_ACCOUNTS_PER_DEVICE:
                c.close()
                return self.send_html(page_register(f"از این دستگاه حداکثر {MAX_ACCOUNTS_PER_DEVICE} حساب می‌توان ساخت."))
            if c.execute("SELECT 1 FROM users WHERE username=?", (uname,)).fetchone():
                c.close(); return self.send_html(page_register("این نام کاربری گرفته شده."))
            pid = gen_user_public_id()
            while c.execute("SELECT 1 FROM users WHERE public_id=?", (pid,)).fetchone():
                pid = gen_user_public_id()
            c.execute("INSERT INTO users(username,display_name,password,public_id,theme,device_id,created) VALUES(?,?,?,?,?,?,?)",
                      (uname, display or uname, hpw(pw), pid, "dark", did, now()))
            c.commit()
            uid = c.execute("SELECT id FROM users WHERE username=?", (uname,)).fetchone()["id"]
            c.close()
            ensure_saved_messages(uid)
            try:
                c = db()
                bot = c.execute("SELECT id FROM users WHERE username='AvaBot'").fetchone()
                if bot:
                    uname_dm = f"dm_{min(uid,bot['id'])}_{max(uid,bot['id'])}"
                    conv = c.execute("SELECT id FROM conversations WHERE username=?", (uname_dm,)).fetchone()
                    if not conv:
                        c.execute("INSERT INTO conversations(username,title,is_group,owner_id,created) VALUES(?,?,0,?,?)",
                                  (uname_dm, "بات آوا", bot["id"], now()))
                        cid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
                        c.execute("INSERT INTO conv_members(cid,uid) VALUES(?,?)", (cid, uid))
                        c.execute("INSERT INTO conv_members(cid,uid) VALUES(?,?)", (cid, bot["id"]))
                    else: cid = conv["id"]
                    c.execute("INSERT INTO messages(cid,sender,body,created) VALUES(?,?,?,?)",
                              (cid, bot["id"], random.choice(WELCOME_MSGS), now()))
                    notify(uid, bot["id"], "welcome", 0, "به آوا خوش اومدی!")
                c.commit(); c.close()
            except: pass
            tok = make_token(uid)
            return self.redirect("/home", {
                "Set-Cookie": f"token={tok}; Path=/; HttpOnly; SameSite=Lax",
                "Set-Cookie": f"did={did}; Path=/; Max-Age=31536000",
            })

        if not me: return self.redirect("/login")

        # --- same handlers as before for post/like/etc with private channel support ---
        if path == "/post/create":
            content = form.get("content", "").strip()[:3000]
            image = save_media(fields.get("image")) if "image" in fields else None
            if content or image:
                c = db()
                c.execute("INSERT INTO posts(uid,content,image,is_explore,views,created) VALUES(?,?,?,?,0,?)",
                          (me["id"], content, image or "", 1, now()))
                c.commit(); c.close()
            return self.redirect("/home")

        if path.startswith("/p/") and path.endswith("/like"):
            try: pid = int(path[3:-5])
            except: return self.redirect("/home")
            c = db()
            if c.execute("SELECT 1 FROM likes WHERE uid=? AND pid=?", (me["id"], pid)).fetchone():
                c.execute("DELETE FROM likes WHERE uid=? AND pid=?", (me["id"], pid))
            else:
                c.execute("INSERT INTO likes(uid,pid) VALUES(?,?)", (me["id"], pid))
                post = c.execute("SELECT uid FROM posts WHERE id=?", (pid,)).fetchone()
                if post: notify(post["uid"], me["id"], "like", pid, "پستت را لایک کرد")
            c.commit(); c.close()
            return self.redirect(self.headers.get("Referer", "/home"))

        if path.startswith("/p/") and path.endswith("/save"):
            try: pid = int(path[3:-5])
            except: return self.redirect("/home")
            c = db()
            if c.execute("SELECT 1 FROM saves WHERE uid=? AND pid=?", (me["id"], pid)).fetchone():
                c.execute("DELETE FROM saves WHERE uid=? AND pid=?", (me["id"], pid))
            else:
                c.execute("INSERT INTO saves(uid,pid) VALUES(?,?)", (me["id"], pid))
            c.commit(); c.close()
            return self.redirect(self.headers.get("Referer", "/home"))

        if path.startswith("/p/") and path.endswith("/comment"):
            try: pid = int(path[3:-8])
            except: return self.redirect("/home")
            body = form.get("body", "").strip()[:800]
            if body:
                c = db()
                c.execute("INSERT INTO comments(pid,uid,body,created) VALUES(?,?,?,?)", (pid, me["id"], body, now()))
                post = c.execute("SELECT uid FROM posts WHERE id=?", (pid,)).fetchone()
                if post: notify(post["uid"], me["id"], "comment", pid, "روی پستت کامنت گذاشت")
                c.commit(); c.close()
            return self.redirect(f"/p/{pid}")

        if path.startswith("/u/") and path.endswith("/follow"):
            uname = unquote(path[3:-7])
            c = db()
            target = c.execute("SELECT id FROM users WHERE username=?", (uname,)).fetchone()
            if target and target["id"] != me["id"]:
                if c.execute("SELECT 1 FROM follows WHERE a=? AND b=?", (me["id"], target["id"])).fetchone():
                    c.execute("DELETE FROM follows WHERE a=? AND b=?", (me["id"], target["id"]))
                else:
                    c.execute("INSERT INTO follows(a,b) VALUES(?,?)", (me["id"], target["id"]))
                    notify(target["id"], me["id"], "follow", me["id"], "دنبالت کرد")
                c.commit()
            c.close()
            return self.redirect(self.headers.get("Referer", f"/u/{uname}"))

        if path == "/settings":
            display = form.get("display_name", "").strip()[:40]
            bio = form.get("bio", "").strip()[:300]
            new_uname = clean_username(form.get("username", ""), 5)
            c = db()
            if "avatar" in fields:
                av = save_media(fields["avatar"])
                if av: c.execute("UPDATE users SET avatar=? WHERE id=?", (av, me["id"]))
            if new_uname and new_uname != me["username"]:
                if not c.execute("SELECT 1 FROM users WHERE username=? AND id!=?", (new_uname, me["id"])).fetchone():
                    c.execute("UPDATE users SET username=? WHERE id=?", (new_uname, me["id"]))
            c.execute("UPDATE users SET display_name=?, bio=? WHERE id=?", (display, bio, me["id"]))
            c.commit(); c.close()
            return self.redirect("/settings")

        if path == "/story/create":
            image = save_media(fields.get("image")) if "image" in fields else None
            caption = form.get("caption", "").strip()[:200]
            if image:
                expires = (datetime.now(timezone.utc) + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
                c = db()
                c.execute("INSERT INTO stories(uid,image,caption,created,expires) VALUES(?,?,?,?,?)",
                          (me["id"], image, caption, now(), expires))
                c.commit(); c.close()
            return self.redirect("/home")

        if path == "/create/channel":
            title = form.get("title", "").strip()[:60]
            uname = clean_username(form.get("username", ""), 7)
            desc = form.get("description", "").strip()[:300]
            is_priv = 1 if form.get("is_private") == "1" else 0
            if not uname:
                return self.redirect("/chat?err=id")
            if title:
                c = db()
                if c.execute("SELECT 1 FROM conversations WHERE username=?", (uname,)).fetchone():
                    c.close(); return self.redirect("/chat?err=taken")
                inv = gen_invite() if is_priv else ""
                c.execute("INSERT INTO conversations(username,title,is_group,is_channel,is_private,invite_code,owner_id,description,created) VALUES(?,?,0,1,?,?,?,?,?)",
                          (uname, title, is_priv, inv, me["id"], desc, now()))
                cid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
                c.execute("INSERT INTO conv_members(cid,uid,role) VALUES(?,?,?)", (cid, me["id"], "owner"))
                c.commit(); c.close()
                return self.redirect(f"/ch/{uname}")
            return self.redirect("/chat")

        if path == "/create/group":
            title = form.get("title", "").strip()[:60]
            uname = clean_username(form.get("username", ""), 7)
            is_priv = 1 if form.get("is_private") == "1" else 0
            if not uname:
                return self.redirect("/chat?err=id")
            if title:
                c = db()
                if c.execute("SELECT 1 FROM conversations WHERE username=?", (uname,)).fetchone():
                    c.close(); return self.redirect("/chat?err=taken")
                inv = gen_invite() if is_priv else ""
                c.execute("INSERT INTO conversations(username,title,is_group,is_channel,is_private,invite_code,owner_id,created) VALUES(?,?,1,0,?,?,?,?)",
                          (uname, title, is_priv, inv, me["id"], now()))
                cid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
                c.execute("INSERT INTO conv_members(cid,uid,role) VALUES(?,?,?)", (cid, me["id"], "owner"))
                c.commit(); c.close()
                return self.redirect(f"/g/{uname}")
            return self.redirect("/chat")

        if path == "/invite/join":
            code = form.get("code", "").strip()
            c = db()
            conv = c.execute("SELECT * FROM conversations WHERE invite_code=?", (code,)).fetchone()
            if conv:
                c.execute("INSERT OR IGNORE INTO conv_members(cid,uid,role) VALUES(?,?,?)", (conv["id"], me["id"], "member"))
                c.commit()
                c.close()
                prefix = "ch" if conv["is_channel"] else "g"
                return self.redirect(f"/{prefix}/{conv['username']}")
            c.close()
            return self.redirect("/chat")

        if path.endswith("/edit") and (path.startswith("/ch/") or path.startswith("/g/")):
            parts = path.strip("/").split("/")
            uname = unquote(parts[1])
            title = form.get("title", "").strip()[:60]
            desc = form.get("description", "").strip()[:300]
            is_priv = 1 if form.get("is_private") == "1" else 0
            c = db()
            conv = c.execute("SELECT * FROM conversations WHERE username=?", (uname,)).fetchone()
            if conv and conv["owner_id"] == me["id"]:
                inv = g(conv, "invite_code") or ""
                if is_priv and not inv:
                    inv = gen_invite()
                if not is_priv:
                    inv = ""
                if "avatar" in fields:
                    av = save_media(fields["avatar"])
                    if av: c.execute("UPDATE conversations SET avatar=? WHERE id=?", (av, conv["id"]))
                c.execute("UPDATE conversations SET title=?, description=?, is_private=?, invite_code=? WHERE id=?",
                          (title or conv["title"], desc, is_priv, inv, conv["id"]))
                c.commit()
            c.close()
            prefix = "ch" if conv and conv["is_channel"] else "g"
            return self.redirect(f"/{prefix}/{uname}")

        if (path.startswith("/c/") or path.startswith("/g/") or path.startswith("/ch/")) and path.endswith("/send"):
            parts = path.strip("/").split("/")
            uname = unquote(parts[1])
            body = form.get("body", "").strip()[:2000]
            image = save_media(fields.get("image")) if "image" in fields else None
            c = db()
            conv = c.execute("SELECT * FROM conversations WHERE username=?", (uname,)).fetchone()
            if conv and (body or image):
                member = c.execute("SELECT * FROM conv_members WHERE cid=? AND uid=?", (conv["id"], me["id"])).fetchone()
                if conv["is_channel"]:
                    if not member or member["role"] not in ("owner", "admin"):
                        c.close(); return self.redirect(f"/ch/{uname}")
                if member or conv["is_channel"]:
                    if not member and conv["is_channel"]:
                        c.execute("INSERT OR IGNORE INTO conv_members(cid,uid,role) VALUES(?,?,?)", (conv["id"], me["id"], "member"))
                    c.execute("INSERT INTO messages(cid,sender,body,image,created) VALUES(?,?,?,?,?)",
                              (conv["id"], me["id"], body, image or "", now()))
                    c.commit()
            c.close()
            prefix = "ch" if conv and conv["is_channel"] else ("g" if conv and conv["is_group"] else "c")
            return self.redirect(f"/{prefix}/{uname}")

        if path == "/chat/start":
            target_uname = form.get("username", "").strip()
            c = db()
            target = c.execute("SELECT id FROM users WHERE username=?", (target_uname,)).fetchone()
            if target and target["id"] != me["id"]:
                uname = f"dm_{min(me['id'],target['id'])}_{max(me['id'],target['id'])}"
                existing = c.execute("SELECT id FROM conversations WHERE username=?", (uname,)).fetchone()
                if not existing:
                    c.execute("INSERT INTO conversations(username,title,is_group,owner_id,created) VALUES(?,?,0,?,?)",
                              (uname, "چت خصوصی", me["id"], now()))
                    cid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
                    c.execute("INSERT INTO conv_members(cid,uid) VALUES(?,?)", (cid, me["id"]))
                    c.execute("INSERT INTO conv_members(cid,uid) VALUES(?,?)", (cid, target["id"]))
                    c.commit()
                c.close()
                return self.redirect(f"/c/{uname}")
            c.close()
            return self.redirect("/chat")

        if path.startswith("/join/"):
            uname = unquote(path[6:])
            c = db()
            conv = c.execute("SELECT * FROM conversations WHERE username=?", (uname,)).fetchone()
            if conv and not g(conv, "is_private"):
                c.execute("INSERT OR IGNORE INTO conv_members(cid,uid,role) VALUES(?,?,?)", (conv["id"], me["id"], "member"))
                c.commit()
            c.close()
            prefix = "ch" if conv and conv["is_channel"] else "g"
            return self.redirect(f"/{prefix}/{uname}")

        if path == "/bot/create":
            name = form.get("name", "").strip()[:40]
            uname = clean_username(form.get("username", ""), 5)
            if name and uname:
                uname = uname if uname.endswith("bot") else uname + "bot"
                c = db()
                if c.execute("SELECT 1 FROM users WHERE username=?", (uname,)).fetchone():
                    c.close(); return self.redirect("/bots?err=taken")
                token = "ava:" + secrets.token_hex(16)
                pid = gen_user_public_id()
                c.execute("INSERT INTO users(username,display_name,password,public_id,is_bot,is_verified,bio,bot_token,theme,created) VALUES(?,?,?,?,1,0,?,?,?,?)",
                          (uname, name, hpw(token), pid, f"ربات · @{me['username']}", token, "dark", now()))
                bot_uid = c.execute("SELECT id FROM users WHERE username=?", (uname,)).fetchone()["id"]
                c.execute("INSERT INTO bots(owner_id,bot_uid,token,name,username,created) VALUES(?,?,?,?,?,?)",
                          (me["id"], bot_uid, token, name, uname, now()))
                c.commit(); c.close()
                return self.redirect("/bots?ok=1")
            return self.redirect("/bots")

        # Admin (same pattern)
        if path.startswith("/admin/"):
            if not g(me, "is_admin"): return self.redirect("/home")
            action = path[7:]
            if action in ("block", "unblock", "make_admin", "remove_admin", "verify", "unverify", "delete_user"):
                target_pid = form.get("public_id", "").strip()
                c = db()
                target = c.execute("SELECT * FROM users WHERE public_id=?", (target_pid,)).fetchone()
                if target:
                    tid = target["id"]
                    if action == "block": c.execute("UPDATE users SET is_blocked=1 WHERE id=?", (tid,))
                    elif action == "unblock": c.execute("UPDATE users SET is_blocked=0 WHERE id=?", (tid,))
                    elif action == "make_admin": c.execute("UPDATE users SET is_admin=1 WHERE id=?", (tid,))
                    elif action == "remove_admin" and tid != me["id"]:
                        c.execute("UPDATE users SET is_admin=0 WHERE id=?", (tid,))
                    elif action == "verify": c.execute("UPDATE users SET is_verified=1 WHERE id=?", (tid,))
                    elif action == "unverify": c.execute("UPDATE users SET is_verified=0 WHERE id=?", (tid,))
                    elif action == "delete_user" and tid != me["id"]:
                        for tbl, col in [("likes","uid"),("comments","uid"),("saves","uid"),("posts","uid"),("stories","uid")]:
                            c.execute(f"DELETE FROM {tbl} WHERE {col}=?", (tid,))
                        c.execute("DELETE FROM follows WHERE a=? OR b=?", (tid, tid))
                        c.execute("DELETE FROM users WHERE id=?", (tid,))
                    c.commit()
                c.close()
                return self.redirect("/admin?tab=users")
            if action == "broadcast":
                body = form.get("body", "").strip()[:2000]
                image = save_media(fields.get("image")) if "image" in fields else None
                if body or image:
                    c = db()
                    users = c.execute("SELECT id FROM users WHERE is_blocked=0 AND is_bot=0").fetchall()
                    bot = c.execute("SELECT id FROM users WHERE username='AvaBot'").fetchone()
                    sender = bot["id"] if bot else me["id"]
                    for urow in users:
                        notify(urow["id"], sender, "broadcast", 0, (body or "پیام")[:80])
                        try:
                            uname_dm = f"dm_{min(urow['id'],sender)}_{max(urow['id'],sender)}"
                            conv = c.execute("SELECT id FROM conversations WHERE username=?", (uname_dm,)).fetchone()
                            if not conv:
                                c.execute("INSERT INTO conversations(username,title,is_group,owner_id,created) VALUES(?,?,0,?,?)",
                                          (uname_dm, "بات آوا", sender, now()))
                                cid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
                                c.execute("INSERT INTO conv_members(cid,uid) VALUES(?,?)", (cid, urow["id"]))
                                c.execute("INSERT INTO conv_members(cid,uid) VALUES(?,?)", (cid, sender))
                            else: cid = conv["id"]
                            c.execute("INSERT INTO messages(cid,sender,body,image,created) VALUES(?,?,?,?,?)",
                                      (cid, sender, f"📢 {body}" if body else "📢 پیام همگانی", image or "", now()))
                        except: pass
                    c.execute("INSERT INTO broadcasts(body,image,sent_by,created) VALUES(?,?,?,?)",
                              (body, image or "", me["id"], now()))
                    c.commit(); c.close()
                return self.redirect("/admin?tab=broadcast")
            if action == "ad_create":
                title = form.get("title", "").strip()[:100]
                body = form.get("body", "").strip()[:500]
                link = form.get("link", "").strip()[:300]
                image = save_media(fields.get("image")) if "image" in fields else None
                if title and body:
                    c = db()
                    c.execute("INSERT INTO ads(title,body,link,image,is_active,created) VALUES(?,?,?,?,1,?)",
                              (title, body, link, image or "", now()))
                    c.commit(); c.close()
                return self.redirect("/admin?tab=ads")
            if action == "ad_toggle":
                aid = form.get("ad_id", "")
                c = db()
                ad = c.execute("SELECT is_active FROM ads WHERE id=?", (aid,)).fetchone()
                if ad:
                    c.execute("UPDATE ads SET is_active=? WHERE id=?", (0 if ad["is_active"] else 1, aid))
                    c.commit()
                c.close()
                return self.redirect("/admin?tab=ads")
            if action == "ad_delete":
                c = db(); c.execute("DELETE FROM ads WHERE id=?", (form.get("ad_id", ""),)); c.commit(); c.close()
                return self.redirect("/admin?tab=ads")
            if action == "toggle_explore":
                pid = form.get("post_id", "")
                c = db()
                p = c.execute("SELECT is_explore FROM posts WHERE id=?", (pid,)).fetchone()
                if p:
                    c.execute("UPDATE posts SET is_explore=? WHERE id=?", (0 if p["is_explore"] else 1, pid))
                    c.commit()
                c.close()
                return self.redirect("/admin?tab=posts")
            if action == "delete_post":
                pid = form.get("post_id", "")
                c = db()
                for t in ("likes", "comments", "saves", "post_views"):
                    try: c.execute(f"DELETE FROM {t} WHERE pid=?", (pid,))
                    except: pass
                c.execute("DELETE FROM posts WHERE id=?", (pid,))
                c.commit(); c.close()
                return self.redirect("/admin?tab=posts")
            if action == "settings":
                set_setting("welcome_enabled", "1" if form.get("welcome_enabled") == "1" else "0")
                set_setting("explore_mode", form.get("explore_mode", "all"))
                return self.redirect("/admin?tab=settings")
            return self.redirect("/admin")

        return self.redirect("/home")

# ==================== UI (compact shared styles + pages) ====================
def css_vars(theme):
    if theme == "light":
        return ":root{--bg:#fafafa;--card:#fff;--text:#262626;--muted:#8e8e8e;--border:#dbdbdb;--accent:#0095f6;--warm:#ed4956;--warning:#e0a800;--danger:#ed4956;--nav-bg:rgba(255,255,255,.95);--input-bg:#fafafa;--bubble-other:#efefef;--hover:rgba(0,0,0,.03)}"
    return ":root{--bg:#0b0b0f;--card:#14141a;--text:#f0f0f5;--muted:#8b8b9a;--border:#252530;--accent:#00d4aa;--warm:#ff6b35;--warning:#f59e0b;--danger:#ff3b5c;--nav-bg:rgba(20,20,26,.95);--input-bg:#0e0e14;--bubble-other:#1c1c26;--hover:rgba(255,255,255,.03)}"

def layout(title, body, me=None, active="", theme="dark"):
    nav = ""
    if me:
        nav = f'''<div class="bottom-nav">
            <a href="/home" class="nav-item {'active' if active=='home' else ''}">{ic('home',24)}<span>خانه</span></a>
            <a href="/explore" class="nav-item {'active' if active=='explore' else ''}">{ic('explore',24)}<span>کاوش</span></a>
            <a href="/create" class="nav-item {'active' if active=='create' else ''}">{ic('plus',26)}<span>بساز</span></a>
            <a href="/chat" class="nav-item {'active' if active=='chat' else ''}">{ic('chat',24)}<span>پیام‌ها</span></a>
            <a href="/u/{esc(g(me,'username'))}" class="nav-item {'active' if active=='profile' else ''}">{ic('user',24)}<span>پروفایل</span></a>
        </div>'''
    admin_btn = f'<a href="/admin" style="color:var(--warning)">{ic("admin")}</a>' if me and g(me, "is_admin") else ""
    theme_icon = ic("sun", 20) if theme == "dark" else ic("moon", 20)
    return f'''<!DOCTYPE html><html lang="fa" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>{esc(title)} · {APP_NAME}</title>
<style>
{css_vars(theme)}
*{{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
body{{background:var(--bg);color:var(--text);padding-bottom:80px;min-height:100vh}}
a{{text-decoration:none;color:inherit}}
.navbar{{position:sticky;top:0;background:var(--nav-bg);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:10px 14px;display:flex;justify-content:space-between;align-items:center;z-index:100}}
.navbar .logo{{font-weight:700;font-size:18px;display:flex;align-items:center;gap:8px}}
.bottom-nav{{position:fixed;bottom:0;left:0;right:0;background:var(--nav-bg);backdrop-filter:blur(12px);border-top:1px solid var(--border);display:flex;justify-content:space-around;padding:8px 0 12px;z-index:100}}
.nav-item{{display:flex;flex-direction:column;align-items:center;font-size:10px;color:var(--muted);gap:2px}}
.nav-item.active{{color:var(--text)}}
.container{{max-width:600px;margin:0 auto;padding:10px 12px}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:12px;margin-bottom:12px;overflow:hidden}}
.post-header{{display:flex;align-items:center;padding:12px;gap:10px}}
.post-header .name{{font-weight:600;font-size:14px;display:flex;align-items:center;gap:3px;flex-wrap:wrap}}
.post-image{{width:100%;max-height:600px;object-fit:cover;display:block}}
.post-actions{{display:flex;padding:8px 12px 4px;gap:14px;align-items:center}}
.post-actions a{{display:flex;flex-direction:column;align-items:center;gap:2px;font-size:11px;color:var(--muted)}}
.post-actions a svg{{color:var(--text)}}
.post-actions .count{{font-size:11px;font-weight:600;color:var(--text)}}
.post-content{{padding:4px 12px 6px;font-size:14px;line-height:1.5}}
.post-time{{padding:0 12px 12px;font-size:11px;color:var(--muted)}}
input,textarea,select{{width:100%;padding:11px 12px;border:1px solid var(--border);border-radius:10px;background:var(--input-bg);color:var(--text);margin-bottom:10px;font-size:14px;outline:none}}
.btn{{padding:9px 16px;border-radius:10px;border:none;font-weight:600;cursor:pointer;font-size:14px;display:inline-block;text-align:center}}
.btn-primary{{background:var(--accent);color:#fff}}
.btn-outline{{background:transparent;border:1px solid var(--border);color:var(--text)}}
.btn-danger{{background:var(--danger);color:#fff}}
.btn-warning{{background:var(--warning);color:#111}}
.auth-box{{max-width:380px;margin:36px auto;padding:28px 24px;background:var(--card);border:1px solid var(--border);border-radius:16px;text-align:center}}
.auth-box h1{{font-size:26px;margin-bottom:4px}}
.auth-box .error{{color:var(--danger);margin-bottom:10px;font-size:13px;background:rgba(237,73,86,.08);padding:10px;border-radius:8px}}
.empty{{text-align:center;padding:40px 16px;color:var(--muted);font-size:14px}}
.badge-bot{{display:inline-flex;align-items:center;gap:2px;font-size:10px;background:rgba(0,168,132,.12);color:#00a884;padding:1px 6px;border-radius:6px}}
.list-item{{display:flex;gap:12px;padding:10px 12px;border-bottom:1px solid var(--border);align-items:center}}
.stories-row{{display:flex;gap:12px;overflow-x:auto;padding:6px 0 12px;scrollbar-width:none}}
.story-item{{flex-shrink:0;text-align:center;width:68px}}
.story-ring{{width:64px;height:64px;border-radius:50%;padding:2px;background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888);display:flex;align-items:center;justify-content:center}}
.story-ring img,.story-ring>div{{width:58px;height:58px;border-radius:50%;border:2px solid var(--bg);object-fit:cover}}
.admin-tabs{{display:flex;gap:6px;overflow-x:auto;margin-bottom:14px}}
.admin-tabs a{{padding:7px 12px;border-radius:20px;font-size:12px;background:var(--card);border:1px solid var(--border);white-space:nowrap}}
.admin-tabs a.active{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.admin-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px;margin-bottom:8px}}
.admin-actions{{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}}
.admin-actions .btn{{padding:5px 9px;font-size:11px}}
.stats-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(90px,1fr));gap:8px;margin-bottom:16px}}
.stat-box{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px;text-align:center}}
.stat-box .num{{font-size:20px;font-weight:700;color:var(--accent)}}
.stat-box .lbl{{font-size:10px;color:var(--muted)}}
.ad-banner{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px;margin-bottom:12px;display:flex;gap:10px;align-items:center}}
.msg-bubble{{max-width:78%;padding:9px 12px;border-radius:14px;margin-bottom:6px;font-size:14px}}
.msg-me{{background:var(--accent);color:#fff;margin-right:auto;border-bottom-right-radius:4px}}
.msg-other{{background:var(--bubble-other);margin-left:auto;border-bottom-left-radius:4px}}
.msg-meta{{font-size:10px;opacity:.7;margin-top:3px}}
.create-tabs{{display:flex;gap:8px;margin-bottom:12px}}
.create-tabs a{{flex:1;text-align:center;padding:10px;border-radius:10px;background:var(--card);border:1px solid var(--border);font-weight:600;font-size:13px}}
.create-tabs a.active{{border-color:var(--accent);color:var(--accent)}}
.footer-dev{{text-align:center;padding:20px;font-size:11px;color:var(--muted)}}
.token-box{{background:var(--input-bg);border:1px dashed var(--accent);border-radius:10px;padding:12px;font-family:monospace;font-size:12px;word-break:break-all;margin:8px 0;direction:ltr;text-align:left}}
.fun-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}}
.fun-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px;text-align:center}}
.terms-box{{font-size:13px;line-height:1.8;padding:8px}}
.terms-box h2{{font-size:18px;margin-bottom:12px}}
.terms-box h3{{font-size:14px;margin:14px 0 6px}}
.terms-box ul{{padding-right:18px;margin-bottom:8px}}
.terms-check{{display:flex;align-items:flex-start;gap:8px;text-align:right;font-size:12px;margin:12px 0;color:var(--muted)}}
.terms-check input{{width:auto;margin:0}}
.cap-row{{display:flex;gap:8px;align-items:center;margin-bottom:10px}}
.cap-q{{background:var(--input-bg);border:1px solid var(--border);border-radius:10px;padding:10px 14px;font-weight:700;font-size:16px;min-width:70px;text-align:center}}
.priv-tag{{font-size:10px;background:rgba(237,73,86,.12);color:var(--danger);padding:1px 6px;border-radius:6px}}
</style></head><body>
<div class="navbar">
  <a href="/home" class="logo">{LOGO_SVG} {APP_NAME}</a>
  <div style="display:flex;gap:14px;align-items:center">
    {admin_btn}
    <a href="/theme">{theme_icon}</a>
    <a href="/notifications">{ic('bell',20)}</a>
    <a href="/search">{ic('search',20)}</a>
    <a href="/settings">{ic('settings',20)}</a>
  </div>
</div>
<div class="container">{body}</div>
{nav}
</body></html>'''

def page_login(error="", theme="dark"):
    sid, q = store_captcha()
    err = f'<div class="error">{esc(error)}</div>' if error else ""
    body = f'''
    <div class="auth-box">
      <div style="margin-bottom:8px">{LOGO_SVG.replace('width="34"','width="56"').replace('height="34"','height="56"')}</div>
      <h1>{APP_NAME}</h1>
      <p style="color:var(--muted);font-size:13px;margin-bottom:16px">{APP_TAGLINE}</p>
      {err}
      <form method="POST" action="/login">
        <input type="text" name="ident" placeholder="نام کاربری یا آیدی" required>
        <input type="password" name="password" placeholder="رمز عبور" required>
        <div class="cap-row">
          <div class="cap-q">{esc(q)} = ?</div>
          <input type="hidden" name="cap_sid" value="{sid}">
          <input type="text" name="cap_ans" placeholder="پاسخ" required style="margin:0;flex:1" inputmode="numeric">
        </div>
        <label class="terms-check">
          <input type="checkbox" name="accept_terms" value="1" required>
          <span><a href="/terms" target="_blank" style="color:var(--accent)">قوانین آوا</a> را خوانده و می‌پذیرم</span>
        </label>
        <button type="submit" class="btn btn-primary" style="width:100%">ورود</button>
      </form>
      <div style="margin-top:14px;font-size:13px;color:var(--muted)">حساب نداری؟ <a href="/register" style="color:var(--accent)">ثبت‌نام</a></div>
      <div class="footer-dev">{DEVELOPER}</div>
    </div>'''
    return layout("ورود", body, theme=theme)

def page_register(error="", theme="dark"):
    sid, q = store_captcha()
    err = f'<div class="error">{esc(error)}</div>' if error else ""
    body = f'''
    <div class="auth-box">
      <div style="margin-bottom:8px">{LOGO_SVG.replace('width="34"','width="56"').replace('height="34"','height="56"')}</div>
      <h1>ثبت‌نام</h1>
      <p style="color:var(--muted);font-size:13px;margin-bottom:16px">حداکثر ۳ حساب · نام کاربری حداقل ۵ حرف</p>
      {err}
      <form method="POST" action="/register">
        <input type="text" name="username" placeholder="نام کاربری (انگلیسی، حداقل ۵)" required minlength="5" pattern="[a-zA-Z0-9_]{{5,24}}">
        <input type="text" name="display_name" placeholder="نام نمایشی" required>
        <input type="password" name="password" placeholder="رمز عبور (حداقل ۶)" required minlength="6">
        <div class="cap-row">
          <div class="cap-q">{esc(q)} = ?</div>
          <input type="hidden" name="cap_sid" value="{sid}">
          <input type="text" name="cap_ans" placeholder="پاسخ" required style="margin:0;flex:1" inputmode="numeric">
        </div>
        <label class="terms-check">
          <input type="checkbox" name="accept_terms" value="1" required>
          <span><a href="/terms" target="_blank" style="color:var(--accent)">قوانین و شرایط</a> را خوانده‌ام و می‌پذیرم</span>
        </label>
        <button type="submit" class="btn btn-primary" style="width:100%">ساخت حساب</button>
      </form>
      <div style="margin-top:14px;font-size:13px;color:var(--muted)">حساب داری؟ <a href="/login" style="color:var(--accent)">ورود</a></div>
    </div>'''
    return layout("ثبت‌نام", body, theme=theme)

def page_terms(theme="dark"):
    body = f'<div class="card" style="padding:16px">{TERMS_HTML}</div><a href="/register" class="btn btn-primary" style="width:100%;margin-top:8px">بازگشت به ثبت‌نام</a>'
    return layout("قوانین", body, theme=theme)

def render_stories_bar(me, theme):
    c = db()
    stories = c.execute("""
        SELECT s.*, u.username, u.display_name, u.avatar FROM stories s JOIN users u ON s.uid=u.id
        WHERE s.expires > ? AND u.is_blocked=0 GROUP BY s.uid ORDER BY s.id DESC LIMIT 20
    """, (now(),)).fetchall()
    c.close()
    h = '<div class="stories-row">'
    h += f'''<a href="/create?tab=story" class="story-item">
      <div class="story-ring" style="background:var(--border)">
        <div style="width:58px;height:58px;border-radius:50%;background:var(--card);display:flex;align-items:center;justify-content:center;font-size:26px;color:var(--accent);border:2px solid var(--bg)">+</div>
      </div>
      <div style="font-size:10px;margin-top:3px;color:var(--muted)">استوری</div></a>'''
    for s in stories:
        h += f'''<a href="/s/{s['id']}" class="story-item">
          <div class="story-ring">{avatar_html(s, 58)}</div>
          <div style="font-size:10px;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{esc(g(s,"display_name","")[:9])}</div></a>'''
    return h + '</div>'

def render_ad(theme):
    c = db()
    ad = c.execute("SELECT * FROM ads WHERE is_active=1 ORDER BY RANDOM() LIMIT 1").fetchone()
    c.close()
    if not ad: return ""
    img = f'<img src="/uploads/{esc(ad["image"])}" style="width:52px;height:52px;border-radius:8px;object-fit:cover">' if g(ad, "image") else '<div style="width:52px;height:52px;border-radius:8px;background:var(--border);display:flex;align-items:center;justify-content:center">📣</div>'
    link = f'href="{esc(ad["link"])}" target="_blank"' if g(ad, "link") else 'href="#"'
    return f'''<a {link} class="ad-banner">{img}<div style="flex:1;min-width:0">
      <div style="font-weight:600;font-size:13px">{esc(ad["title"])} <span style="font-size:10px;color:var(--muted)">Sponsored</span></div>
      <div style="font-size:12px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{esc(g(ad,"body","")[:70])}</div>
    </div></a>'''

def render_post_card(p, me, theme):
    c = db()
    liked = c.execute("SELECT 1 FROM likes WHERE uid=? AND pid=?", (me["id"], p["id"])).fetchone()
    saved = c.execute("SELECT 1 FROM saves WHERE uid=? AND pid=?", (me["id"], p["id"])).fetchone()
    likes = c.execute("SELECT COUNT(*) as c FROM likes WHERE pid=?", (p["id"],)).fetchone()["c"]
    comments = c.execute("SELECT COUNT(*) as c FROM comments WHERE pid=?", (p["id"],)).fetchone()["c"]
    views = g(p, "views") or 0
    c.close()
    heart = "heart_fill" if liked else "heart"
    bookmark = "bookmark_fill" if saved else "bookmark"
    img = f'<a href="/p/{p["id"]}"><img src="/uploads/{esc(p["image"])}" class="post-image" loading="lazy"></a>' if g(p, "image") else ""
    return f'''<article class="card">
      <div class="post-header">
        <a href="/u/{esc(p["username"])}">{avatar_html(p, 36)}</a>
        <div style="flex:1"><a href="/u/{esc(p["username"])}" class="name">{esc(p["display_name"])}{verified_badge(p)}{admin_badge(p)}{bot_badge(p)}</a>
        <div style="font-size:11px;color:var(--muted)">@{esc(p["username"])}</div></div>
      </div>
      {img}
      <div class="post-actions">
        <a href="/p/{p['id']}/like">{ic(heart, 24)}<span class="count">{likes}</span></a>
        <a href="/p/{p['id']}">{ic('comment', 22)}<span class="count">{comments}</span></a>
        <a href="/p/{p['id']}/save">{ic(bookmark, 22)}</a>
        <span style="margin-right:auto;display:flex;align-items:center;gap:4px;font-size:11px;color:var(--muted)">{ic('eye',14)} {views}</span>
      </div>
      <div class="post-content">{format_text(g(p,"content") or "")}</div>
      <div class="post-time">{time_ago(p["created"])}</div>
    </article>'''

def page_home(me, theme):
    c = db()
    mode = get_setting("explore_mode", "all")
    if mode == "all":
        posts = c.execute("""SELECT p.*, u.username, u.display_name, u.avatar, u.is_verified, u.is_admin, u.is_bot
            FROM posts p JOIN users u ON p.uid=u.id WHERE u.is_blocked=0 ORDER BY p.id DESC LIMIT 40""").fetchall()
    else:
        posts = c.execute("""SELECT p.*, u.username, u.display_name, u.avatar, u.is_verified, u.is_admin, u.is_bot
            FROM posts p JOIN users u ON p.uid=u.id
            WHERE u.is_blocked=0 AND (p.uid=? OR p.uid IN (SELECT b FROM follows WHERE a=?))
            ORDER BY p.id DESC LIMIT 40""", (me["id"], me["id"])).fetchall()
    top_ch = c.execute("SELECT * FROM conversations WHERE is_channel=1 AND is_private=0 ORDER BY id DESC LIMIT 6").fetchall()
    c.close()
    posts_html = "".join(render_post_card(p, me, theme) for p in posts) or '<div class="empty">هنوز پستی نیست</div>'
    top_html = ""
    if top_ch:
        top_html = '<div style="margin-bottom:12px"><div style="font-size:12px;color:var(--muted);margin-bottom:6px;font-weight:600">کانال‌های عمومی</div><div style="display:flex;gap:8px;overflow-x:auto">'
        for ch in top_ch:
            top_html += f'<a href="/ch/{esc(ch["username"])}" style="flex-shrink:0;background:var(--card);border:1px solid var(--border);border-radius:10px;padding:8px 12px;font-size:12px">📢 {esc(ch["title"])}</a>'
        top_html += '</div></div>'
    body = f'''{render_stories_bar(me, theme)}{render_ad(theme)}
    <div class="fun-grid">
      <a href="/fun" class="fun-card"><div style="font-size:22px">🎮</div><div style="font-weight:600;font-size:13px;margin-top:4px">سرگرمی</div></a>
      <a href="/bots" class="fun-card"><div style="font-size:22px">🤖</div><div style="font-weight:600;font-size:13px;margin-top:4px">ربات‌ها</div></a>
    </div>
    {top_html}{posts_html}
    <div class="footer-dev">{DEVELOPER} · {APP_NAME}</div>'''
    return layout("خانه", body, me, "home", theme)

def page_explore(me, theme):
    c = db()
    posts = c.execute("""SELECT p.*, u.username, u.display_name, u.avatar, u.is_verified, u.is_admin, u.is_bot
        FROM posts p JOIN users u ON p.uid=u.id WHERE u.is_blocked=0 AND p.is_explore=1 ORDER BY p.id DESC LIMIT 48""").fetchall()
    c.close()
    grid = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:2px">'
    for p in posts:
        if g(p, "image"):
            grid += f'<a href="/p/{p["id"]}"><img src="/uploads/{esc(p["image"])}" style="width:100%;aspect-ratio:1;object-fit:cover" loading="lazy"></a>'
        else:
            grid += f'<a href="/p/{p["id"]}" style="background:var(--card);aspect-ratio:1;display:flex;align-items:center;justify-content:center;padding:6px;font-size:10px;color:var(--muted)">{esc((g(p,"content") or "")[:50])}</a>'
    grid += '</div>'
    body = f'<h2 style="font-size:16px;margin-bottom:10px;font-weight:600">کاوش</h2>{render_ad(theme)}{grid if posts else "<div class=empty>خالی</div>"}'
    return layout("کاوش", body, me, "explore", theme)

def page_fun(me, theme):
    body = f'''<h2 style="font-size:16px;margin-bottom:12px;font-weight:600">سرگرمی</h2>
    <div class="fun-grid">
      <a href="/bots" class="fun-card"><div style="font-size:28px">🤖</div><div style="font-weight:600;margin-top:6px;font-size:13px">ربات‌ساز</div></a>
      <a href="/docs" class="fun-card"><div style="font-size:28px">📚</div><div style="font-weight:600;margin-top:6px;font-size:13px">مستندات بات</div></a>
      <a href="/channels" class="fun-card"><div style="font-size:28px">📢</div><div style="font-weight:600;margin-top:6px;font-size:13px">کانال‌ها</div></a>
      <a href="/groups" class="fun-card"><div style="font-size:28px">👥</div><div style="font-weight:600;margin-top:6px;font-size:13px">گروه‌ها</div></a>
      <a href="/terms" class="fun-card"><div style="font-size:28px">📜</div><div style="font-weight:600;margin-top:6px;font-size:13px">قوانین</div></a>
      <a href="/explore" class="fun-card"><div style="font-size:28px">🔥</div><div style="font-weight:600;margin-top:6px;font-size:13px">ترندها</div></a>
    </div>
    <div class="card" style="padding:16px"><h3 style="font-size:14px;margin-bottom:6px">نکته</h3>
    <p style="font-size:12px;color:var(--muted)">ربات رسمی @AvaBot و بات‌پدر @BotFather تیک آبی دارند. ربات خودت را از بخش ربات‌ساز بساز.</p></div>'''
    return layout("سرگرمی", body, me, theme=theme)

def page_bots(me, theme):
    c = db()
    my_bots = c.execute("SELECT * FROM bots WHERE owner_id=? ORDER BY id DESC", (me["id"],)).fetchall()
    c.close()
    rows = "".join(f'''<div class="admin-card">
      <div style="font-weight:600;font-size:14px">{esc(b["name"])} <span class="badge-bot">بات</span></div>
      <div style="font-size:12px;color:var(--muted)">@{esc(b["username"])}</div>
      <div class="token-box">{esc(b["token"])}</div>
      <a href="/u/{esc(b["username"])}" class="btn btn-outline" style="font-size:12px;margin-top:6px">مشاهده پروفایل ربات</a>
    </div>''' for b in my_bots)
    body = f'''<h2 style="font-size:16px;margin-bottom:6px;font-weight:600">ربات‌ها</h2>
    <p style="font-size:12px;color:var(--muted);margin-bottom:12px">با بات‌پدر ربات بساز، توکن بگیر و اجرا کن.</p>
    <div class="card" style="padding:16px;margin-bottom:12px">
      <h3 style="font-size:14px;margin-bottom:10px">ساخت ربات</h3>
      <form method="POST" action="/bot/create">
        <input type="text" name="name" placeholder="نام ربات" required>
        <input type="text" name="username" placeholder="آیدی انگلیسی (حداقل ۵ — خودش bot می‌گیرد)" required minlength="5">
        <button type="submit" class="btn btn-primary" style="width:100%">ساخت + توکن</button>
      </form>
    </div>
    <a href="/docs" class="btn btn-outline" style="width:100%;margin-bottom:12px">📚 مستندات کامل</a>
    <h3 style="font-size:13px;margin-bottom:8px;color:var(--muted)">ربات‌های من</h3>
    {rows or '<div class="empty">رباتی نساخته‌اید</div>'}'''
    return layout("ربات‌ها", body, me, theme=theme)

def page_docs(me, theme):
    body = f'''<h2 style="font-size:16px;margin-bottom:12px;font-weight:600">مستندات بات‌پدر و API آوا</h2>
    <div class="card" style="padding:16px;font-size:13px;line-height:1.75">
      <h3 style="font-size:14px;margin-bottom:8px">۱. ربات‌های رسمی</h3>
      <p><strong>@AvaBot</strong> — خوشامدگویی، پیام همگانی از پنل ادمین، تیک آبی</p>
      <p><strong>@BotFather</strong> — صدور توکن و ساخت ربات، تیک آبی</p>
      <hr style="border:none;border-top:1px solid var(--border);margin:14px 0">
      <h3 style="font-size:14px;margin-bottom:8px">۲. ساخت ربات</h3>
      <ol style="padding-right:18px;color:var(--muted)">
        <li>به <a href="/bots" style="color:var(--accent)">ربات‌ها</a> بروید</li>
        <li>نام و آیدی انگلیسی (حداقل ۵ حرف) وارد کنید</li>
        <li>توکن <code style="background:var(--input-bg);padding:2px 6px;border-radius:4px">ava:xxxxxxxx</code> دریافت کنید</li>
        <li>از پروفایل ربات می‌توانید آن را مثل کاربر دنبال کنید</li>
      </ol>
      <hr style="border:none;border-top:1px solid var(--border);margin:14px 0">
      <h3 style="font-size:14px;margin-bottom:8px">۳. اجرای ربات</h3>
      <p style="color:var(--muted)">در نسخه فعلی ربات یک حساب کاربری با پرچم بات است. توکن برای احراز هویت آینده و وب‌هوک رزرو شده. پیام همگانی فقط از پنل ادمین از طریق @AvaBot ارسال می‌شود.</p>
      <hr style="border:none;border-top:1px solid var(--border);margin:14px 0">
      <h3 style="font-size:14px;margin-bottom:8px">۴. محدودیت‌ها</h3>
      <ul style="padding-right:18px;color:var(--muted)">
        <li>اسپم و سوءاستفاده از توکن = مسدودسازی</li>
        <li>حداکثر ۳ حساب کاربری عادی به ازای هر دستگاه</li>
        <li>نام کاربری حداقل ۵ حرف انگلیسی</li>
      </ul>
      <hr style="border:none;border-top:1px solid var(--border);margin:14px 0">
      <h3 style="font-size:14px;margin-bottom:8px">۵. نمونه توکن</h3>
      <div class="token-box">ava:1a2b3c4d5e6f7890...</div>
      <p style="font-size:12px;color:var(--muted)">توکن را محرمانه نگه دارید.</p>
    </div>
    <a href="/bots" class="btn btn-primary" style="width:100%;margin-top:8px">ساخت ربات</a>'''
    return layout("مستندات", body, me, theme=theme)

def page_search(me, q, theme):
    q = (q or "").strip()
    results = ""
    if q:
        c = db()
        users = c.execute("SELECT * FROM users WHERE (username LIKE ? OR display_name LIKE ? OR public_id LIKE ?) AND is_blocked=0 LIMIT 20",
                          (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
        # فقط کانال/گروه عمومی در جستجو
        channels = c.execute("SELECT * FROM conversations WHERE (title LIKE ? OR username LIKE ?) AND is_channel=1 AND is_private=0 LIMIT 10",
                             (f"%{q}%", f"%{q}%")).fetchall()
        groups = c.execute("SELECT * FROM conversations WHERE (title LIKE ? OR username LIKE ?) AND is_group=1 AND is_private=0 LIMIT 10",
                           (f"%{q}%", f"%{q}%")).fetchall()
        c.close()
        if users:
            results += '<div style="font-size:12px;color:var(--muted);margin:8px 0 6px;font-weight:600">کاربران</div>'
            for u in users:
                results += f'''<a href="/u/{esc(u["username"])}" class="list-item">{avatar_html(u, 40)}
                  <div><div style="font-weight:600;font-size:13px">{esc(u["display_name"])}{verified_badge(u)}{bot_badge(u)}</div>
                  <div style="font-size:11px;color:var(--muted)">@{esc(u["username"])}</div></div></a>'''
        if channels:
            results += '<div style="font-size:12px;color:var(--muted);margin:12px 0 6px;font-weight:600">کانال‌های عمومی</div>'
            for ch in channels:
                results += f'''<a href="/ch/{esc(ch["username"])}" class="list-item">
                  <div style="width:40px;height:40px;border-radius:10px;background:var(--accent);display:flex;align-items:center;justify-content:center;color:#fff">📢</div>
                  <div><div style="font-weight:600;font-size:13px">{esc(ch["title"])}</div>
                  <div style="font-size:11px;color:var(--muted)">@{esc(ch["username"])}</div></div></a>'''
        if groups:
            results += '<div style="font-size:12px;color:var(--muted);margin:12px 0 6px;font-weight:600">گروه‌های عمومی</div>'
            for gr in groups:
                results += f'''<a href="/g/{esc(gr["username"])}" class="list-item">
                  <div style="width:40px;height:40px;border-radius:10px;background:var(--warm);display:flex;align-items:center;justify-content:center;color:#fff">👥</div>
                  <div><div style="font-weight:600;font-size:13px">{esc(gr["title"])}</div>
                  <div style="font-size:11px;color:var(--muted)">@{esc(gr["username"])}</div></div></a>'''
        if not results: results = '<div class="empty">نتیجه‌ای نبود</div>'
    body = f'''<form method="GET" action="/search"><input type="text" name="q" value="{esc(q)}" placeholder="جستجو..." autofocus></form>
    <div class="card" style="padding:0">{results if q else '<div class="empty">جستجو کنید (کانال/گروه خصوصی نمایش داده نمی‌شود)</div>'}</div>'''
    return layout("جستجو", body, me, theme=theme)

def page_notifications(me, theme):
    c = db()
    notifs = c.execute("""SELECT n.*, u.username, u.display_name, u.avatar FROM notifications n JOIN users u ON n.actor=u.id
        WHERE n.uid=? ORDER BY n.id DESC LIMIT 50""", (me["id"],)).fetchall()
    c.execute("UPDATE notifications SET is_read=1 WHERE uid=?", (me["id"],)); c.commit(); c.close()
    items = "".join(f'''<div class="list-item"><a href="/u/{esc(n["username"])}">{avatar_html(n, 36)}</a>
      <div style="flex:1"><a href="/u/{esc(n["username"])}" style="font-weight:600;font-size:13px">{esc(n["display_name"])}</a>
      <span style="font-size:13px;color:var(--muted)"> {esc(n["body"])}</span>
      <div style="font-size:10px;color:var(--muted)">{time_ago(n["created"])}</div></div></div>''' for n in notifs)
    body = f'<div class="card" style="padding:0">{items or "<div class=empty>اعلانی نیست</div>"}</div>'
    return layout("اعلان‌ها", body, me, theme=theme)

def page_chat_list(me, theme):
    ensure_saved_messages(me["id"])
    c = db()
    convs = c.execute("""SELECT c.*,
        (SELECT body FROM messages WHERE cid=c.id ORDER BY id DESC LIMIT 1) as last_msg,
        (SELECT created FROM messages WHERE cid=c.id ORDER BY id DESC LIMIT 1) as last_time
        FROM conversations c JOIN conv_members m ON c.id=m.cid WHERE m.uid=?
        ORDER BY CASE WHEN c.username LIKE 'saved_%' THEN 0 ELSE 1 END, last_time DESC NULLS LAST LIMIT 40
    """, (me["id"],)).fetchall()
    c.close()
    items = ""
    for conv in convs:
        icon = "💾" if conv["username"].startswith("saved_") else ("📢" if conv["is_channel"] else ("👥" if conv["is_group"] else "💬"))
        title = "پیام‌های ذخیره شده" if conv["username"].startswith("saved_") else (conv["title"] or conv["username"])
        priv = ' <span class="priv-tag">خصوصی</span>' if g(conv, "is_private") else ""
        prefix = "ch" if conv["is_channel"] else ("g" if conv["is_group"] else "c")
        items += f'''<a href="/{prefix}/{esc(conv["username"])}" class="list-item">
          <div style="width:44px;height:44px;border-radius:50%;background:var(--accent);display:flex;align-items:center;justify-content:center;font-size:18px;color:#fff">{icon}</div>
          <div style="flex:1;min-width:0"><div style="font-weight:600;font-size:13px">{esc(title)}{priv}</div>
          <div style="font-size:12px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{esc(g(conv,"last_msg") or "...")}</div></div></a>'''
    body = f'''<div class="card" style="padding:12px;margin-bottom:10px">
      <form method="POST" action="/chat/start" style="display:flex;gap:8px">
        <input type="text" name="username" placeholder="شروع گفتگو با نام کاربری" style="margin:0;flex:1">
        <button type="submit" class="btn btn-primary">شروع</button>
      </form></div>
    <div style="display:flex;gap:8px;margin-bottom:10px">
      <a href="/channels" class="btn btn-outline" style="flex:1;font-size:12px">کانال‌ها</a>
      <a href="/groups" class="btn btn-outline" style="flex:1;font-size:12px">گروه‌ها</a>
    </div>
    <div class="card" style="padding:12px;margin-bottom:10px">
      <div style="font-size:12px;font-weight:600;margin-bottom:8px">ساخت کانال / گروه <span style="font-weight:400;color:var(--muted)">(آیدی ≥ ۷ حرف)</span></div>
      <details style="margin-bottom:8px"><summary class="btn btn-outline" style="width:100%;cursor:pointer;font-size:12px">+ کانال</summary>
        <form method="POST" action="/create/channel" style="margin-top:8px">
          <input type="text" name="title" placeholder="نام کانال" required>
          <input type="text" name="username" placeholder="آیدی انگلیسی (حداقل ۷)" required minlength="7">
          <textarea name="description" placeholder="توضیحات" rows="2"></textarea>
          <label class="terms-check"><input type="checkbox" name="is_private" value="1"><span>خصوصی (لینک دعوت — در جستجو نمی‌آید)</span></label>
          <button type="submit" class="btn btn-primary" style="width:100%">ایجاد کانال</button>
        </form></details>
      <details><summary class="btn btn-outline" style="width:100%;cursor:pointer;font-size:12px">+ گروه</summary>
        <form method="POST" action="/create/group" style="margin-top:8px">
          <input type="text" name="title" placeholder="نام گروه" required>
          <input type="text" name="username" placeholder="آیدی انگلیسی (حداقل ۷)" required minlength="7">
          <label class="terms-check"><input type="checkbox" name="is_private" value="1"><span>خصوصی (لینک دعوت)</span></label>
          <button type="submit" class="btn btn-primary" style="width:100%">ایجاد گروه</button>
        </form></details>
    </div>
    <div class="card" style="padding:0">{items or "<div class=empty>گفتگویی ندارید</div>"}</div>'''
    return layout("پیام‌ها", body, me, "chat", theme)

def page_conversation(me, conv, theme):
    c = db()
    member = c.execute("SELECT * FROM conv_members WHERE cid=? AND uid=?", (conv["id"], me["id"])).fetchone()
    if not member and not conv["is_channel"] and not g(conv, "is_private"):
        c.close(); return layout("خطا", "<div class='empty'>عضو نیستید</div>", me, theme=theme)
    msgs = c.execute("""SELECT m.*, u.username, u.display_name, u.avatar FROM messages m JOIN users u ON m.sender=u.id
        WHERE m.cid=? ORDER BY m.id ASC LIMIT 100""", (conv["id"],)).fetchall()
    members_count = c.execute("SELECT COUNT(*) as c FROM conv_members WHERE cid=?", (conv["id"],)).fetchone()["c"]
    c.close()
    html_m = ""
    for m in msgs:
        cls = "msg-me" if m["sender"] == me["id"] else "msg-other"
        img = f'<img src="/uploads/{esc(m["image"])}" style="max-width:100%;border-radius:8px;margin-bottom:4px">' if g(m, "image") else ""
        html_m += f'''<div class="msg-bubble {cls}">{img}{format_text(m["body"])}
          <div class="msg-meta">{esc(m["display_name"])} · {time_ago(m["created"])}</div></div>'''
    can_send = True
    if conv["is_channel"] and (not member or member["role"] not in ("owner", "admin")):
        can_send = False
    form_html = ""
    if can_send:
        prefix = "ch" if conv["is_channel"] else ("g" if conv["is_group"] else "c")
        form_html = f'''<form method="POST" action="/{prefix}/{esc(conv["username"])}/send" enctype="multipart/form-data" style="margin-top:8px">
          <div style="display:flex;gap:6px;align-items:center">
            <input type="text" name="body" placeholder="پیام..." style="margin:0;flex:1">
            <label class="btn btn-outline" style="padding:8px;margin:0;cursor:pointer">📎<input type="file" name="image" accept="image/*" style="display:none"></label>
            <button type="submit" class="btn btn-primary">ارسال</button>
          </div></form>'''
    elif conv["is_channel"] and not member and not g(conv, "is_private"):
        form_html = f'''<form method="POST" action="/join/{esc(conv["username"])}" style="margin-top:8px">
          <button type="submit" class="btn btn-primary" style="width:100%">عضویت</button></form>'''
    title = "پیام‌های ذخیره شده" if conv["username"].startswith("saved_") else (conv["title"] or conv["username"])
    edit_link = priv_info = ""
    if conv["owner_id"] == me["id"] and (conv["is_channel"] or conv["is_group"]):
        prefix = "ch" if conv["is_channel"] else "g"
        edit_link = f'<a href="/{prefix}/{esc(conv["username"])}/edit" style="font-size:12px;color:var(--accent)">ویرایش</a>'
        if g(conv, "is_private") and g(conv, "invite_code"):
            link = f"/invite?c={conv['invite_code']}"
            priv_info = f'''<div style="margin-top:8px;padding:8px;background:var(--input-bg);border-radius:8px;font-size:12px">
              لینک دعوت خصوصی: <code style="direction:ltr">{esc(link)}</code>
              <div style="color:var(--muted);margin-top:4px">این لینک را فقط به افراد مورد اعتماد بدهید</div></div>'''
    body = f'''<div class="card" style="padding:12px;margin-bottom:8px">
      <div style="display:flex;align-items:center;gap:10px">
        <a href="/chat" style="color:var(--accent)">←</a>
        <div style="flex:1"><strong style="font-size:14px">{esc(title)}</strong>
          <div style="font-size:11px;color:var(--muted)">{members_count} عضو · @{esc(conv["username"])}
          {" · خصوصی" if g(conv,"is_private") else " · عمومی"}</div></div>
        {edit_link}
      </div>
      {priv_info}
    </div>
    <div class="card" style="padding:12px;min-height:280px;display:flex;flex-direction:column">
      <div style="flex:1;overflow-y:auto">{html_m or '<div class="empty">پیامی نیست</div>'}</div>
      {form_html}
    </div>'''
    return layout(title, body, me, "chat", theme)

def page_invite(me, code, theme):
    c = db()
    conv = c.execute("SELECT * FROM conversations WHERE invite_code=?", (code,)).fetchone()
    c.close()
    if not conv:
        return layout("لینک نامعتبر", "<div class='empty'>لینک دعوت معتبر نیست</div>", me, theme=theme)
    body = f'''<div class="card" style="padding:20px;text-align:center">
      <div style="font-size:40px;margin-bottom:8px">{"📢" if conv["is_channel"] else "👥"}</div>
      <h2 style="font-size:16px">{esc(conv["title"])}</h2>
      <p style="font-size:12px;color:var(--muted);margin:8px 0">دعوت به {"کانال" if conv["is_channel"] else "گروه"} خصوصی</p>
      <form method="POST" action="/invite/join">
        <input type="hidden" name="code" value="{esc(code)}">
        <button type="submit" class="btn btn-primary" style="width:100%">پیوستن</button>
      </form>
    </div>'''
    return layout("دعوت", body, me, theme=theme)

def page_conv_edit(me, conv, theme):
    if conv["owner_id"] != me["id"]:
        return layout("خطا", "<div class='empty'>فقط مالک</div>", me, theme=theme)
    prefix = "ch" if conv["is_channel"] else "g"
    body = f'''<h2 style="font-size:16px;margin-bottom:12px">ویرایش</h2>
    <div class="card" style="padding:16px">
      <form method="POST" action="/{prefix}/{esc(conv["username"])}/edit" enctype="multipart/form-data">
        <input type="file" name="avatar" accept="image/*">
        <input type="text" name="title" value="{esc(conv["title"])}" required>
        <textarea name="description" rows="3">{esc(g(conv,"description") or "")}</textarea>
        <label class="terms-check"><input type="checkbox" name="is_private" value="1" {"checked" if g(conv,"is_private") else ""}>
          <span>خصوصی (لینک دعوت — مخفی از جستجو)</span></label>
        <button type="submit" class="btn btn-primary" style="width:100%">ذخیره</button>
      </form>
    </div>
    <a href="/{prefix}/{esc(conv["username"])}" class="btn btn-outline" style="width:100%;margin-top:8px">بازگشت</a>'''
    return layout("ویرایش", body, me, theme=theme)

def page_saved(me, theme):
    c = db()
    posts = c.execute("""SELECT p.*, u.username, u.display_name, u.avatar, u.is_verified, u.is_admin, u.is_bot
        FROM saves s JOIN posts p ON s.pid=p.id JOIN users u ON p.uid=u.id WHERE s.uid=? ORDER BY s.rowid DESC LIMIT 40""", (me["id"],)).fetchall()
    c.close()
    body = f'''<div class="card" style="padding:16px;text-align:center;margin-bottom:10px"><div style="font-size:32px">🔖</div>
      <h2 style="font-size:15px;margin-top:4px">ذخیره‌شده‌ها</h2></div>
    {"".join(render_post_card(p, me, theme) for p in posts) or '<div class="empty">خالی</div>'}'''
    return layout("ذخیره‌شده‌ها", body, me, theme=theme)

def page_follow_list(me, uname, kind, theme):
    c = db()
    target = c.execute("SELECT * FROM users WHERE username=?", (uname,)).fetchone()
    if not target:
        c.close(); return layout("یافت نشد", "<div class='empty'>یافت نشد</div>", me, theme=theme)
    if kind == "followers":
        users = c.execute("SELECT u.* FROM follows f JOIN users u ON f.a=u.id WHERE f.b=? AND u.is_blocked=0 LIMIT 100", (target["id"],)).fetchall()
        title = f"فالوورهای {g(target,'display_name')}"
    else:
        users = c.execute("SELECT u.* FROM follows f JOIN users u ON f.b=u.id WHERE f.a=? AND u.is_blocked=0 LIMIT 100", (target["id"],)).fetchall()
        title = f"فالوینگ‌های {g(target,'display_name')}"
    c.close()
    items = ""
    for u in users:
        is_me = u["id"] == me["id"]
        c2 = db()
        is_f = None if is_me else c2.execute("SELECT 1 FROM follows WHERE a=? AND b=?", (me["id"], u["id"])).fetchone()
        c2.close()
        btn = ""
        if not is_me:
            label, cls = ("آنفالو", "btn-outline") if is_f else ("فالو", "btn-primary")
            btn = f'''<form method="POST" action="/u/{esc(u["username"])}/follow" style="margin:0">
              <button type="submit" class="btn {cls}" style="padding:6px 12px;font-size:12px">{label}</button></form>'''
        items += f'''<div class="list-item">
          <a href="/u/{esc(u["username"])}">{avatar_html(u, 40)}</a>
          <a href="/u/{esc(u["username"])}" style="flex:1">
            <div style="font-weight:600;font-size:13px">{esc(u["display_name"])}{verified_badge(u)}{bot_badge(u)}</div>
            <div style="font-size:11px;color:var(--muted)">@{esc(u["username"])}</div></a>{btn}</div>'''
    body = f'''<div class="card" style="padding:12px;margin-bottom:8px;display:flex;align-items:center;gap:10px">
      <a href="/u/{esc(uname)}" style="color:var(--accent)">←</a><strong style="font-size:14px">{esc(title)}</strong></div>
    <div class="card" style="padding:0">{items or '<div class="empty">خالی</div>'}</div>'''
    return layout(title, body, me, theme=theme)

def page_profile(me, target, theme):
    c = db()
    posts = c.execute("SELECT * FROM posts WHERE uid=? ORDER BY id DESC LIMIT 30", (target["id"],)).fetchall()
    followers = c.execute("SELECT COUNT(*) as c FROM follows WHERE b=?", (target["id"],)).fetchone()["c"]
    following = c.execute("SELECT COUNT(*) as c FROM follows WHERE a=?", (target["id"],)).fetchone()["c"]
    is_following = c.execute("SELECT 1 FROM follows WHERE a=? AND b=?", (me["id"], target["id"])).fetchone()
    c.close()
    if me["id"] != target["id"]:
        label, cls = ("آنفالو", "btn-outline") if is_following else ("فالو", "btn-primary")
        actions = f'''<form method="POST" action="/u/{esc(target["username"])}/follow" style="display:inline">
          <button type="submit" class="btn {cls}">{label}</button></form>
        <form method="POST" action="/chat/start" style="display:inline">
          <input type="hidden" name="username" value="{esc(target["username"])}">
          <button type="submit" class="btn btn-outline">پیام</button></form>'''
    else:
        actions = f'<a href="/settings" class="btn btn-outline">ویرایش</a> <a href="/saved" class="btn btn-outline">ذخیره‌ها</a>'
    grid = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:2px;margin-top:8px">'
    for p in posts:
        if g(p, "image"):
            grid += f'<a href="/p/{p["id"]}"><img src="/uploads/{esc(p["image"])}" style="width:100%;aspect-ratio:1;object-fit:cover" loading="lazy"></a>'
        else:
            grid += f'<a href="/p/{p["id"]}" style="background:var(--card);aspect-ratio:1;display:flex;align-items:center;padding:6px;font-size:10px;color:var(--muted)">{esc((g(p,"content") or "")[:40])}</a>'
    grid += '</div>' if posts else '<div class="empty">پستی ندارد</div>'
    banner = ""
    if g(target, "is_bot"):
        banner = '<div style="background:linear-gradient(90deg,rgba(0,168,132,.1),transparent);padding:8px 12px;font-size:12px;color:#00a884">🤖 حساب ربات</div>'
    elif g(target, "is_admin"):
        banner = '<div style="background:linear-gradient(90deg,rgba(245,158,11,.1),transparent);padding:8px 12px;font-size:12px;color:var(--warning)">👑 مدیر آوا</div>'
    body = f'''<div class="card" style="overflow:hidden">{banner}
      <div style="padding:20px;text-align:center">
        <div style="display:flex;justify-content:center;margin-bottom:12px">{avatar_html(target, 88)}</div>
        <h1 style="font-size:18px;font-weight:700">{esc(target["display_name"])}{verified_badge(target)}{admin_badge(target)}{bot_badge(target)}</h1>
        <div style="color:var(--muted);font-size:13px;margin:2px 0 6px">@{esc(target["username"])}</div>
        <div style="font-size:11px;color:var(--muted);margin-bottom:8px">آیدی · {esc(target["public_id"])}</div>
        <p style="font-size:13px;color:var(--muted);max-width:280px;margin:0 auto 12px">{esc(g(target,"bio") or "")}</p>
        <div style="display:flex;justify-content:center;gap:28px;margin-bottom:14px;font-size:13px">
          <div><strong style="display:block;font-size:16px">{len(posts)}</strong><span style="color:var(--muted);font-size:11px">پست</span></div>
          <a href="/u/{esc(target["username"])}/followers"><strong style="display:block;font-size:16px">{followers}</strong><span style="color:var(--muted);font-size:11px">فالوور</span></a>
          <a href="/u/{esc(target["username"])}/following"><strong style="display:block;font-size:16px">{following}</strong><span style="color:var(--muted);font-size:11px">فالوینگ</span></a>
        </div>
        <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap">{actions}</div>
      </div></div>{grid}'''
    return layout(g(target, "display_name"), body, me, "profile" if me["id"] == target["id"] else "", theme)

def page_single_post(me, pid, theme):
    c = db()
    p = c.execute("""SELECT p.*, u.username, u.display_name, u.avatar, u.is_verified, u.is_admin, u.is_bot
        FROM posts p JOIN users u ON p.uid=u.id WHERE p.id=?""", (pid,)).fetchone()
    if not p:
        c.close(); return layout("یافت نشد", "<div class='empty'>پیدا نشد</div>", me, theme=theme)
    comments = c.execute("""SELECT cm.*, u.username, u.display_name, u.avatar, u.is_verified
        FROM comments cm JOIN users u ON cm.uid=u.id WHERE cm.pid=? ORDER BY cm.id DESC LIMIT 40""", (pid,)).fetchall()
    c.close()
    cm_html = "".join(f'''<div style="display:flex;gap:8px;padding:8px 0;border-bottom:1px solid var(--border)">
      <a href="/u/{esc(cm["username"])}">{avatar_html(cm, 32)}</a>
      <div><a href="/u/{esc(cm["username"])}" style="font-weight:600;font-size:12px">{esc(cm["display_name"])}{verified_badge(cm)}</a>
      <div style="font-size:13px">{format_text(cm["body"])}</div>
      <div style="font-size:10px;color:var(--muted)">{time_ago(cm["created"])}</div></div></div>''' for cm in comments)
    body = f'''{render_post_card(p, me, theme)}
    <div class="card" style="padding:12px">
      <h3 style="font-size:13px;margin-bottom:8px;font-weight:600">نظرات</h3>
      <form method="POST" action="/p/{pid}/comment" style="margin-bottom:10px">
        <textarea name="body" placeholder="نظر..." rows="2" required></textarea>
        <button type="submit" class="btn btn-primary">ارسال</button>
      </form>
      {cm_html or '<div class="empty">اولین نظر را بنویسید</div>'}
    </div>'''
    return layout("پست", body, me, theme=theme)

def page_create(me, tab, theme):
    tab = tab if tab in ("post", "story") else "post"
    body = f'''<h2 style="font-size:16px;margin-bottom:10px;font-weight:600">ایجاد</h2>
    <div class="create-tabs">
      <a href="/create?tab=post" class="{'active' if tab=='post' else ''}">پست</a>
      <a href="/create?tab=story" class="{'active' if tab=='story' else ''}">استوری</a>
    </div>'''
    if tab == "post":
        body += '''<div class="card" style="padding:16px">
          <form method="POST" action="/post/create" enctype="multipart/form-data">
            <textarea name="content" placeholder="چه خبر؟" rows="4"></textarea>
            <input type="file" name="image" accept="image/*">
            <button type="submit" class="btn btn-primary" style="width:100%">انتشار</button>
          </form></div>
        <p style="font-size:11px;color:var(--muted);text-align:center;margin-top:8px">کانال و گروه از بخش پیام‌ها</p>'''
    else:
        body += '''<div class="card" style="padding:16px">
          <form method="POST" action="/story/create" enctype="multipart/form-data">
            <input type="file" name="image" accept="image/*" required>
            <input type="text" name="caption" placeholder="کپشن">
            <button type="submit" class="btn btn-primary" style="width:100%">استوری (۲۴ ساعت)</button>
          </form></div>'''
    return layout("ایجاد", body, me, "create", theme)

def page_view_story(me, sid, theme):
    c = db()
    s = c.execute("""SELECT s.*, u.username, u.display_name, u.avatar, u.is_verified
        FROM stories s JOIN users u ON s.uid=u.id WHERE s.id=? AND s.expires>?""", (sid, now())).fetchone()
    if s:
        c.execute("INSERT OR IGNORE INTO story_views(sid,uid) VALUES(?,?)", (sid, me["id"])); c.commit()
    c.close()
    if not s:
        return layout("استوری", "<div class='empty'>منقضی شده</div>", me, theme=theme)
    body = f'''<div class="card" style="overflow:hidden">
      <div class="post-header"><a href="/u/{esc(s["username"])}">{avatar_html(s, 36)}</a>
        <div><a href="/u/{esc(s["username"])}" class="name">{esc(s["display_name"])}{verified_badge(s)}</a>
        <div style="font-size:11px;color:var(--muted)">{time_ago(s["created"])}</div></div></div>
      <img src="/uploads/{esc(s["image"])}" style="width:100%;max-height:70vh;object-fit:contain;background:#000">
      <div class="post-content">{format_text(g(s,"caption"))}</div></div>
    <a href="/home" class="btn btn-outline" style="width:100%;margin-top:8px">بازگشت</a>'''
    return layout("استوری", body, me, theme=theme)

def page_channels(me, theme):
    c = db()
    channels = c.execute("SELECT * FROM conversations WHERE is_channel=1 AND is_private=0 ORDER BY id DESC LIMIT 40").fetchall()
    c.close()
    items = "".join(f'''<a href="/ch/{esc(ch["username"])}" class="list-item">
      <div style="width:44px;height:44px;border-radius:12px;background:var(--accent);display:flex;align-items:center;justify-content:center;color:#fff">📢</div>
      <div><div style="font-weight:600;font-size:13px">{esc(ch["title"])}</div>
      <div style="font-size:11px;color:var(--muted)">@{esc(ch["username"])}</div></div></a>''' for ch in channels)
    body = f'''<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
      <h2 style="font-size:16px;font-weight:600">کانال‌های عمومی</h2>
      <a href="/chat" class="btn btn-primary" style="padding:6px 12px;font-size:12px">ساخت</a></div>
    <div class="card" style="padding:0">{items or '<div class="empty">کانالی نیست</div>'}</div>'''
    return layout("کانال‌ها", body, me, theme=theme)

def page_groups(me, theme):
    c = db()
    groups = c.execute("SELECT * FROM conversations WHERE is_group=1 AND is_private=0 ORDER BY id DESC LIMIT 40").fetchall()
    c.close()
    items = "".join(f'''<a href="/g/{esc(gr["username"])}" class="list-item">
      <div style="width:44px;height:44px;border-radius:12px;background:var(--warm);display:flex;align-items:center;justify-content:center;color:#fff">👥</div>
      <div><div style="font-weight:600;font-size:13px">{esc(gr["title"])}</div>
      <div style="font-size:11px;color:var(--muted)">@{esc(gr["username"])}</div></div></a>''' for gr in groups)
    body = f'''<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
      <h2 style="font-size:16px;font-weight:600">گروه‌های عمومی</h2>
      <a href="/chat" class="btn btn-primary" style="padding:6px 12px;font-size:12px">ساخت</a></div>
    <div class="card" style="padding:0">{items or '<div class="empty">گروهی نیست</div>'}</div>'''
    return layout("گروه‌ها", body, me, theme=theme)

def page_settings(me, theme):
    body = f'''<div class="card" style="padding:20px">
      <h2 style="font-size:16px;margin-bottom:14px;font-weight:600">ویرایش پروفایل</h2>
      <form method="POST" action="/settings" enctype="multipart/form-data">
        <div style="text-align:center;margin-bottom:14px">{avatar_html(me, 80)}</div>
        <label style="font-size:12px;color:var(--muted)">عکس پروفایل</label>
        <input type="file" name="avatar" accept="image/jpeg,image/png,image/gif,image/webp">
        <label style="font-size:12px;color:var(--muted)">نام نمایشی</label>
        <input type="text" name="display_name" value="{esc(g(me,'display_name'))}" required>
        <label style="font-size:12px;color:var(--muted)">نام کاربری (حداقل ۵ حرف انگلیسی)</label>
        <input type="text" name="username" value="{esc(g(me,'username'))}" required minlength="5" pattern="[a-zA-Z0-9_]{{5,24}}">
        <label style="font-size:12px;color:var(--muted)">بیوگرافی</label>
        <textarea name="bio" rows="3">{esc(g(me,'bio') or '')}</textarea>
        <div style="font-size:12px;color:var(--muted);margin-bottom:12px;padding:8px;background:var(--input-bg);border-radius:8px">
          آیدی عددی: <strong>{esc(g(me,'public_id'))}</strong>
        </div>
        <button type="submit" class="btn btn-primary" style="width:100%">ذخیره</button>
      </form>
      <div style="margin-top:16px;padding-top:12px;border-top:1px solid var(--border)">
        <a href="/theme" class="btn btn-outline" style="width:100%;margin-bottom:8px">تم ({'روز' if theme=='dark' else 'شب'})</a>
        <a href="/terms" class="btn btn-outline" style="width:100%;margin-bottom:8px">قوانین</a>
        <a href="/logout" class="btn btn-outline" style="width:100%;color:var(--danger)">خروج</a>
      </div>
      <div class="footer-dev">{DEVELOPER}</div>
    </div>'''
    return layout("تنظیمات", body, me, theme=theme)

def page_admin(me, tab, theme):
    tabs = [("dashboard","داشبورد"),("users","کاربران"),("posts","پست‌ها"),("ads","تبلیغات"),
            ("broadcast","همگانی"),("bots","ربات‌ها"),("settings","تنظیمات")]
    tabs_html = "".join(f'<a href="/admin?tab={t[0]}" class="{"active" if tab==t[0] else ""}">{t[1]}</a>' for t in tabs)
    c = db()
    content = ""
    if tab == "dashboard":
        stats = {k: c.execute(q).fetchone()["c"] for k, q in [
            ("users", "SELECT COUNT(*) as c FROM users WHERE is_bot=0"),
            ("posts", "SELECT COUNT(*) as c FROM posts"),
            ("likes", "SELECT COUNT(*) as c FROM likes"),
            ("channels", "SELECT COUNT(*) as c FROM conversations WHERE is_channel=1"),
            ("groups", "SELECT COUNT(*) as c FROM conversations WHERE is_group=1"),
            ("verified", "SELECT COUNT(*) as c FROM users WHERE is_verified=1"),
            ("blocked", "SELECT COUNT(*) as c FROM users WHERE is_blocked=1"),
            ("ads", "SELECT COUNT(*) as c FROM ads WHERE is_active=1"),
            ("bots", "SELECT COUNT(*) as c FROM bots"),
        ]}
        content = f'''<div class="stats-grid">
          {"".join(f'<div class="stat-box"><div class="num">{v}</div><div class="lbl">{k}</div></div>' for k,v in [
            ("کاربر",stats["users"]),("پست",stats["posts"]),("لایک",stats["likes"]),
            ("کانال",stats["channels"]),("گروه",stats["groups"]),("تأیید",stats["verified"]),
            ("بلاک",stats["blocked"]),("تبلیغ",stats["ads"]),("ربات",stats["bots"])])}
        </div>
        <div class="card" style="padding:14px"><div style="display:flex;flex-wrap:wrap;gap:6px">
          <a href="/admin?tab=broadcast" class="btn btn-primary" style="font-size:12px">همگانی</a>
          <a href="/admin?tab=ads" class="btn btn-outline" style="font-size:12px">تبلیغات</a>
          <a href="/admin?tab=users" class="btn btn-outline" style="font-size:12px">کاربران</a>
        </div></div>
        <div class="footer-dev">{DEVELOPER}</div>'''
    elif tab == "users":
        users = c.execute("SELECT * FROM users ORDER BY id DESC LIMIT 80").fetchall()
        rows = ""
        for u in users:
            st = []
            if g(u,"is_admin"): st.append('<span style="font-size:10px;color:var(--warning)">ادمین</span>')
            if g(u,"is_verified"): st.append('<span style="font-size:10px;color:#1d9bf0">تأیید</span>')
            if g(u,"is_blocked"): st.append('<span style="font-size:10px;color:var(--danger)">بلاک</span>')
            if g(u,"is_bot"): st.append('<span class="badge-bot">بات</span>')
            rows += f'''<div class="admin-card">
              <div style="display:flex;align-items:center;gap:8px">{avatar_html(u,36)}
                <div style="flex:1"><div style="font-weight:600;font-size:13px">{esc(u["display_name"])} @{esc(u["username"])}</div>
                <div style="font-size:10px;color:var(--muted)">#{u["public_id"]}</div></div>
                <div>{" ".join(st)}</div></div>
              <div class="admin-actions">
                <form method="POST" action="/admin/verify"><input type="hidden" name="public_id" value="{u['public_id']}"><button class="btn btn-primary" type="submit">تیک</button></form>
                <form method="POST" action="/admin/unverify"><input type="hidden" name="public_id" value="{u['public_id']}"><button class="btn btn-outline" type="submit">حذف تیک</button></form>
                <form method="POST" action="/admin/block"><input type="hidden" name="public_id" value="{u['public_id']}"><button class="btn btn-danger" type="submit">بلاک</button></form>
                <form method="POST" action="/admin/unblock"><input type="hidden" name="public_id" value="{u['public_id']}"><button class="btn btn-outline" type="submit">آنبلاک</button></form>
                <form method="POST" action="/admin/make_admin"><input type="hidden" name="public_id" value="{u['public_id']}"><button class="btn btn-warning" type="submit">ادمین</button></form>
                <form method="POST" action="/admin/delete_user" onsubmit="return confirm('حذف؟')"><input type="hidden" name="public_id" value="{u['public_id']}"><button class="btn btn-danger" type="submit">حذف</button></form>
              </div></div>'''
        content = rows
    elif tab == "posts":
        posts = c.execute("SELECT p.*, u.username, u.display_name FROM posts p JOIN users u ON p.uid=u.id ORDER BY p.id DESC LIMIT 40").fetchall()
        rows = "".join(f'''<div class="admin-card">
          <div style="font-size:12px"><strong>{esc(p["display_name"])}</strong> · {time_ago(p["created"])} · 👁 {g(p,"views") or 0}</div>
          <div style="font-size:12px;color:var(--muted);margin:4px 0">{esc((g(p,"content") or "")[:80])}</div>
          <div class="admin-actions">
            <form method="POST" action="/admin/toggle_explore"><input type="hidden" name="post_id" value="{p['id']}"><button class="btn btn-outline" type="submit">اکسپلور</button></form>
            <form method="POST" action="/admin/delete_post" onsubmit="return confirm('حذف؟')"><input type="hidden" name="post_id" value="{p['id']}"><button class="btn btn-danger" type="submit">حذف</button></form>
          </div></div>''' for p in posts)
        content = rows or '<div class="empty">خالی</div>'
    elif tab == "ads":
        ads = c.execute("SELECT * FROM ads ORDER BY id DESC LIMIT 30").fetchall()
        form = '''<div class="card" style="padding:14px;margin-bottom:12px">
          <h3 style="font-size:14px;margin-bottom:8px">تبلیغ جدید</h3>
          <form method="POST" action="/admin/ad_create" enctype="multipart/form-data">
            <input type="text" name="title" placeholder="عنوان" required>
            <textarea name="body" placeholder="متن" rows="2" required></textarea>
            <input type="text" name="link" placeholder="لینک">
            <input type="file" name="image" accept="image/*">
            <button type="submit" class="btn btn-primary">ثبت</button>
          </form></div>'''
        rows = "".join(f'''<div class="admin-card">
          <div style="font-weight:600;font-size:13px">{esc(a["title"])} <span style="font-size:11px;color:var(--muted)">{"✅" if g(a,"is_active") else "⏸"}</span></div>
          <div style="font-size:12px;color:var(--muted)">{esc(g(a,"body","")[:60])}</div>
          <div class="admin-actions">
            <form method="POST" action="/admin/ad_toggle"><input type="hidden" name="ad_id" value="{a['id']}"><button class="btn btn-outline" type="submit">وضعیت</button></form>
            <form method="POST" action="/admin/ad_delete" onsubmit="return confirm('حذف؟')"><input type="hidden" name="ad_id" value="{a['id']}"><button class="btn btn-danger" type="submit">حذف</button></form>
          </div></div>''' for a in ads)
        content = form + (rows or '<div class="empty">تبلیغی نیست</div>')
    elif tab == "broadcast":
        history = c.execute("SELECT b.*, u.display_name FROM broadcasts b JOIN users u ON b.sent_by=u.id ORDER BY b.id DESC LIMIT 8").fetchall()
        hist = "".join(f'''<div class="admin-card"><div style="font-size:12px">{esc(g(h,"body","")[:120])}</div>
          <div style="font-size:10px;color:var(--muted)">{esc(h["display_name"])} · {time_ago(h["created"])}</div></div>''' for h in history)
        content = f'''<div class="card" style="padding:14px;margin-bottom:12px">
          <h3 style="font-size:14px;margin-bottom:6px">پیام همگانی</h3>
          <form method="POST" action="/admin/broadcast" enctype="multipart/form-data">
            <textarea name="body" placeholder="متن..." rows="3"></textarea>
            <input type="file" name="image" accept="image/*">
            <button type="submit" class="btn btn-primary" onclick="return confirm('ارسال؟')">ارسال</button>
          </form></div>{hist or '<div class="empty">خالی</div>'}'''
    elif tab == "bots":
        bots = c.execute("SELECT b.*, u.display_name as owner_name FROM bots b JOIN users u ON b.owner_id=u.id ORDER BY b.id DESC LIMIT 30").fetchall()
        content = "".join(f'''<div class="admin-card">
          <div style="font-weight:600;font-size:13px">{esc(b["name"])} @{esc(b["username"])}</div>
          <div style="font-size:11px;color:var(--muted)">مالک: {esc(b["owner_name"])}</div>
          <div class="token-box">{esc(b["token"])}</div></div>''' for b in bots) or '<div class="empty">خالی</div>'
    elif tab == "settings":
        mode = get_setting("explore_mode", "all")
        welcome = get_setting("welcome_enabled", "1")
        content = f'''<div class="card" style="padding:16px">
          <form method="POST" action="/admin/settings">
            <label style="font-size:12px;display:block;margin-bottom:4px">فید</label>
            <select name="explore_mode">
              <option value="all" {"selected" if mode=="all" else ""}>همه</option>
              <option value="following" {"selected" if mode=="following" else ""}>فالوینگ</option>
            </select>
            <label style="font-size:12px;display:block;margin:10px 0 4px">خوشامدگویی</label>
            <select name="welcome_enabled">
              <option value="1" {"selected" if welcome=="1" else ""}>فعال</option>
              <option value="0" {"selected" if welcome=="0" else ""}>غیرفعال</option>
            </select>
            <button type="submit" class="btn btn-primary" style="margin-top:10px">ذخیره</button>
          </form>
          <div style="margin-top:16px;font-size:12px;color:var(--muted)">
            <p>{APP_NAME} · {DEVELOPER}</p>
            <p>ادمین: HAMAVA · @AvaBot · @BotFather</p>
            <p>حداکثر حساب هر دستگاه: {MAX_ACCOUNTS_PER_DEVICE}</p>
          </div></div>'''
    c.close()
    body = f'''<h2 style="font-size:16px;margin-bottom:4px;font-weight:600">پنل مدیریت</h2>
    <div class="admin-tabs">{tabs_html}</div>{content}'''
    return layout("مدیریت", body, me, theme=theme)

if __name__ == "__main__":
    init_db()
    start_background()
    print(f"""
╔══════════════════════════════════════════════════╗
║              {APP_NAME}  ({APP_NAME_EN})                     ║
╠══════════════════════════════════════════════════╣
║  http://localhost:{PORT}                             ║
║  ادمین: HAMAVA  /  13866831                      ║
║  پنل: /admin                                     ║
║  {DEVELOPER}                           ║
╚══════════════════════════════════════════════════╝
""")
    server = HTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nخاموش.")
        server.server_close()
